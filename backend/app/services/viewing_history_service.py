"""
Viewing History Service

This module implements the business logic for viewing history operations
in the Film-like application.

It orchestrates entry creation, history retrieval, and entry removal.
Input validation is handled upstream by Pydantic schemas, and data
persistence is delegated to the viewing history repository.

Functions:
    - get_all_tags: return all available tags
    - create_entry: log a new film in the user's viewing history
    - get_history: retrieve the full viewing history of a user
    - remove_entry: remove a film from the user's viewing history
"""

import asyncio

import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import viewing_history_repository
from app.schemas.viewing_history import (
    TagResponse, ViewingHistoryEntryCreate, ViewingHistoryEntryResponse
)
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.models.user import User
from app.external import tmdb_client

# Reuse the same image base URL as film_service
_POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_all_tags(db: Session) -> list[TagResponse]:
    """
    Return all available tags as TagResponse objects.

    Used by GET /tags so the frontend can display the full list of
    mood/quality labels before the user creates a viewing history entry.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI.

    Returns:
        list[TagResponse]: All tags ordered by id.
    """
    tags = viewing_history_repository.get_all_tags(db)
    return [TagResponse.model_validate(tag) for tag in tags]


async def create_entry(
    db: Session, user: User, payload: ViewingHistoryEntryCreate
) -> ViewingHistoryEntryResponse:
    """
    Log a new film in the user's viewing history.

    Validates the film with TMDB, resolves tag IDs to Tag instances, and
    delegates persistence to the repository. Film metadata is included in the
    response but is never stored in the application database.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI.
        user (User): The authenticated user, injected by get_current_user.
        payload (ViewingHistoryEntryCreate): Validated creation data
            containing tmdb_id, tag_ids, prestige_tier, and personal_note.

    Returns:
        ViewingHistoryEntryResponse: The created entry with all fields
            populated, including title, poster_url, and resolved tags.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response.
        httpx.RequestError: If the TMDB request cannot be sent.
    """
    film_data = await tmdb_client.get_movie_basic(payload.tmdb_id)
    tags = viewing_history_repository.get_tags_by_ids(db, payload.tag_ids)
    entry = ViewingHistoryEntry(
        user_id=user.id,
        tmdb_id=payload.tmdb_id,
        tags=tags,
        prestige_tier=payload.prestige_tier,
        personal_note=payload.personal_note
    )
    created = viewing_history_repository.create(db, entry)
    return _entry_response(created, film_data)


async def get_history(
    db: Session, user: User
) -> list[ViewingHistoryEntryResponse]:
    """
    Retrieve the full viewing history of the authenticated user.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI.
        user (User): The authenticated user, injected by get_current_user.

    Returns:
        list[ViewingHistoryEntryResponse]: All viewing history entries,
            enriched concurrently with current TMDB title and poster data.
            If an individual lookup fails, that entry is retained with null
            display metadata. Returns an empty list if none exist.
    """
    entries = viewing_history_repository.get_by_user(db, user.id)
    return await asyncio.gather(*(_enrich_entry(entry) for entry in entries))


async def _enrich_entry(
    entry: ViewingHistoryEntry,
) -> ViewingHistoryEntryResponse:
    """Resolve display metadata for one entry without affecting persistence."""
    try:
        film_data = await tmdb_client.get_movie_basic(entry.tmdb_id)
    except httpx.HTTPError:
        film_data = None
    return _entry_response(entry, film_data)


def _entry_response(
    entry: ViewingHistoryEntry,
    film_data: dict | None,
) -> ViewingHistoryEntryResponse:
    """Build an API response from persisted reactions and transient metadata."""
    response = ViewingHistoryEntryResponse.model_validate(entry)
    if not film_data:
        return response

    poster_path = film_data.get("poster_path")
    return response.model_copy(update={
        "title": film_data.get("title"),
        "poster_url": _POSTER_BASE_URL + poster_path if poster_path else None,
    })


def remove_entry(
    db: Session, user: User, tmdb_id: int
) -> None:
    """
    Remove a film from the user's viewing history.

    Delegates deletion to the repository. Raises 404 if the user has
    no entry for the given film, so the error propagates directly to
    the FastAPI route without any additional handling.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI.
        user (User): The authenticated user, injected by get_current_user.
        tmdb_id (int): TMDB identifier of the film to remove.

    Raises:
        HTTPException 404: If the user has no history entry for this film.
    """
    removed = viewing_history_repository.remove(db, user.id, tmdb_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history entry found for this film."
        )
