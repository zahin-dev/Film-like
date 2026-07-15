"""Schemas for TMDB-backed film data."""

from pydantic import BaseModel, Field


class Film(BaseModel):
    """Film metadata resolved from TMDB and never persisted as an entity."""

    tmdb_id: int = Field(gt=0)
    title: str = Field(min_length=1)
    year: int | None = None
    genres: list[str] | None = None
    poster_url: str | None = None
    synopsis: str | None = None
    director: str | None = None
    cast: list[str] | None = None
    runtime: int | None = None
    streaming_platforms: list[str] | None = None


class FilmWithStatus(BaseModel):
    """TMDB film details plus the current user's history status."""

    film: Film
    in_history: bool
