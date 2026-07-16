"""Schemas for mood-based, TMDB-verified film recommendations."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.film import Film


class Mood(StrEnum):
    """Mood vocabulary supported by the recommendation prompt."""

    RELAXED = "relaxed"
    UPLIFTING = "uplifting"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    EMOTIONAL = "emotional"
    ROMANTIC = "romantic"
    ADVENTUROUS = "adventurous"
    SCARED = "scared"


class RecommendationRequest(BaseModel):
    """Authenticated request for mood-based recommendations."""

    mood: Mood
    limit: int = Field(default=5, ge=1, le=10)


class Recommendation(BaseModel):
    """A recommendation whose film identity was verified through TMDB."""

    film: Film
    reason: str


class RecommendationResponse(BaseModel):
    """Recommendation result plus the user context disclosed to the client."""

    mood: Mood
    history_tags_used: list[str]
    recommendations: list[Recommendation]


class AICandidate(BaseModel):
    """Untrusted candidate shape requested from Mistral."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    title: str = Field(min_length=1, max_length=200)
    year: int | None = Field(default=None, ge=1888, le=2100)
    reason: str = Field(min_length=1, max_length=400)


class AICandidateList(BaseModel):
    """Strict top-level structured output requested from Mistral."""

    model_config = ConfigDict(extra="forbid", strict=True)

    candidates: list[AICandidate] = Field(min_length=1, max_length=20)
