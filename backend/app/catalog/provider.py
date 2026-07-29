"""Provider boundary for film metadata."""

import re
import unicodedata
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.film_catalog import FilmCatalog
from app.repositories import film_catalog_repository


def normalize_search_text(value: str) -> str:
    """Normalize Japanese/Latin title input without online transliteration."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[\W_]+", "", normalized, flags=re.UNICODE)


class FilmCatalogProvider(Protocol):
    """Replaceable catalogue interface used by all main film flows."""

    def search(
        self, db: Session, query: str, limit: int = 30
    ) -> list[FilmCatalog]: ...

    def get(self, db: Session, film_id: int) -> FilmCatalog | None: ...

    def get_by_tmdb_id(
        self, db: Session, tmdb_id: int
    ) -> FilmCatalog | None: ...

    def list_all(self, db: Session) -> list[FilmCatalog]: ...


class LocalFilmCatalogProvider:
    """PostgreSQL/SQLite implementation with no external HTTP communication."""

    def search(
        self, db: Session, query: str, limit: int = 30
    ) -> list[FilmCatalog]:
        normalized_query = normalize_search_text(query)
        if not normalized_query:
            return []
        return film_catalog_repository.search(db, normalized_query, limit)

    def get(self, db: Session, film_id: int) -> FilmCatalog | None:
        return film_catalog_repository.get_by_id(db, film_id)

    def get_by_tmdb_id(
        self, db: Session, tmdb_id: int
    ) -> FilmCatalog | None:
        return film_catalog_repository.get_by_tmdb_id(db, tmdb_id)

    def list_all(self, db: Session) -> list[FilmCatalog]:
        return film_catalog_repository.list_all(db)
