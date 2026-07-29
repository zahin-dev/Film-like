"""Japanese-first film operations backed exclusively by the local catalogue."""

from sqlalchemy.orm import Session

from app.catalog import FilmCatalogProvider, LocalFilmCatalogProvider
from app.models.film_catalog import FilmCatalog
from app.models.user import User
from app.repositories import viewing_history_repository
from app.schemas.film import Film, FilmWithStatus


_provider: FilmCatalogProvider = LocalFilmCatalogProvider()


def set_provider(provider: FilmCatalogProvider) -> None:
    """Override the provider in tests or a future self-hosted adapter."""
    global _provider
    _provider = provider


def film_from_record(record: FilmCatalog) -> Film:
    title = record.title_ja or "日本語タイトル情報はありません"
    return Film(
        id=record.id,
        tmdb_id=record.tmdb_id,
        title=title,
        original_title=record.original_title,
        release_date=record.release_date,
        year=record.release_date.year if record.release_date else None,
        genres=record.genres or [],
        poster_url=record.poster_path,
        synopsis=record.synopsis_ja or "日本語のあらすじ情報はありません",
        director="、".join(record.directors) if record.directors else "監督情報はありません",
        cast=record.cast_members or [],
        runtime=record.runtime_minutes,
        streaming_platforms=record.streaming_platforms or [],
        streaming_region=record.streaming_region,
        streaming_updated_at=record.streaming_updated_at,
        data_source=record.source.display_name,
    )


def search_films(db: Session, query: str) -> list[Film]:
    """Search locally, preferring Japanese titles in every result."""
    return [film_from_record(record) for record in _provider.search(db, query)]


def get_film_details(db: Session, film_id: int) -> Film | None:
    record = _provider.get(db, film_id)
    return film_from_record(record) if record else None


def get_film_by_tmdb_id(db: Session, tmdb_id: int) -> Film | None:
    """Compatibility lookup for records migrated from the former TMDB flow."""
    record = _provider.get_by_tmdb_id(db, tmdb_id)
    return film_from_record(record) if record else None


def get_film_with_status(
    db: Session, user: User, film_id: int
) -> FilmWithStatus | None:
    film = get_film_details(db, film_id)
    if film is None:
        return None
    in_history = viewing_history_repository.get_by_user_and_film(
        db, user.id, film_id
    ) is not None
    return FilmWithStatus(film=film, in_history=in_history)


def get_catalog_records(db: Session) -> list[FilmCatalog]:
    """Expose provider records to the deterministic recommendation engine."""
    return _provider.list_all(db)
