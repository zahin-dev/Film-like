"""
Film Routes

This module defines the FastAPI router for film-related endpoints.
It handles HTTP concerns only — query parameter extraction, error
mapping, and response forwarding. All business logic is delegated
to film_service.

Routes:
    - GET  /films/search:          search the TMDB catalog by title
    - GET  /films/history:         retrieve the current user's viewing history
    - GET  /films/{tmdb_id}:       fetch full metadata for a single film
    - POST /films/log:             log a film in the current user's history
    - DELETE /films/log/{tmdb_id}: remove a film from the current user's history
"""

from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
import httpx

from app.database import get_db
from app.schemas.film import Film, FilmWithStatus
from app.services import film_service
from app.dependencies import get_current_user
from app.models.user import User
from app.services import viewing_history_service
from app.schemas.viewing_history import (
    ViewingHistoryEntryCreate, ViewingHistoryEntryResponse
)


router = APIRouter(prefix="/films", tags=["films"])


@router.get("/search", response_model=list[Film], status_code=status.HTTP_200_OK)
async def search_films(query: str = Query(..., min_length=1)):
    """
    Search the TMDB catalog by movie title.

    Args:
        query (str): Movie title to search for. Minimum 1 character.

    Returns:
        list[Film]: Partial Film objects (tmdb_id, title, year,
            poster_url, synopsis). Fields unavailable from the search
            endpoint (genres, cast, director, etc.) are None.

    Raises:
        HTTPException 503: If TMDB returns an error or is unreachable.
    """
    try:
        return await film_service.search_films(query)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Film search service is temporarily unavailable."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the film database. Please try again later."
        )


@router.get("/history", response_model=list[ViewingHistoryEntryResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the authenticated user's full viewing history.

    Each entry contains the tmdb_id of the logged film, its tags,
    prestige tier, and personal note. Film metadata (title, poster, etc.)
    is not embedded — the frontend loads it via GET /films/{tmdb_id}
    to avoid N sequential TMDB calls server-side.

    Returns:
        list[ViewingHistoryEntryResponse]: All entries in the user's
            history. Returns an empty list if none exist.

    Raises:
        HTTPException 401: If the request is not authenticated.
    """
    return viewing_history_service.get_history(db, current_user)


@router.get("/{tmdb_id}", response_model=FilmWithStatus, status_code=status.HTTP_200_OK)
async def get_film(
    tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch full metadata for a single film and the user's history status.

    Args:
        tmdb_id (int): TMDB unique identifier of the movie.

    Returns:
        FilmWithStatus: Fully populated Film object (genres, cast, director,
            runtime, streaming platforms) alongside in_history, which
            indicates whether the current user has already logged this film.

    Raises:
        HTTPException 401: If the request is not authenticated.
        HTTPException 404: If TMDB does not recognise the tmdb_id.
        HTTPException 503: If TMDB returns another error or is unreachable.
    """
    try:
        return await film_service.get_film_with_status(db, current_user, tmdb_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film {tmdb_id} not found."
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Film detail service is temporarily unavailable."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the film database. Please try again later."
        )

@router.post("/log", response_model=ViewingHistoryEntryResponse, status_code=status.HTTP_201_CREATED)
async def log_film(
    payload: ViewingHistoryEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a film in the authenticated user's viewing history.

    Fetches title and poster from TMDB at log time so the history list
    can be displayed without additional API calls.

    Args:
        payload (ViewingHistoryEntryCreate): tmdb_id, optional tag_ids,
            optional prestige_tier, and optional personal_note.

    Returns:
        ViewingHistoryEntryResponse: The created entry with all fields
            populated, including title, poster_url, and resolved tags.

    Raises:
        HTTPException 401: If the request is not authenticated.
        HTTPException 422: If the payload fails validation.
        HTTPException 503: If TMDB is unreachable.
    """
    try:
        return await viewing_history_service.create_entry(db, current_user, payload)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film {payload.tmdb_id} not found."
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Film service temporarily unavailable."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the film database. Please try again later."
        )


@router.delete("/log/{tmdb_id}", status_code=status.HTTP_200_OK)
def remove_film(
    tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a film from the authenticated user's viewing history.

    Args:
        tmdb_id (int): TMDB identifier of the film to remove.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException 401: If the request is not authenticated.
        HTTPException 404: If the user has no history entry for this film.
    """
    viewing_history_service.remove_entry(db, current_user, tmdb_id)
    return {"detail": "Film removed from history."}
