"""Local catalogue, Japanese metadata, tags, and viewing-history tests."""

from sqlalchemy import select

from app.models.film_catalog import FilmCatalog
from app.models.film_data_source import FilmDataSource


def _film(db_session, external_id):
    return db_session.execute(
        select(FilmCatalog).where(FilmCatalog.external_id == external_id)
    ).scalar_one()


def test_search_by_japanese_title_prefers_japanese_metadata(client):
    response = client.get("/films/search", params={"query": "羅生門"})
    assert response.status_code == 200
    body = response.json()
    assert body[0]["title"] == "羅生門"
    assert body[0]["synopsis"].endswith("人間ドラマです。")
    assert body[0]["streaming_region"] == "JP"


def test_original_title_search_still_returns_japanese_title(client):
    response = client.get("/films/search", params={"query": "Rashomon"})
    assert response.status_code == 200
    assert response.json()[0]["title"] == "羅生門"


def test_kana_alias_search_is_available(client):
    response = client.get("/films/search", params={"query": "らしょうもん"})
    assert response.status_code == 200
    assert response.json()[0]["title"] == "羅生門"


def test_empty_local_search_is_controlled(client):
    response = client.get("/films/search", params={"query": "存在しない作品"})
    assert response.status_code == 200
    assert response.json() == []


def test_film_detail_uses_local_id_and_japanese_gaps(
    client, auth_headers, db_session
):
    source = db_session.get(FilmDataSource, "demo-ja")
    missing = FilmCatalog(
        source_key=source.key,
        external_id="missing-ja",
        title_ja=None,
        original_title="Untranslated Proper Title",
        synopsis_ja=None,
        genres=[],
        directors=[],
        cast_members=[],
        streaming_platforms=[],
        streaming_region="JP",
        normalized_title="untranslatedpropertitle",
        recommendation_moods=[],
    )
    db_session.add(missing)
    db_session.commit()

    response = client.get(f"/films/{missing.id}", headers=auth_headers)
    assert response.status_code == 200
    film = response.json()["film"]
    assert film["title"] == "日本語タイトル情報はありません"
    assert film["original_title"] == "Untranslated Proper Title"
    assert film["synopsis"] == "日本語のあらすじ情報はありません"
    assert film["director"] == "監督情報はありません"
    assert film["cast"] == []
    assert film["streaming_platforms"] == []


def test_missing_film_returns_japanese_404(client, auth_headers):
    response = client.get("/films/999999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == (
        "指定された映画はローカルカタログにありません。"
    )


def test_tags_have_stable_keys_and_japanese_text(client):
    response = client.get("/tags")
    assert response.status_code == 200
    tag = response.json()[0]
    assert tag["key"] == "feel-good"
    assert tag["name"] == "元気をもらえる"
    assert "作品" in tag["description"]


def test_log_and_read_history_with_local_film_id(
    client, auth_headers, db_session
):
    film = _film(db_session, "rashomon-1950")
    tag_id = client.get("/tags").json()[0]["id"]
    created = client.post(
        "/films/log",
        json={
            "film_id": film.id,
            "tag_ids": [tag_id],
            "prestige_tier": "Gold",
            "personal_note": "証言の違いが印象的でした。",
        },
        headers=auth_headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["film_id"] == film.id
    assert body["tmdb_id"] == 548
    assert body["title"] == "羅生門"
    assert body["prestige_tier_label"] == "かなり良い"
    assert body["tags"][0]["name"] == "元気をもらえる"

    history = client.get("/films/history", headers=auth_headers)
    assert history.status_code == 200
    assert history.json()[0]["personal_note"] == "証言の違いが印象的でした。"


def test_legacy_tmdb_id_payload_is_migrated_to_local_film_id(
    client, auth_headers, db_session
):
    film = _film(db_session, "rashomon-1950")
    response = client.post(
        "/films/log",
        json={"tmdb_id": 548},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["film_id"] == film.id
    assert response.json()["tmdb_id"] == 548


def test_duplicate_history_returns_japanese_conflict(
    client, auth_headers, db_session
):
    film = _film(db_session, "rashomon-1950")
    assert client.post(
        "/films/log", json={"film_id": film.id}, headers=auth_headers
    ).status_code == 201
    duplicate = client.post(
        "/films/log", json={"film_id": film.id}, headers=auth_headers
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == (
        "この映画はすでに視聴記録へ追加されています。"
    )


def test_invalid_tag_is_rejected_in_japanese(client, auth_headers, db_session):
    film = _film(db_session, "rashomon-1950")
    response = client.post(
        "/films/log",
        json={"film_id": film.id, "tag_ids": [999999]},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"] == (
        "選択されたタグの一部が見つかりません。"
    )


def test_remove_history_by_local_id(client, auth_headers, db_session):
    film = _film(db_session, "rashomon-1950")
    client.post("/films/log", json={"film_id": film.id}, headers=auth_headers)
    removed = client.delete(f"/films/log/{film.id}", headers=auth_headers)
    assert removed.status_code == 200
    assert removed.json()["detail"] == "視聴記録から削除しました。"
    assert client.get("/films/history", headers=auth_headers).json() == []


def test_local_catalog_does_not_need_poster_or_streaming_api(
    client, auth_headers, db_session
):
    film = _film(db_session, "tokyo-story-1953")
    body = client.get(f"/films/{film.id}", headers=auth_headers).json()["film"]
    assert body["poster_url"] is None
    assert body["streaming_platforms"] == []
    assert body["streaming_region"] == "JP"
    assert body["streaming_updated_at"] is None
