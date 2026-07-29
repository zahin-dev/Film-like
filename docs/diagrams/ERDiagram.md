# ER図

```mermaid
erDiagram
    USERS ||--o{ VIEWING_HISTORY_ENTRIES : "記録する"
    FILM_DATA_SOURCES ||--o{ FILMS : "提供する"
    FILMS ||--o{ VIEWING_HISTORY_ENTRIES : "参照される"
    VIEWING_HISTORY_ENTRIES ||--o{ VIEWING_HISTORY_TAGS : "持つ"
    TAGS ||--o{ VIEWING_HISTORY_TAGS : "選択される"

    USERS {
        uuid id PK
        string first_name
        string last_name
        string username
        string email UK
        string hashed_password
        boolean is_admin
        integer age
        datetime created_at
        datetime updated_at
    }

    FILM_DATA_SOURCES {
        string key PK
        string display_name
        string license_name
        string commercial_use
        string redistribution
        date obtained_on
        boolean has_japanese_metadata
        text update_method
    }

    FILMS {
        integer id PK
        string source_key FK
        string external_id
        integer tmdb_id UK "任意・移行照合用"
        string title_ja
        string original_title
        text synopsis_ja
        date release_date
        integer runtime_minutes
        json genres
        json directors
        json cast_members
        string poster_path
        json streaming_platforms
        string streaming_region
        datetime streaming_updated_at
        string normalized_title
        json recommendation_moods
        datetime created_at
        datetime updated_at
    }

    VIEWING_HISTORY_ENTRIES {
        uuid id PK
        uuid user_id FK
        integer film_id FK
        integer tmdb_id "任意・旧データ保持"
        enum prestige_tier
        text personal_note
        datetime created_at
        datetime updated_at
    }

    TAGS {
        integer id PK
        string key UK
        string name UK "旧値"
        string description "旧値"
        string display_name_ja
        string description_ja
    }

    VIEWING_HISTORY_TAGS {
        uuid viewing_history_entry_id PK,FK
        integer tag_id PK,FK
    }
```

`film_id`が現在の映画識別子です。`tmdb_id`は既存履歴の照合と将来の移行のために保持しますが、映画検索や詳細表示の必須値ではありません。

評価Enumの英語値は既存データ互換の内部値です。APIは`prestige_tier_label`で日本語表示を追加します。

## チーム帰属

このスキーマは3名で共同開発・保守するFilm-likeの現行構成です。バックエンドは`zahin-dev`、フロントエンドは`aoi-dev`、インフラは`sakamoto-dev`が主担当ですが、主担当は排他的な作者や貢献割合を意味しません。`zahin-dev`アカウントでのリポジトリ管理も単独所有を意味しません。
