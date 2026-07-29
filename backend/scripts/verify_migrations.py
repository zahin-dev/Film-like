#!/usr/bin/env python3
"""Destructively verify legacy-data upgrade and rollback on a dedicated DB."""

import os
from pathlib import Path
from uuid import UUID

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def main() -> int:
    url = os.environ.get("MIGRATION_TEST_DATABASE_URL")
    if not url or not url.startswith("postgresql"):
        raise RuntimeError("PostgreSQLのMIGRATION_TEST_DATABASE_URLが必要です")
    if os.environ.get("ALLOW_DESTRUCTIVE_MIGRATION_TEST") != "1":
        raise RuntimeError(
            "専用テストDBであることを確認し、"
            "ALLOW_DESTRUCTIVE_MIGRATION_TEST=1を設定してください"
        )

    os.environ["DATABASE_URL"] = url
    os.environ.setdefault("SECRET_KEY", "migration-test-secret")
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    command.downgrade(config, "base")
    command.upgrade(config, "b3d91f6a2c04")

    user_id = UUID("11111111-1111-1111-1111-111111111111")
    history_id = UUID("22222222-2222-2222-2222-222222222222")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO users (
                    id, first_name, last_name, username, email,
                    hashed_password, is_admin, age
                ) VALUES (
                    :id, '移行', '確認', '移行確認', 'migration@example.com',
                    'not-used-in-test', false, NULL
                )
                """
            ),
            {"id": user_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO viewing_history_entries (
                    id, user_id, tmdb_id, prestige_tier, personal_note
                ) VALUES (
                    :id, :user_id, 548, 'Gold', '保持されるメモ'
                )
                """
            ),
            {"id": history_id, "user_id": user_id},
        )

    command.upgrade(config, "head")
    with engine.begin() as connection:
        migrated = connection.execute(
            text(
                """
                SELECT history.film_id, history.tmdb_id, history.personal_note,
                       films.source_key, films.tmdb_id AS film_tmdb_id
                FROM viewing_history_entries AS history
                JOIN films ON films.id = history.film_id
                WHERE history.id = :id
                """
            ),
            {"id": history_id},
        ).mappings().one()
        assert migrated["film_id"] is not None
        assert migrated["tmdb_id"] == 548
        assert migrated["film_tmdb_id"] == 548
        assert migrated["source_key"] == "legacy-tmdb"
        assert migrated["personal_note"] == "保持されるメモ"

    command.downgrade(config, "b3d91f6a2c04")
    with engine.begin() as connection:
        rolled_back = connection.execute(
            text(
                "SELECT tmdb_id, personal_note FROM viewing_history_entries "
                "WHERE id = :id"
            ),
            {"id": history_id},
        ).mappings().one()
        assert rolled_back["tmdb_id"] == 548
        assert rolled_back["personal_note"] == "保持されるメモ"

    command.upgrade(config, "head")
    print("旧tmdb_idデータのアップグレードとロールバック検証に合格しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
