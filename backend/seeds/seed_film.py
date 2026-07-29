#!/usr/bin/env python3
"""Seed the small, rights-conscious Japanese demo catalogue."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.importing import import_catalog_files


def seed() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    db = SessionLocal()
    try:
        count = import_catalog_files(
            db,
            data_dir / "demo_source.json",
            data_dir / "demo_films.json",
        )
        print(f"{count}件の日本語デモ映画を登録しました。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
