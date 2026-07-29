"""Local deterministic recommendation-engine tests."""

import re

from sqlalchemy import select

from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry


def _current_user(db_session):
    return db_session.execute(
        select(User).where(User.email == "hanako@example.com")
    ).scalar_one()


def _recommend(client, headers, mood="thoughtful", limit=5):
    return client.post(
        "/recommendations",
        json={"mood": mood, "limit": limit},
        headers=headers,
    )


def test_api_key_is_not_required_and_reasons_are_japanese(
    client, auth_headers
):
    response = _recommend(client, auth_headers, mood="thoughtful", limit=5)
    assert response.status_code == 200
    body = response.json()
    assert body["mood"] == "thoughtful"
    assert body["mood_label"] == "じっくり考えたい"
    assert len(body["recommendations"]) == 5
    for item in body["recommendations"]:
        assert re.search(r"[ぁ-んァ-ヶ一-龠]", item["reason"])


def test_same_input_and_data_return_same_order(client, auth_headers):
    first = _recommend(client, auth_headers, mood="excited", limit=5).json()
    second = _recommend(client, auth_headers, mood="excited", limit=5).json()
    first_ids = [item["film"]["id"] for item in first["recommendations"]]
    second_ids = [item["film"]["id"] for item in second["recommendations"]]
    assert first_ids == second_ids
    assert len(first_ids) == len(set(first_ids))


def test_mood_changes_top_candidate(client, auth_headers):
    scared = _recommend(client, auth_headers, mood="scared", limit=1).json()
    relaxed = _recommend(client, auth_headers, mood="relaxed", limit=1).json()
    assert scared["recommendations"][0]["film"]["title"] == "リング"
    assert relaxed["recommendations"][0]["film"]["title"] == "海街diary"


def test_watched_films_are_excluded(
    client, auth_headers, db_session, demo_films
):
    ring = next(film for film in demo_films if film.title_ja == "リング")
    assert client.post(
        "/films/log",
        json={"film_id": ring.id},
        headers=auth_headers,
    ).status_code == 201

    body = _recommend(client, auth_headers, mood="scared", limit=10).json()
    ids = [item["film"]["id"] for item in body["recommendations"]]
    assert ring.id not in ids
    assert len(ids) == len(set(ids))


def test_history_tag_is_disclosed_and_used_in_reason(
    client, auth_headers, db_session, demo_films
):
    tag = next(
        tag for tag in client.get("/tags").json()
        if tag["key"] == "feel-good"
    )
    client.post(
        "/films/log",
        json={"film_id": demo_films[0].id, "tag_ids": [tag["id"]]},
        headers=auth_headers,
    )
    body = _recommend(client, auth_headers, mood="relaxed", limit=2).json()
    assert body["history_tags_used"] == ["元気をもらえる"]
    assert any(
        "元気をもらえる" in item["reason"]
        for item in body["recommendations"]
    )


def test_recent_genres_are_reflected_in_explanation(
    client, auth_headers, demo_films
):
    tokyo_story = next(
        film for film in demo_films if film.title_ja == "東京物語"
    )
    client.post(
        "/films/log",
        json={"film_id": tokyo_story.id},
        headers=auth_headers,
    )
    body = _recommend(client, auth_headers, mood="thoughtful", limit=5).json()
    assert any(
        "最近よく観ているドラマ" in item["reason"]
        for item in body["recommendations"]
    )


def test_candidate_shortage_returns_controlled_unique_fallback(
    client, auth_headers, db_session, demo_films
):
    user = _current_user(db_session)
    for film in demo_films[:-1]:
        db_session.add(
            ViewingHistoryEntry(
                user_id=user.id,
                film_id=film.id,
                tmdb_id=film.tmdb_id,
                tags=[],
            )
        )
    db_session.commit()

    body = _recommend(client, auth_headers, mood="scared", limit=5).json()
    assert len(body["recommendations"]) == 1
    assert body["fallback_used"] is True
    assert body["message"] == (
        "未視聴の候補が少ないため、取得できた範囲で表示しています。"
    )


def test_no_candidates_is_not_an_error(
    client, auth_headers, db_session, demo_films
):
    user = _current_user(db_session)
    for film in demo_films:
        db_session.add(
            ViewingHistoryEntry(
                user_id=user.id,
                film_id=film.id,
                tmdb_id=film.tmdb_id,
                tags=[],
            )
        )
    db_session.commit()
    response = _recommend(client, auth_headers, mood="romantic", limit=5)
    assert response.status_code == 200
    assert response.json()["recommendations"] == []
    assert response.json()["message"] == (
        "未視聴の候補がありません。カタログに映画を追加してください。"
    )


def test_recommendations_require_authentication(client):
    response = client.post(
        "/recommendations", json={"mood": "relaxed", "limit": 5}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "ログインが必要です。"


def test_invalid_mood_returns_japanese_validation(client, auth_headers):
    response = _recommend(client, auth_headers, mood="hungry", limit=5)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == (
        "気分の選択肢が正しくありません。"
    )
