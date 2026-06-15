"""
Viewing History Entry

This module defines the ViewingHistoryEntry SQLAlchemy model, representing
a single film logged by a user in their personal viewing history.

Each entry links a user to a TMDB film (by id only — no film data is stored
locally) and stores the user's personal reaction: an optional prestige tier
rating, free-text note, and a set of mood/quality tags chosen from the
shared tag list.

The many-to-many relationship between entries and tags is handled by the
viewing_history_tags association table defined in this module.
"""

from app.database import Base
from app.models.base_model import BaseModel
from app.models.prestige_tier import PrestigeTier
from app.models.tag import Tag
from sqlalchemy import Table, Column, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

# Association table for the many-to-many relationship between
# ViewingHistoryEntry and Tag. Not a model — no extra columns needed.
viewing_history_tags = Table(
    "viewing_history_tags",
    Base.metadata,
    Column("viewing_history_entry_id", ForeignKey("viewing_history_entries.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)


class ViewingHistoryEntry(BaseModel):
    """
    SQLAlchemy model representing a film logged by a user.

    Inherits from BaseModel, which provides:
        - id (UUID primary key)
        - created_at (set at insertion)
        - updated_at (refreshed on every update)

    Attributes:
        user_id (UUID): Foreign key to the user who logged this entry.
        tmdb_id (int): TMDB identifier of the film. Not a foreign key —
            film metadata is fetched on demand from TMDB, never stored.
        title (str, optional): Film title cached at log time to avoid
            a TMDB call when displaying the history list.
        poster_url (str, optional): Full poster URL cached at log time
            for the same reason. None if TMDB had no poster.
        tags (list[Tag]): Mood/quality labels chosen by the user.
            Loaded eagerly (lazy="joined") since tags are always needed
            when displaying a history entry.
        prestige_tier (PrestigeTier, optional): The user's personal
            rating for this film (Platinum → Trash).
        personal_note (str, optional): Free-text note from the user.
            No length limit — stored as TEXT in PostgreSQL.
    """

    __tablename__ = "viewing_history_entries"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    tmdb_id: Mapped[int] = mapped_column(
        nullable=False
    )
    title: Mapped[str | None] = mapped_column(
        nullable=True
    )
    poster_url: Mapped[str | None] = mapped_column(
        nullable=True
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=viewing_history_tags,
        lazy="joined"
    )
    prestige_tier: Mapped[PrestigeTier | None] = mapped_column(
        # values_callable tells SQLAlchemy to store the VALUE string ("Platinum")
        # instead of the Python member name ("PLATINUM"). This must match the
        # PostgreSQL enum type created by the migration, which uses the values.
        Enum(PrestigeTier, values_callable=lambda e: [x.value for x in e]),
        nullable=True
    )
    personal_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
