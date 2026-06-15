"""
Tag

This module defines the Tag SQLAlchemy model, representing a mood or
quality label that a user can attach to a viewing history entry.

Tags are reference data: they are seeded once at setup (via seeds/seed_tag.py)
and never modified by users. They use an integer primary key instead of UUID
because they are looked up by id in a join table, and do not need the
created_at / updated_at timestamps provided by BaseModel.
"""

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer


class Tag(Base):
    """
    SQLAlchemy model representing a mood or quality label for a film.

    Tags are seeded at setup and shared across all users — a user
    picks from the existing list when logging a viewing history entry.

    Intentionally inherits from Base (not BaseModel) because tags are
    static reference data: no UUID primary key, no timestamps.

    Attributes:
        id (int): Auto-incremented integer primary key.
        name (str): Unique display label. Maximum 30 characters.
            Example: "Hidden Gem", "Comfort Movie".
        description (str): Short explanation shown in the UI.
            Maximum 255 characters.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
