"""
Tests for film search, film detail, tags, and viewing history endpoints.

Covers:
    - GET  /tags
    - GET  /films/search
    - GET  /films/{tmdb_id}
    - POST /films/log
    - GET  /films/history
    - DELETE /films/log/{tmdb_id}
    - JWT authentication edge cases (expired, invalid, unknown user)

TMDB API calls are mocked with AsyncMock — no real network calls are made.
"""

import pytest
import httpx
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from fastapi import status

from app.models.tag import Tag
from app.config import settings


# ---------------------------------------------------------------------------
# Mock TMDB data
# ---------------------------------------------------------------------------

TMDB_ID = 27205  # Inception

MOCK_SEARCH_RESULTS = [
    {
        "id": TMDB_ID,
        "title": "Inception",
        "release_date": "2010-07-16",
        "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "overview": "A thief who steals corporate secrets through dream-sharing.",
    }
]

MOCK_MOVIE_BASIC = {
    "id": TMDB_ID,
    "title": "Inception",
    "release_date": "2010-07-16",
    "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
}

MOCK_MOVIE_DETAILS = {
    "id": TMDB_ID,
    "title": "Inception",
    "release_date": "2010-07-16",
    "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
    "overview": "A thief who steals corporate secrets through dream-sharing.",
    "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
    "runtime": 148,
    "credits": {
        "crew": [{"job": "Director", "name": "Christopher Nolan", "department": "Directing"}],
        "cast": [
            {"name": "Leonardo DiCaprio", "order": 0},
            {"name": "Joseph Gordon-Levitt", "order": 1},
        ],
    },
}

MOCK_WATCH_PROVIDERS = {
    "flatrate": [{"provider_name": "Netflix", "logo_path": "/logo.jpg"}]
}


def make_http_error(status_code: int) -> httpx.HTTPStatusError:
    """Build an httpx.HTTPStatusError with the given status code."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    return httpx.HTTPStatusError("error", request=MagicMock(), response=mock_response)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_USER_A = {
    "first_name": "Alice",
    "last_name": "Cinemood",
    "email": "alice@test.com",
    "password": "Test1234!",
}

_USER_B = {
    "first_name": "Bob",
    "last_name": "Cinemood",
    "email": "bob@test.com",
    "password": "Test1234!",
}


@pytest.fixture()
def auth_headers(client):
    """Register user A and return their JWT Authorization headers."""
    client.post("/auth/register", json=_USER_A)
    res = client.post("/auth/login", json={
        "email": _USER_A["email"], "password": _USER_A["password"]
    })
    return {"Authorization": f"Bearer {res.json()['token']}"}


@pytest.fixture()
def other_auth_headers(client):
    """Register user B and return their JWT Authorization headers."""
    client.post("/auth/register", json=_USER_B)
    res = client.post("/auth/login", json={
        "email": _USER_B["email"], "password": _USER_B["password"]
    })
    return {"Authorization": f"Bearer {res.json()['token']}"}


@pytest.fixture()
def seeded_tags(db_session):
    """Insert three test tags directly into the database."""
    tags = [
        Tag(name="Feel-Good Movie", description="Leaves you with a smile"),
        Tag(name="Masterpiece", description="Everything just works. No notes."),
        Tag(name="Emotional Damage", description="You're fine. Totally fine."),
    ]
    for tag in tags:
        db_session.add(tag)
    db_session.commit()
    for tag in tags:
        db_session.refresh(tag)
    return tags


@pytest.fixture()
def logged_film(client, auth_headers):
    """Log Inception for user A and return the response body."""
    with patch("app.external.tmdb_client.get_movie_basic",
               new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
        res = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers)
    return res.json()


# ---------------------------------------------------------------------------
# GET /tags
# ---------------------------------------------------------------------------

class TestGetTags:
    """Public endpoint — no auth required."""

    def test_returns_200_without_auth(self, client):
        assert client.get("/tags").status_code == status.HTTP_200_OK

    def test_empty_when_no_tags_seeded(self, client):
        assert client.get("/tags").json() == []

    def test_returns_all_seeded_tags(self, client, seeded_tags):
        res = client.get("/tags")
        assert len(res.json()) == 3

    def test_response_structure(self, client, seeded_tags):
        tag = client.get("/tags").json()[0]
        assert {"id", "name", "description"} <= tag.keys()

    def test_ordered_by_id(self, client, seeded_tags):
        ids = [t["id"] for t in client.get("/tags").json()]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# GET /films/search
# ---------------------------------------------------------------------------

class TestSearchFilms:
    """No auth required — TMDB calls are mocked."""

    def test_success_returns_results(self, client):
        with patch("app.external.tmdb_client.search_movie",
                   new=AsyncMock(return_value=MOCK_SEARCH_RESULTS)):
            res = client.get("/films/search?query=Inception")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()[0]["title"] == "Inception"
        assert res.json()[0]["tmdb_id"] == TMDB_ID

    def test_maps_year_and_poster_url(self, client):
        with patch("app.external.tmdb_client.search_movie",
                   new=AsyncMock(return_value=MOCK_SEARCH_RESULTS)):
            film = client.get("/films/search?query=Inception").json()[0]
        assert film["year"] == 2010
        assert film["poster_url"].startswith("https://image.tmdb.org")

    def test_empty_results(self, client):
        with patch("app.external.tmdb_client.search_movie",
                   new=AsyncMock(return_value=[])):
            res = client.get("/films/search?query=xyznotamovie")
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []

    def test_missing_query_returns_422(self, client):
        assert client.get("/films/search").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_query_returns_422(self, client):
        assert client.get("/films/search?query=").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_tmdb_http_error_returns_503(self, client):
        with patch("app.external.tmdb_client.search_movie",
                   new=AsyncMock(side_effect=make_http_error(500))):
            res = client.get("/films/search?query=Inception")
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_tmdb_network_error_returns_503(self, client):
        with patch("app.external.tmdb_client.search_movie",
                   new=AsyncMock(side_effect=httpx.RequestError("timeout"))):
            res = client.get("/films/search?query=Inception")
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ---------------------------------------------------------------------------
# GET /films/{tmdb_id}
# ---------------------------------------------------------------------------

class TestGetFilmDetail:
    """Requires auth. Returns FilmWithStatus."""

    def _mock_tmdb(self):
        return (
            patch("app.external.tmdb_client.get_movie_details",
                  new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)),
            patch("app.external.tmdb_client.get_watch_providers",
                  new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)),
        )

    def test_no_token_returns_403(self, client):
        assert client.get(f"/films/{TMDB_ID}").status_code == status.HTTP_403_FORBIDDEN

    def test_success_not_in_history(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)):
            res = client.get(f"/films/{TMDB_ID}", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["film"]["title"] == "Inception"
        assert res.json()["in_history"] is False

    def test_in_history_flag_true_after_log(self, client, auth_headers, logged_film):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)):
            res = client.get(f"/films/{TMDB_ID}", headers=auth_headers)
        assert res.json()["in_history"] is True

    def test_in_history_false_for_other_user(self, client, auth_headers,
                                              other_auth_headers, logged_film):
        """Film logged by user A must not appear as in_history for user B."""
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)):
            res = client.get(f"/films/{TMDB_ID}", headers=other_auth_headers)
        assert res.json()["in_history"] is False

    def test_maps_genres_director_runtime(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)):
            film = client.get(f"/films/{TMDB_ID}", headers=auth_headers).json()["film"]
        assert film["director"] == "Christopher Nolan"
        assert "Action" in film["genres"]
        assert film["runtime"] == 148

    def test_maps_streaming_platforms(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(return_value=MOCK_MOVIE_DETAILS)), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value=MOCK_WATCH_PROVIDERS)):
            film = client.get(f"/films/{TMDB_ID}", headers=auth_headers).json()["film"]
        assert "Netflix" in film["streaming_platforms"]

    def test_tmdb_404_returns_404(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(side_effect=make_http_error(404))), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value={})):
            res = client.get(f"/films/{TMDB_ID}", headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_tmdb_error_returns_503(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_details",
                   new=AsyncMock(side_effect=make_http_error(500))), \
             patch("app.external.tmdb_client.get_watch_providers",
                   new=AsyncMock(return_value={})):
            res = client.get(f"/films/{TMDB_ID}", headers=auth_headers)
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ---------------------------------------------------------------------------
# POST /films/log
# ---------------------------------------------------------------------------

class TestLogFilm:
    """Requires auth. Calls get_movie_basic — mocked."""

    def test_no_token_returns_403(self, client):
        assert client.post("/films/log", json={"tmdb_id": TMDB_ID}).status_code == status.HTTP_403_FORBIDDEN

    def test_missing_tmdb_id_returns_422(self, client, auth_headers):
        assert client.post("/films/log", json={}, headers=auth_headers).status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_success_minimal_payload(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            res = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers)
        assert res.status_code == status.HTTP_201_CREATED

    def test_caches_title_and_poster(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers).json()
        assert body["title"] == "Inception"
        assert body["poster_url"].startswith("https://image.tmdb.org")

    def test_response_has_timestamps_and_id(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers).json()
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    def test_with_tags(self, client, auth_headers, seeded_tags):
        tag_ids = [seeded_tags[0].id, seeded_tags[1].id]
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log",
                               json={"tmdb_id": TMDB_ID, "tag_ids": tag_ids},
                               headers=auth_headers).json()
        assert len(body["tags"]) == 2
        tag_names = {t["name"] for t in body["tags"]}
        assert seeded_tags[0].name in tag_names

    def test_with_prestige_tier(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log",
                               json={"tmdb_id": TMDB_ID, "prestige_tier": "Gold"},
                               headers=auth_headers).json()
        assert body["prestige_tier"] == "Gold"

    def test_with_personal_note(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log",
                               json={"tmdb_id": TMDB_ID, "personal_note": "Best film ever"},
                               headers=auth_headers).json()
        assert body["personal_note"] == "Best film ever"

    def test_with_all_optional_fields(self, client, auth_headers, seeded_tags):
        payload = {
            "tmdb_id": TMDB_ID,
            "tag_ids": [seeded_tags[0].id],
            "prestige_tier": "Platinum",
            "personal_note": "A masterpiece.",
        }
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            body = client.post("/films/log", json=payload, headers=auth_headers).json()
        assert body["prestige_tier"] == "Platinum"
        assert body["personal_note"] == "A masterpiece."
        assert len(body["tags"]) == 1

    def test_invalid_tmdb_id_returns_404(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(side_effect=make_http_error(404))):
            res = client.post("/films/log", json={"tmdb_id": 999999999}, headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_tmdb_error_returns_503(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(side_effect=make_http_error(500))):
            res = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers)
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_tmdb_network_error_returns_503(self, client, auth_headers):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(side_effect=httpx.RequestError("timeout"))):
            res = client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers)
        assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ---------------------------------------------------------------------------
# GET /films/history
# ---------------------------------------------------------------------------

class TestGetHistory:

    def test_no_token_returns_403(self, client):
        assert client.get("/films/history").status_code == status.HTTP_403_FORBIDDEN

    def test_empty_history(self, client, auth_headers):
        res = client.get("/films/history", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == []

    def test_contains_logged_film(self, client, auth_headers, logged_film):
        entries = client.get("/films/history", headers=auth_headers).json()
        assert len(entries) == 1
        assert entries[0]["tmdb_id"] == TMDB_ID

    def test_entry_has_title_and_poster(self, client, auth_headers, logged_film):
        entry = client.get("/films/history", headers=auth_headers).json()[0]
        assert entry["title"] == "Inception"
        assert entry["poster_url"].startswith("https://image.tmdb.org")

    def test_entry_has_empty_tags_by_default(self, client, auth_headers, logged_film):
        entry = client.get("/films/history", headers=auth_headers).json()[0]
        assert entry["tags"] == []

    def test_entry_includes_tags_when_logged_with_tags(self, client, auth_headers, seeded_tags):
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            client.post("/films/log",
                        json={"tmdb_id": TMDB_ID, "tag_ids": [seeded_tags[0].id]},
                        headers=auth_headers)
        entry = client.get("/films/history", headers=auth_headers).json()[0]
        assert len(entry["tags"]) == 1
        assert entry["tags"][0]["name"] == seeded_tags[0].name

    def test_isolated_per_user(self, client, auth_headers, other_auth_headers, logged_film):
        """User B must not see user A's history."""
        assert client.get("/films/history", headers=other_auth_headers).json() == []

    def test_multiple_films(self, client, auth_headers):
        other = {**MOCK_MOVIE_BASIC, "id": 550, "title": "Fight Club"}
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=MOCK_MOVIE_BASIC)):
            client.post("/films/log", json={"tmdb_id": TMDB_ID}, headers=auth_headers)
        with patch("app.external.tmdb_client.get_movie_basic",
                   new=AsyncMock(return_value=other)):
            client.post("/films/log", json={"tmdb_id": 550}, headers=auth_headers)
        assert len(client.get("/films/history", headers=auth_headers).json()) == 2


# ---------------------------------------------------------------------------
# DELETE /films/log/{tmdb_id}
# ---------------------------------------------------------------------------

class TestRemoveFilm:

    def test_no_token_returns_403(self, client):
        assert client.delete(f"/films/log/{TMDB_ID}").status_code == status.HTTP_403_FORBIDDEN

    def test_success_returns_200(self, client, auth_headers, logged_film):
        res = client.delete(f"/films/log/{TMDB_ID}", headers=auth_headers)
        assert res.status_code == status.HTTP_200_OK

    def test_success_returns_confirmation_message(self, client, auth_headers, logged_film):
        res = client.delete(f"/films/log/{TMDB_ID}", headers=auth_headers)
        assert "detail" in res.json()

    def test_entry_gone_from_history_after_remove(self, client, auth_headers, logged_film):
        client.delete(f"/films/log/{TMDB_ID}", headers=auth_headers)
        assert client.get("/films/history", headers=auth_headers).json() == []

    def test_film_not_logged_returns_404(self, client, auth_headers):
        res = client.delete(f"/films/log/{TMDB_ID}", headers=auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_remove_another_users_entry(self, client, auth_headers,
                                                other_auth_headers, logged_film):
        """User B must get 404 when trying to remove user A's entry."""
        res = client.delete(f"/films/log/{TMDB_ID}", headers=other_auth_headers)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_other_users_entry_still_exists_after_failed_remove(
            self, client, auth_headers, other_auth_headers, logged_film):
        client.delete(f"/films/log/{TMDB_ID}", headers=other_auth_headers)
        assert len(client.get("/films/history", headers=auth_headers).json()) == 1


# ---------------------------------------------------------------------------
# JWT authentication edge cases
# ---------------------------------------------------------------------------

class TestAuthentication:
    """Tested through GET /films/history as a representative protected route."""

    def test_no_header_returns_403(self, client):
        """HTTPBearer returns 403 when the Authorization header is absent."""
        assert client.get("/films/history").status_code == status.HTTP_403_FORBIDDEN

    def test_expired_token_returns_401(self, client, auth_headers):
        expired = jwt.encode(
            {
                "sub": "00000000-0000-0000-0000-000000000001",
                "exp": datetime.now(tz=timezone.utc) - timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        res = client.get("/films/history", headers={"Authorization": f"Bearer {expired}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json()["detail"] == "Token expired"

    def test_invalid_token_returns_401(self, client):
        res = client.get("/films/history", headers={"Authorization": "Bearer notavalidtoken"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json()["detail"] == "Invalid token"

    def test_token_wrong_secret_returns_401(self, client):
        bad_token = jwt.encode(
            {"sub": "some-id", "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )
        res = client.get("/films/history", headers={"Authorization": f"Bearer {bad_token}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_unknown_user_returns_401(self, client):
        """Valid token signed with the real key but for a non-existent user UUID."""
        token = jwt.encode(
            {
                "sub": "00000000-0000-0000-0000-000000000000",
                "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        res = client.get("/films/history", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json()["detail"] == "User not found"
