"""Schemas for deterministic, local mood-based recommendations."""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.film import Film


class Mood(StrEnum):
    """画面では日本語表示する安定した気分コード。"""

    RELAXED = "relaxed"
    UPLIFTING = "uplifting"
    EXCITED = "excited"
    THOUGHTFUL = "thoughtful"
    EMOTIONAL = "emotional"
    ROMANTIC = "romantic"
    ADVENTUROUS = "adventurous"
    SCARED = "scared"


class RecommendationRequest(BaseModel):
    """気分に合う映画を推薦するための入力。"""

    mood: Mood
    limit: int = Field(default=5, ge=1, le=10)


class Recommendation(BaseModel):
    """ローカルで採点した映画と説明可能な日本語理由。"""

    film: Film
    reason: str


class RecommendationResponse(BaseModel):
    """推薦結果と、採点に使用したユーザー自身の情報。"""

    mood: Mood
    mood_label: str
    history_tags_used: list[str]
    recommendations: list[Recommendation]
    fallback_used: bool = False
    message: str | None = None
