"""Shared isolated fixtures for the local-only backend test suite."""

import os
from pathlib import Path
import socket

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "film-like-test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.importing import import_catalog_files
from app.main import app
from app.models.film_catalog import FilmCatalog
from app.models.tag import Tag
from seeds.seed_tag import TAGS


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch):
    """Fail immediately if application code attempts a real network socket."""

    def denied(*args, **kwargs):
        raise AssertionError("テスト中の外部ネットワーク接続は禁止されています")

    monkeypatch.setattr(socket, "create_connection", denied)


def _seed(db) -> None:
    for key, legacy_name, description_ja, display_name_ja in TAGS:
        db.add(
            Tag(
                key=key,
                name=legacy_name,
                description=description_ja,
                display_name_ja=display_name_ja,
                description_ja=description_ja,
            )
        )
    db.commit()
    data_dir = Path(__file__).resolve().parents[1] / "data"
    import_catalog_files(
        db,
        data_dir / "demo_source.json",
        data_dir / "demo_films.json",
    )


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _seed(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    payload = {
        "first_name": "花子",
        "last_name": "映画",
        "email": "hanako@example.com",
        "password": "Films123!",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['token']}"}


@pytest.fixture()
def demo_films(db_session):
    return db_session.execute(
        select(FilmCatalog).order_by(FilmCatalog.id)
    ).scalars().all()
