"""Local catalogue import and rights-manifest validation tests."""

from datetime import date
import json

import pytest
from sqlalchemy import select

from app.importing import import_catalog_files
from app.models.film_catalog import FilmCatalog
from app.models.film_data_source import FilmDataSource


def test_import_local_japanese_catalog(db_session, tmp_path):
    source = tmp_path / "source.json"
    films = tmp_path / "films.json"
    source.write_text(
        json.dumps(
            {
                "key": "owned-data",
                "display_name": "権利確認済みデータ",
                "license_name": "社内利用許諾",
                "license_url": None,
                "commercial_use": "許可",
                "redistribution": "禁止",
                "obtained_on": "2026-07-26",
                "has_japanese_metadata": True,
                "update_method": "管理者がローカルファイルを更新",
                "notes": "テスト用",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    films.write_text(
        json.dumps(
            [
                {
                    "external_id": "local-1",
                    "title_ja": "ローカル映画",
                    "original_title": "Local Film",
                    "search_aliases": ["ろーかるえいが"],
                    "synopsis_ja": "権利を確認した説明です。",
                    "release_date": "2026-01-01",
                    "runtime_minutes": 90,
                    "genres": ["ドラマ"],
                    "directors": [],
                    "cast_members": [],
                    "poster_path": "/posters/local-1.webp",
                    "streaming_platforms": ["自前配信"],
                    "streaming_region": "JP",
                    "streaming_updated_at": "2026-07-26T12:00:00+09:00",
                    "recommendation_moods": ["thoughtful"],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert import_catalog_files(db_session, source, films) == 1
    record = db_session.execute(
        select(FilmCatalog).where(FilmCatalog.external_id == "local-1")
    ).scalar_one()
    assert record.title_ja == "ローカル映画"
    assert record.streaming_region == "JP"


def test_remote_poster_url_is_rejected(db_session, tmp_path):
    source = tmp_path / "source.json"
    films = tmp_path / "films.json"
    source.write_text(
        json.dumps(
            {
                "key": "checked-source",
                "display_name": "確認済み",
                "license_name": "許諾済み",
                "license_url": None,
                "commercial_use": "許可",
                "redistribution": "許可",
                "obtained_on": "2026-07-26",
                "has_japanese_metadata": True,
                "update_method": "手動",
                "notes": None,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    films.write_text(
        json.dumps(
            [
                {
                    "external_id": "bad-poster",
                    "title_ja": "不正な画像",
                    "poster_path": "https://example.com/poster.jpg",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="ローカルパス"):
        import_catalog_files(db_session, source, films)


def test_import_replaces_legacy_placeholder_without_changing_local_id(
    db_session, tmp_path
):
    legacy_source = FilmDataSource(
        key="legacy-tmdb",
        display_name="旧ID",
        license_name="識別子のみ",
        commercial_use="識別子のみ",
        redistribution="識別子のみ",
        obtained_on=date(2026, 7, 26),
        has_japanese_metadata=False,
        update_method="手動",
    )
    db_session.add(legacy_source)
    legacy_film = FilmCatalog(
        source_key="legacy-tmdb",
        external_id="999",
        tmdb_id=999,
        normalized_title="tmdb999",
        genres=[],
        directors=[],
        cast_members=[],
        streaming_platforms=[],
        streaming_region="JP",
        recommendation_moods=[],
    )
    db_session.add(legacy_film)
    db_session.commit()
    original_id = legacy_film.id

    source = tmp_path / "source.json"
    films = tmp_path / "films.json"
    source.write_text(
        json.dumps(
            {
                "key": "replacement",
                "display_name": "補完データ",
                "license_name": "確認済み",
                "license_url": None,
                "commercial_use": "許可",
                "redistribution": "禁止",
                "obtained_on": "2026-07-26",
                "has_japanese_metadata": True,
                "update_method": "手動",
                "notes": None,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    films.write_text(
        json.dumps(
            [
                {
                    "external_id": "replacement-999",
                    "tmdb_id": 999,
                    "title_ja": "補完された映画",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    import_catalog_files(db_session, source, films)
    updated = db_session.get(FilmCatalog, original_id)
    assert updated.id == original_id
    assert updated.source_key == "replacement"
    assert updated.title_ja == "補完された映画"
