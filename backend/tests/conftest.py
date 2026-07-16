"""
Test configuration and shared fixtures for Film-like backend tests.

Uses an in-memory SQLite database to isolate tests from the production
PostgreSQL database. Each test gets a fresh database and a clean
FastAPI client — no test can pollute another.

Fixtures:
    - db_session: a SQLAlchemy session connected to the in-memory SQLite DB
    - client: a FastAPI TestClient with get_db overridden to use db_session
"""

import os

# Configure deterministic test-only settings before importing the application.
# Production continues to require its own environment configuration.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "film-like-test-secret-key")
os.environ.setdefault("TMDB_READ_ACCESS_TOKEN", "test-tmdb-access-token")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

SQLITE_URL = "sqlite:///:memory:"

# StaticPool forces SQLAlchemy to reuse a single connection for the
# in-memory database. Without it, create_all and the session get
# separate connections, each seeing an empty DB.
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    """
    Provide a clean SQLite in-memory session for a single test.

    Creates all tables before the test runs and drops them afterwards,
    ensuring complete isolation between tests.

    Yields:
        Session: A SQLAlchemy session bound to the in-memory SQLite database.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """
    Provide a FastAPI TestClient using the test database session.

    Overrides the get_db dependency so every request made through this
    client uses the SQLite session instead of the production PostgreSQL
    session. The override is cleared after the test to avoid leaking
    state between tests.

    Args:
        db_session: The in-memory SQLite session provided by the
            db_session fixture.

    Yields:
        TestClient: A configured FastAPI test client.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
