"""Pydantic request and response schemas for the Film-like API."""

from app.schemas.film import Film, FilmWithStatus
from app.schemas.recommendation import (
    Mood,
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
)
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse
from app.schemas.viewing_history import (
    TagResponse,
    ViewingHistoryEntryCreate,
    ViewingHistoryEntryResponse,
)

__all__ = [
    "AuthResponse",
    "Film",
    "FilmWithStatus",
    "Mood",
    "Recommendation",
    "RecommendationRequest",
    "RecommendationResponse",
    "TagResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "ViewingHistoryEntryCreate",
    "ViewingHistoryEntryResponse",
]
