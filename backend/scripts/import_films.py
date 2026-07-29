#!/usr/bin/env python3
"""Import a local JSON catalogue after validating its licence manifest."""

import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.importing import import_catalog_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="権利情報を確認済みのローカル映画データを取り込みます。"
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--films", required=True, type=Path)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        count = import_catalog_files(db, args.source, args.films)
        print(f"{count}件の映画データを取り込みました。")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
