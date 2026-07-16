"""Pydantic request and response schemas for the Film-like API."""

from app.schemas.film import Film, FilmWithStatus
from app.schemas.insight import DiaryInsightsResponse, ReactionSignalSummary
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
    "DiaryInsightsResponse",
    "Mood",
    "Recommendation",
    "RecommendationRequest",
    "RecommendationResponse",
    "ReactionSignalSummary",
    "TagResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "ViewingHistoryEntryCreate",
    "ViewingHistoryEntryResponse",
]
