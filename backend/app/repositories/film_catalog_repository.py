"""Database access for the local film catalogue and its provenance."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.film_catalog import FilmCatalog
from app.models.film_data_source import FilmDataSource


def search(db: Session, normalized_query: str, limit: int = 30) -> list[FilmCatalog]:
    """Find Japanese or original titles using a pre-normalized query."""
    return db.execute(
        select(FilmCatalog)
        .where(FilmCatalog.normalized_title.contains(normalized_query))
        .order_by(
            FilmCatalog.title_ja.is_(None),
            FilmCatalog.release_date.desc(),
            FilmCatalog.id,
        )
        .limit(limit)
    ).scalars().all()


def get_by_id(db: Session, film_id: int) -> FilmCatalog | None:
    return db.get(FilmCatalog, film_id)


def get_by_tmdb_id(db: Session, tmdb_id: int) -> FilmCatalog | None:
    return db.execute(
        select(FilmCatalog).where(FilmCatalog.tmdb_id == tmdb_id)
    ).scalar_one_or_none()


def list_all(db: Session) -> list[FilmCatalog]:
    return db.execute(
        select(FilmCatalog).order_by(FilmCatalog.id)
    ).scalars().all()


def get_source(db: Session, source_key: str) -> FilmDataSource | None:
    return db.get(FilmDataSource, source_key)


def get_by_source_identity(
    db: Session, source_key: str, external_id: str
) -> FilmCatalog | None:
    return db.execute(
        select(FilmCatalog).where(
            FilmCatalog.source_key == source_key,
            FilmCatalog.external_id == external_id,
        )
    ).scalar_one_or_none()


def upsert_source(db: Session, source: FilmDataSource) -> FilmDataSource:
    existing = get_source(db, source.key)
    if existing is None:
        db.add(source)
        return source
    for column in (
        "display_name",
        "license_name",
        "license_url",
        "commercial_use",
        "redistribution",
        "obtained_on",
        "has_japanese_metadata",
        "update_method",
        "notes",
    ):
        setattr(existing, column, getattr(source, column))
    return existing


def upsert_film(db: Session, film: FilmCatalog) -> FilmCatalog:
    existing = get_by_source_identity(db, film.source_key, film.external_id)
    if existing is None and film.tmdb_id is not None:
        tmdb_match = get_by_tmdb_id(db, film.tmdb_id)
        if tmdb_match is not None:
            if tmdb_match.source_key != "legacy-tmdb":
                raise ValueError(
                    f"tmdb_id={film.tmdb_id}は別の出典ですでに使用されています"
                )
            # Replace a migration-only placeholder in place so every existing
            # viewing-history foreign key continues to reference the same ID.
            existing = tmdb_match
            existing.source_key = film.source_key
            existing.external_id = film.external_id
    if existing is None:
        db.add(film)
        return film
    for column in (
        "tmdb_id",
        "title_ja",
        "original_title",
        "synopsis_ja",
        "release_date",
        "runtime_minutes",
        "genres",
        "directors",
        "cast_members",
        "poster_path",
        "streaming_platforms",
        "streaming_region",
        "streaming_updated_at",
        "normalized_title",
        "recommendation_moods",
    ):
        setattr(existing, column, getattr(film, column))
    return existing
