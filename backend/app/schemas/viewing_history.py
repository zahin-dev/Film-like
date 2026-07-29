"""Schemas for tags and user-owned viewing-history records."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.prestige_tier import PrestigeTier


class TagResponse(BaseModel):
    """安定した内部キーと日本語表示を持つ感想タグ。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    description: str


class ViewingHistoryEntryCreate(BaseModel):
    """ローカル映画を記録する入力。旧TMDB IDによる照合にも対応。"""

    film_id: int | None = Field(default=None, gt=0)
    tmdb_id: int | None = Field(default=None, gt=0)
    tag_ids: list[int] = Field(default_factory=list)
    prestige_tier: PrestigeTier | None = None
    personal_note: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_film_identity(self):
        if self.film_id is None and self.tmdb_id is None:
            raise ValueError("映画IDを指定してください")
        return self


class ViewingHistoryEntryResponse(BaseModel):
    """日本語表示情報を含む視聴記録。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    film_id: int
    tmdb_id: int | None = None
    title: str = "映画情報はありません"
    poster_url: str | None = None
    tags: list[TagResponse] = Field(default_factory=list)
    prestige_tier: PrestigeTier | None = None
    prestige_tier_label: str | None = None
    personal_note: str | None = None
    created_at: datetime
    updated_at: datetime
