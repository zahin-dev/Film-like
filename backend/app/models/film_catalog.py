"""Locally persisted Japanese-first film catalogue."""

from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FilmCatalog(Base):
    """Film metadata available without any external API or network access."""

    __tablename__ = "films"
    __table_args__ = (
        UniqueConstraint(
            "source_key",
            "external_id",
            name="uq_films_source_external_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(
        ForeignKey("film_data_sources.key"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(160), nullable=False)
    tmdb_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True
    )
    title_ja: Mapped[str | None] = mapped_column(String(300), nullable=True)
    original_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    synopsis_ja: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genres: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    directors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    cast_members: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    poster_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    streaming_platforms: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    streaming_region: Mapped[str] = mapped_column(
        String(2), nullable=False, default="JP"
    )
    streaming_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    normalized_title: Mapped[str] = mapped_column(
        String(800), nullable=False, index=True
    )
    recommendation_moods: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    source: Mapped["FilmDataSource"] = relationship(back_populates="films")
    viewing_history_entries: Mapped[list["ViewingHistoryEntry"]] = relationship(
        back_populates="film"
    )
