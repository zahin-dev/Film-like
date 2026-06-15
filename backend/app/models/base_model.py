"""
BaseModel

This module defines the abstract base class inherited by all persistent
SQLAlchemy models in the Film-like application.

It centralises the three attributes shared by every entity:
a UUID primary key, a creation timestamp, and a last-updated timestamp.
"""

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from uuid import UUID, uuid4
from datetime import datetime, timezone


class BaseModel(Base):
    """
    Abstract base class for all persistent SQLAlchemy models.

    Inherited by: User, WatchlistEntry, ViewingHistoryEntry.

    This class provides the three attributes shared by every entity,
    avoiding duplication across the codebase.

    Attributes:
        id (UUID): Primary key, generated automatically by Python
            via uuid4(). Never modified after creation.
        created_at (datetime): Timestamp set by PostgreSQL at insertion.
            Never modified after creation.
        updated_at (datetime): Timestamp set by PostgreSQL at insertion,
            refreshed automatically by Python on every update via onupdate.

    Notes:
        __abstract__ = True prevents SQLAlchemy from creating a table
        for this class. Only its subclasses will have database tables.
    """

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=lambda: datetime.now(tz=timezone.utc)
    )
