"""
User Repository

This module provides data access functions for the User entity.
It is the only layer in the application that communicates directly
with the database for user-related operations.

All functions receive a SQLAlchemy Session as their first argument,
injected by FastAPI via the get_db() dependency.

Functions:
    - get_by_email: retrieve a user by email address
    - get_by_id: retrieve a user by UUID (used by the auth dependency)
    - create: persist a new user and return the created instance
"""

from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID


def get_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by their email address.

    Used during registration to check for duplicate emails,
    and during login to retrieve the user before password verification.

    Args:
        db (Session): SQLAlchemy database session.
        email (str): Email address to look up.

    Returns:
        User: The matching user instance, or None if not found.
    """
    return db.execute(
        select(User)
        .where(User.email == email)
    ).scalar_one_or_none()


def get_by_id(db: Session, user_id: str) -> User | None:
    """
    Retrieve a user by their UUID.

    Used by the authentication dependency to load the current user
    from the JWT subject claim. The id is received as a string because
    JWT payloads are always strings. It is explicitly converted to a
    UUID object before the comparison so the query works correctly with
    both PostgreSQL and SQLite (SQLite's UUID type requires a UUID object,
    not a raw string).

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): UUID of the user as a string.

    Returns:
        User: The matching user instance, or None if not found or
            if user_id is not a valid UUID string.
    """
    try:
        uid = UUID(user_id)
    except (ValueError, AttributeError):
        return None
    return db.execute(
        select(User)
        .where(User.id == uid)
    ).scalar_one_or_none()


def create(db: Session, user: User) -> User:
    """
    Persist a new User instance to the database.

    Adds the user to the session, commits the transaction, then
    refreshes the instance to load all server-generated values
    such as id, created_at, and updated_at.

    Args:
        db (Session): SQLAlchemy database session.
        user (User): User instance to persist. Must have all required
            fields set before being passed to this function.

    Returns:
        User: The persisted user instance with all database-generated
            fields populated.
    """
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
