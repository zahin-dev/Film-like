"""Tests for authenticated, deterministic diary reaction insights."""

from datetime import datetime, timedelta

from fastapi import status
from sqlalchemy import select

from app.models.tag import Tag
from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry


def _register(client, email: str) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Diary",
            "last_name": "Viewer",
            "email": email,
            "password": "Test1234!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _user(db_session, email: str) -> User:
    return db_session.execute(
        select(User).where(User.email == email)
    ).scalars().one()


def _tag(db_session, name: str) -> Tag:
    tag = Tag(name=name, description=f"{name} test signal")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


def _add_entry(
    db_session,
    user: User,
    tmdb_id: int,
    tags: list[Tag] | None = None,
    created_at: datetime | None = None,
) -> None:
    entry = ViewingHistoryEntry(
        user_id=user.id,
        tmdb_id=tmdb_id,
        tags=tags or [],
    )
    if created_at is not None:
        entry.created_at = created_at
    db_session.add(entry)
    db_session.commit()


def test_insights_requires_authentication(client):
    assert client.get("/insights").status_code == status.HTTP_403_FORBIDDEN


def test_insights_empty_history(client):
    headers = _register(client, "empty-insights@test.com")

    response = client.get("/insights", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "total_films": 0,
        "tagged_films": 0,
        "unique_reaction_signals": 0,
        "top_reaction_signals": [],
        "recent_reaction_signals": [],
    }


def test_insights_history_without_tags(client, db_session):
    email = "untagged-insights@test.com"
    headers = _register(client, email)
    user = _user(db_session, email)
    _add_entry(db_session, user, 101)
    _add_entry(db_session, user, 102)

    body = client.get("/insights", headers=headers).json()

    assert body["total_films"] == 2
    assert body["tagged_films"] == 0
    assert body["unique_reaction_signals"] == 0
    assert body["top_reaction_signals"] == []
    assert body["recent_reaction_signals"] == []


def test_insights_counts_and_percentages(client, db_session):
    email = "counted-insights@test.com"
    headers = _register(client, email)
    user = _user(db_session, email)
    reflective = _tag(db_session, "Reflective")
    comforting = _tag(db_session, "Comforting")
    _add_entry(db_session, user, 201, [reflective, comforting])
    _add_entry(db_session, user, 202, [reflective])
    _add_entry(db_session, user, 203, [comforting])
    _add_entry(db_session, user, 204)

    body = client.get("/insights", headers=headers).json()

    assert body["total_films"] == 4
    assert body["tagged_films"] == 3
    assert body["unique_reaction_signals"] == 2
    assert body["top_reaction_signals"] == [
        {"tag": "Comforting", "count": 2, "percentage": 66.67},
        {"tag": "Reflective", "count": 2, "percentage": 66.67},
    ]


def test_insights_uses_deterministic_tie_ordering(client, db_session):
    email = "ordered-insights@test.com"
    headers = _register(client, email)
    user = _user(db_session, email)
    beta = _tag(db_session, "beta")
    alpha = _tag(db_session, "Alpha")
    _add_entry(db_session, user, 301, [beta])
    _add_entry(db_session, user, 302, [alpha])

    signals = client.get("/insights", headers=headers).json()[
        "top_reaction_signals"
    ]

    assert [signal["tag"] for signal in signals] == ["Alpha", "beta"]


def test_insights_recent_history_uses_latest_five_entries(client, db_session):
    email = "recent-insights@test.com"
    headers = _register(client, email)
    user = _user(db_session, email)
    old = _tag(db_session, "Old Signal")
    current = _tag(db_session, "Current Signal")
    fresh = _tag(db_session, "Fresh Signal")
    start = datetime(2026, 1, 1)
    tag_groups = [[old], [current], [current], [fresh], [], []]
    for offset, tags in enumerate(tag_groups):
        _add_entry(
            db_session,
            user,
            400 + offset,
            tags,
            created_at=start + timedelta(days=offset),
        )

    body = client.get("/insights", headers=headers).json()

    assert [signal["tag"] for signal in body["recent_reaction_signals"]] == [
        "Current Signal",
        "Fresh Signal",
    ]
    assert body["recent_reaction_signals"] == [
        {"tag": "Current Signal", "count": 2, "percentage": 66.67},
        {"tag": "Fresh Signal", "count": 1, "percentage": 33.33},
    ]


def test_insights_are_isolated_per_user(client, db_session):
    first_email = "first-insights@test.com"
    second_email = "second-insights@test.com"
    first_headers = _register(client, first_email)
    second_headers = _register(client, second_email)
    first_user = _user(db_session, first_email)
    second_user = _user(db_session, second_email)
    first_tag = _tag(db_session, "First User Signal")
    second_tag = _tag(db_session, "Second User Signal")
    _add_entry(db_session, first_user, 501, [first_tag])
    _add_entry(db_session, second_user, 502, [second_tag])

    first_body = client.get("/insights", headers=first_headers).json()
    second_body = client.get("/insights", headers=second_headers).json()

    assert first_body["total_films"] == 1
    assert first_body["top_reaction_signals"][0]["tag"] == "First User Signal"
    assert second_body["total_films"] == 1
    assert second_body["top_reaction_signals"][0]["tag"] == "Second User Signal"
