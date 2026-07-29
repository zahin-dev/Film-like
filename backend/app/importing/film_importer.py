"""Import licensed film metadata from local JSON files."""

from datetime import date, datetime
import json
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.catalog.provider import normalize_search_text
from app.models.film_catalog import FilmCatalog
from app.models.film_data_source import FilmDataSource
from app.repositories import film_catalog_repository


class SourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,63}$")
    display_name: str = Field(min_length=1, max_length=160)
    license_name: str = Field(min_length=1, max_length=160)
    license_url: str | None = Field(default=None, max_length=500)
    commercial_use: str = Field(min_length=1, max_length=40)
    redistribution: str = Field(min_length=1, max_length=40)
    obtained_on: date
    has_japanese_metadata: bool
    update_method: str = Field(min_length=1)
    notes: str | None = None


class FilmImportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_id: str = Field(min_length=1, max_length=160)
    tmdb_id: int | None = Field(default=None, gt=0)
    title_ja: str | None = Field(default=None, max_length=300)
    original_title: str | None = Field(default=None, max_length=300)
    search_aliases: list[str] = Field(default_factory=list)
    synopsis_ja: str | None = None
    release_date: date | None = None
    runtime_minutes: int | None = Field(default=None, gt=0, le=1000)
    genres: list[str] = Field(default_factory=list)
    directors: list[str] = Field(default_factory=list)
    cast_members: list[str] = Field(default_factory=list)
    poster_path: str | None = None
    streaming_platforms: list[str] = Field(default_factory=list)
    streaming_region: str = "JP"
    streaming_updated_at: datetime | None = None
    recommendation_moods: list[str] = Field(default_factory=list)

    @field_validator("poster_path")
    @classmethod
    def validate_local_poster_path(cls, value: str | None) -> str | None:
        if value is None:
            return value
        path = PurePosixPath(value)
        if (
            not value.startswith("/posters/")
            or ".." in path.parts
            or value.startswith("//")
        ):
            raise ValueError("ポスターは /posters/ 以下のローカルパスを指定してください")
        return value

    @field_validator("streaming_region")
    @classmethod
    def require_japan_region(cls, value: str) -> str:
        if value != "JP":
            raise ValueError("配信地域は JP を指定してください")
        return value

    @field_validator("recommendation_moods")
    @classmethod
    def validate_moods(cls, values: list[str]) -> list[str]:
        allowed = {
            "relaxed",
            "uplifting",
            "excited",
            "thoughtful",
            "emotional",
            "romantic",
            "adventurous",
            "scared",
        }
        unknown = set(values) - allowed
        if unknown:
            raise ValueError(f"未対応の気分コードです: {', '.join(sorted(unknown))}")
        return values


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_catalog_files(
    db: Session,
    source_manifest_path: Path,
    films_path: Path,
) -> int:
    """Validate and upsert one declared source and its film records."""
    source_payload = SourceManifest.model_validate(_read_json(source_manifest_path))
    film_payloads = [
        FilmImportRecord.model_validate(item)
        for item in _read_json(films_path)
    ]
    source = FilmDataSource(**source_payload.model_dump())
    film_catalog_repository.upsert_source(db, source)

    for payload in film_payloads:
        normalized_title = normalize_search_text(
            " ".join(
                value
                for value in [
                    payload.title_ja or "",
                    payload.original_title or "",
                    *payload.search_aliases,
                ]
                if value
            )
        )
        if not normalized_title:
            raise ValueError(
                f"{payload.external_id}: title_ja、original_title、search_aliases"
                "のいずれかが必要です"
            )
        data = payload.model_dump(exclude={"search_aliases"})
        film_catalog_repository.upsert_film(
            db,
            FilmCatalog(
                source_key=source.key,
                normalized_title=normalized_title,
                **data,
            ),
        )
    db.commit()
    return len(film_payloads)
