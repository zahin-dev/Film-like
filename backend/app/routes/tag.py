"""
Tag Routes

This module defines the FastAPI router for tag-related endpoints.
Tags are read-only reference data — they are seeded once and never
modified by users. This router exposes them so the frontend can
display the full list when a user logs a film.

Routes:
    - GET /tags: return all available tags
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.viewing_history import TagResponse
from app.services import viewing_history_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse], status_code=status.HTTP_200_OK)
def get_tags(db: Session = Depends(get_db)):
    """
    Return all available mood/quality tags.

    No authentication required — tags are public reference data.
    The frontend uses this list to populate the tag selector when
    a user logs a film in their viewing history.

    Returns:
        list[TagResponse]: All tags ordered by id, each with
            id, name, and description.
    """
    return viewing_history_service.get_all_tags(db)
