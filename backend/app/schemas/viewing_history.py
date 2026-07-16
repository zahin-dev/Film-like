"""Schemas for tags and user-owned viewing-history records."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.prestige_tier import PrestigeTier


class TagResponse(BaseModel):
    """Public representation of an application-managed tag."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class ViewingHistoryEntryCreate(BaseModel):
    """Payload for logging a TMDB film in viewing history."""

    tmdb_id: int = Field(gt=0)
    tag_ids: list[int] = Field(default_factory=list)
    prestige_tier: PrestigeTier | None = None
    personal_note: str | None = None


class ViewingHistoryEntryResponse(BaseModel):
    """Viewing-history record enriched with display metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tmdb_id: int
    title: str | None = None
    poster_url: str | None = None
    tags: list[TagResponse] = Field(default_factory=list)
    prestige_tier: PrestigeTier | None = None
    personal_note: str | None = None
    created_at: datetime
    updated_at: datetime
