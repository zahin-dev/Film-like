"""Strict response contracts for deterministic diary reaction insights."""

from pydantic import BaseModel, ConfigDict, Field


class ReactionSignalSummary(BaseModel):
    """Count and tagged-film share for one user-selected reaction tag."""

    model_config = ConfigDict(extra="forbid", strict=True)

    tag: str = Field(min_length=1, max_length=30)
    count: int = Field(ge=1)
    percentage: float = Field(ge=0.0, le=100.0)


class DiaryInsightsResponse(BaseModel):
    """Aggregated reaction signals from one authenticated user's diary."""

    model_config = ConfigDict(extra="forbid", strict=True)

    total_films: int = Field(ge=0)
    tagged_films: int = Field(ge=0)
    unique_reaction_signals: int = Field(ge=0)
    top_reaction_signals: list[ReactionSignalSummary]
    recent_reaction_signals: list[ReactionSignalSummary]
