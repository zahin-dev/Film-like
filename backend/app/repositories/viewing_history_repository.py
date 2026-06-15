"""
Viewing History Repository

This module provides data access functions for the ViewingHistoryEntry entity.
It is the only layer in the application that communicates directly with the
database for viewing history operations.

All functions receive a SQLAlchemy Session as their first argument,
injected by FastAPI via the get_db() dependency.

Functions:
    - get_all_tags: fetch all available tags
    - get_tags_by_ids: fetch Tag objects from a list of IDs
    - create: persist a new entry and return the created instance
    - get_by_user: retrieve all entries for a given user
    - get_by_user_and_tmdb: retrieve a specific entry by user and film
    - remove: delete an entry by user and film
"""

from app.models.viewing_history_entry import ViewingHistoryEntry
from app.models.tag import Tag
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID


def get_all_tags(db: Session) -> list[Tag]:
    """
    Fetch all tags available in the application.

    Used by GET /tags to let the frontend display the full list of
    mood/quality labels a user can attach to a viewing history entry.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        list[Tag]: All Tag instances ordered by id.
    """
    return db.execute(
        select(Tag).order_by(Tag.id)
    ).scalars().all()


def get_tags_by_ids(db: Session, tag_ids: list[int]) -> list[Tag]:
    """
    Fetch Tag objects from a list of integer IDs.

    Used by the viewing history service to resolve the tag_ids from the
    request payload into Tag instances before attaching them to an entry.
    IDs that do not match any tag are silently ignored.

    Args:
        db (Session): SQLAlchemy database session.
        tag_ids (list[int]): List of tag IDs to look up.

    Returns:
        list[Tag]: Tag instances matching the provided IDs.
            Returns an empty list if tag_ids is empty or no match is found.
    """
    if not tag_ids:
        return []
    return db.execute(
        select(Tag).where(Tag.id.in_(tag_ids))
    ).scalars().all()


def create(db: Session, entry: ViewingHistoryEntry) -> ViewingHistoryEntry:
    """
    Persist a new ViewingHistoryEntry instance to the database.

    Tags must be assigned to entry.tags before calling this function —
    SQLAlchemy handles the viewing_history_tags join table automatically
    on commit.

    Adds the entry to the session, commits the transaction, then refreshes
    the instance to load all server-generated values (id, created_at,
    updated_at) and the eagerly loaded tags.

    Args:
        db (Session): SQLAlchemy database session.
        entry (ViewingHistoryEntry): Entry instance to persist. Must have
            user_id, tmdb_id, and tags set before being passed here.

    Returns:
        ViewingHistoryEntry: The persisted entry with all database-generated
            fields populated.
    """
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_by_user(db: Session, user_id: UUID) -> list[ViewingHistoryEntry]:
    """
    Retrieve all viewing history entries for a given user.

    Results are not ordered — ordering by created_at can be added
    at the route level if needed.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (UUID): UUID of the user whose history to retrieve.

    Returns:
        list[ViewingHistoryEntry]: All entries belonging to the user.
            Returns an empty list if the user has no history.
    """
    # unique() is required when lazy="joined" is used on a collection relationship.
    # The JOIN produces one row per tag, so SQLAlchemy 2.0 requires explicit
    # deduplication before converting to a Python list.
    return db.execute(
        select(ViewingHistoryEntry)
        .where(ViewingHistoryEntry.user_id == user_id)
    ).unique().scalars().all()


def get_by_user_and_tmdb(
    db: Session, user_id: UUID, tmdb_id: int
) -> ViewingHistoryEntry | None:
    """
    Retrieve a specific viewing history entry by user and TMDB film ID.

    Used internally by remove() to fetch the entry before deletion,
    and by the service layer to check whether a user has already
    logged a given film.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (UUID): UUID of the user.
        tmdb_id (int): TMDB identifier of the film.

    Returns:
        ViewingHistoryEntry: The matching entry, or None if not found.
    """
    # unique() required for the same reason as get_by_user: lazy="joined"
    # on tags can produce multiple rows for a single entry.
    # scalar_one_or_none() doesn't accept unique(), so we chain through scalars().
    return db.execute(
        select(ViewingHistoryEntry)
        .where(ViewingHistoryEntry.user_id == user_id)
        .where(ViewingHistoryEntry.tmdb_id == tmdb_id)
    ).unique().scalars().one_or_none()


def remove(db: Session, user_id: UUID, tmdb_id: int) -> bool:
    """
    Delete a viewing history entry identified by user and TMDB film ID.

    Fetches the entry first to confirm it exists. Returns False if not
    found so the service layer can raise an appropriate HTTP error
    without coupling the repository to FastAPI.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (UUID): UUID of the user who owns the entry.
        tmdb_id (int): TMDB identifier of the film to remove.

    Returns:
        bool: True if the entry was found and deleted, False otherwise.
    """
    entry_to_delete = get_by_user_and_tmdb(db, user_id, tmdb_id)

    if not entry_to_delete:
        return False

    db.delete(entry_to_delete)
    db.commit()
    return True
