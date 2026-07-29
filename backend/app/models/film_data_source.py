"""Provenance and licence metadata for locally imported film records."""

from datetime import date

from sqlalchemy import Boolean, Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FilmDataSource(Base):
    """A declared source whose terms were reviewed before local import."""

    __tablename__ = "film_data_sources"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    license_name: Mapped[str] = mapped_column(String(160), nullable=False)
    license_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    commercial_use: Mapped[str] = mapped_column(String(40), nullable=False)
    redistribution: Mapped[str] = mapped_column(String(40), nullable=False)
    obtained_on: Mapped[date] = mapped_column(Date, nullable=False)
    has_japanese_metadata: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    update_method: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    films: Mapped[list["FilmCatalog"]] = relationship(back_populates="source")
