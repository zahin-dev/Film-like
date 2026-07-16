"""Mock-only tests for the Mistral recommendation facade and API route."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import status
from sqlalchemy import select

from app.config import settings
from app.external import mistral_client
from app.models.tag import Tag
from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.schemas.film import Film


@pytest.fixture()
def auth_headers(client):
    payload = {
        "first_name": "Romy",
        "last_name": "Viewer",
        "email": "romy@example.com",
        "password": "Films123!",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['token']}"}


@pytest.fixture()
def auth_user(db_session, auth_headers):
    return db_session.execute(
        select(User).where(User.email == "romy@example.com")
    ).scalar_one()


def ai_output(*candidates):
    return json.dumps({"candidates": list(candidates)})


def candidate(title, reason="A strong match for your mood.", year=None):
    return {"title": title, "year": year, "reason": reason}


def film(tmdb_id, title, year=2020):
    return Film(
        tmdb_id=tmdb_id,
        title=title,
        year=year,
        poster_url=f"https://image.tmdb.org/t/p/w500/{tmdb_id}.jpg",
        synopsis="Verified by TMDB.",
    )


class TestRecommendationRoute:
    def test_authentication_required(self, client):
        response = client.post(
            "/recommendations", json={"mood": "thoughtful", "limit": 5}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_mood_validation(self, client, auth_headers):
        response = client.post(
            "/recommendations",
            json={"mood": "hungry", "limit": 5},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_history_returns_verified_recommendation(
        self, client, auth_headers
    ):
        raw = ai_output(candidate("Arrival", "Quiet, thoughtful science fiction.", 2016))
        with patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(return_value=raw),
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(return_value=[film(329865, "Arrival", 2016)]),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "thoughtful", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["mood"] == "thoughtful"
        assert body["history_tags_used"] == []
        assert body["recommendations"][0]["film"]["tmdb_id"] == 329865
        assert body["recommendations"][0]["reason"] == (
            "Quiet, thoughtful science fiction."
        )

    def test_history_tag_frequencies_are_in_facade_context(
        self, client, auth_headers, auth_user, db_session
    ):
        masterpiece = Tag(name="Masterpiece", description="Top quality")
        emotional = Tag(name="Emotional Damage", description="Bring tissues")
        db_session.add_all([masterpiece, emotional])
        db_session.flush()
        db_session.add_all([
            ViewingHistoryEntry(
                user_id=auth_user.id,
                tmdb_id=1,
                tags=[masterpiece, emotional],
            ),
            ViewingHistoryEntry(
                user_id=auth_user.id,
                tmdb_id=2,
                tags=[masterpiece],
            ),
        ])
        db_session.commit()

        captured_messages = []

        async def capture_completion(messages, response_schema):
            captured_messages.extend(messages)
            assert response_schema["additionalProperties"] is False
            return ai_output(candidate("Past Lives", year=2023))

        with patch(
            "app.external.tmdb_client.get_movie_basic",
            new=AsyncMock(side_effect=[{"title": "One"}, {"title": "Two"}]),
        ), patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(side_effect=capture_completion),
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(return_value=[film(666277, "Past Lives", 2023)]),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "emotional", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        context = json.loads(captured_messages[1]["content"])
        assert context["current_mood"] == "emotional"
        assert context["history_tag_frequencies"] == [
            {"tag": "Masterpiece", "count": 2},
            {"tag": "Emotional Damage", "count": 1},
        ]
        assert context["recent_viewed_titles"] == ["One", "Two"]
        assert response.json()["history_tags_used"] == [
            "Masterpiece", "Emotional Damage"
        ]

    def test_malformed_output_retries_once_then_returns_controlled_error(
        self, client, auth_headers
    ):
        completion = AsyncMock(side_effect=["not-json", '{"wrong": []}'])
        with patch(
            "app.external.mistral_client.complete_structured", new=completion
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "relaxed", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.json()["detail"] == (
            "AI recommendation service returned malformed output."
        )
        assert completion.await_count == 2

    def test_duplicate_titles_are_filtered_before_tmdb_lookup(
        self, client, auth_headers
    ):
        raw = ai_output(
            candidate("Arrival", year=2016),
            candidate("  arrival  ", year=2016),
        )
        search = AsyncMock(return_value=[film(329865, "Arrival", 2016)])
        with patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(return_value=raw),
        ), patch("app.services.film_service.search_films", new=search):
            response = client.post(
                "/recommendations",
                json={"mood": "thoughtful", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert search.await_count == 1

    def test_watched_tmdb_ids_and_duplicate_tmdb_results_are_excluded(
        self, client, auth_headers, auth_user, db_session
    ):
        db_session.add(ViewingHistoryEntry(
            user_id=auth_user.id, tmdb_id=329865, tags=[]
        ))
        db_session.commit()
        raw = ai_output(
            candidate("Arrival", year=2016),
            candidate("Another Arrival", year=2016),
            candidate("Moon", year=2009),
        )

        async def search(title):
            if title == "Moon":
                return [film(17431, "Moon", 2009)]
            return [film(329865, "Arrival", 2016)]

        with patch(
            "app.external.tmdb_client.get_movie_basic",
            new=AsyncMock(return_value={"title": "Arrival"}),
        ), patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(return_value=raw),
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(side_effect=search),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "thoughtful", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert [item["film"]["tmdb_id"] for item in response.json()["recommendations"]] == [17431]

    def test_invalid_tmdb_candidate_is_filtered(self, client, auth_headers):
        raw = ai_output(candidate("Made Up Movie"), candidate("Amelie", year=2001))

        async def search(title):
            return [] if title == "Made Up Movie" else [film(194, "Amelie", 2001)]

        with patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(return_value=raw),
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(side_effect=search),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "uplifting", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["recommendations"][0]["film"]["title"] == "Amelie"

    def test_resolution_shortfall_retries_with_different_candidates(
        self, client, auth_headers
    ):
        completion = AsyncMock(side_effect=[
            ai_output(candidate("Unknown Film")),
            ai_output(candidate("The Grand Budapest Hotel", year=2014)),
        ])

        async def search(title):
            if title == "Unknown Film":
                return []
            return [film(120467, "The Grand Budapest Hotel", 2014)]

        with patch(
            "app.external.mistral_client.complete_structured", new=completion
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(side_effect=search),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "relaxed", "limit": 1},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert completion.await_count == 2
        assert response.json()["recommendations"][0]["film"]["tmdb_id"] == 120467

    def test_year_match_is_preferred(self, client, auth_headers):
        raw = ai_output(candidate("Little Women", year=2019))
        results = [
            film(1, "Little Women", 1994),
            film(331482, "Little Women", 2019),
        ]
        with patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(return_value=raw),
        ), patch(
            "app.services.film_service.search_films",
            new=AsyncMock(return_value=results),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "emotional", "limit": 1},
                headers=auth_headers,
            )

        assert response.json()["recommendations"][0]["film"]["tmdb_id"] == 331482

    def test_missing_api_key_returns_503(
        self, client, auth_headers, monkeypatch
    ):
        monkeypatch.setattr(settings, "MISTRAL_API_KEY", None)
        response = client.post(
            "/recommendations",
            json={"mood": "excited", "limit": 1},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["detail"] == (
            "AI recommendation service is not configured."
        )

    def test_mistral_timeout_returns_controlled_error(
        self, client, auth_headers
    ):
        with patch(
            "app.external.mistral_client.complete_structured",
            new=AsyncMock(side_effect=httpx.ReadTimeout("slow upstream")),
        ):
            response = client.post(
                "/recommendations",
                json={"mood": "scared", "limit": 1},
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert response.json()["detail"] == "AI recommendation service timed out."


def test_mistral_client_uses_official_structured_output_contract(monkeypatch):
    recorded = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"candidates": []}'}}]}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, headers, json):
            recorded.update(url=url, headers=headers, payload=json)
            return FakeResponse()

    monkeypatch.setattr(settings, "MISTRAL_API_KEY", "test-mistral-key")
    monkeypatch.setattr(settings, "MISTRAL_API_BASE_URL", "https://api.mistral.ai/v1")
    monkeypatch.setattr(settings, "MISTRAL_MODEL", "mistral-small-latest")
    monkeypatch.setattr(
        mistral_client.httpx, "AsyncClient", lambda **kwargs: FakeClient()
    )

    content = asyncio.run(mistral_client.complete_structured(
        messages=[{"role": "user", "content": "Return JSON."}],
        response_schema={"type": "object", "additionalProperties": False},
    ))

    assert content == '{"candidates": []}'
    assert recorded["url"] == "https://api.mistral.ai/v1/chat/completions"
    assert recorded["payload"]["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "film_recommendation_candidates",
            "schema": {"type": "object", "additionalProperties": False},
            "strict": True,
        },
    }
    assert recorded["headers"]["Authorization"] == "Bearer test-mistral-key"
