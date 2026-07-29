"""Public schemas for the local, Japanese-first film catalogue."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class Film(BaseModel):
    """ローカルPostgreSQLカタログから取得した映画情報。"""

    id: int = Field(gt=0)
    tmdb_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1)
    original_title: str | None = None
    release_date: date | None = None
    year: int | None = None
    genres: list[str] = Field(default_factory=list)
    poster_url: str | None = None
    synopsis: str = "日本語のあらすじ情報はありません"
    director: str = "監督情報はありません"
    cast: list[str] = Field(default_factory=list)
    runtime: int | None = None
    streaming_platforms: list[str] = Field(default_factory=list)
    streaming_region: str = "JP"
    streaming_updated_at: datetime | None = None
    data_source: str


class FilmWithStatus(BaseModel):
    """映画詳細とログイン中ユーザーの視聴記録状態。"""

    film: Film
    in_history: bool
