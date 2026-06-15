"""
Database configuration and session management.

This module sets up the SQLAlchemy engine, session factory, and base class
for all ORM models. It also provides the get_db dependency used by FastAPI
routes to access the database session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings  # centralized environment configuration

# SQLAlchemy engine - manages the connection pool to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Session factory - each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    All models in models/ will inherit from this class.
    """
    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Ensures the session is always closed after the request,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
