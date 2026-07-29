# 主要シーケンス

## 映画検索と詳細

```mermaid
sequenceDiagram
    actor User as 利用者
    participant UI as React
    participant API as FastAPI
    participant Provider as LocalFilmCatalogProvider
    participant DB as PostgreSQL

    User->>UI: 日本語タイトルを入力
    UI->>API: GET /films/search?query=羅生門
    API->>Provider: search(db, query)
    Provider->>DB: 正規化タイトルを部分一致検索
    DB-->>Provider: ローカル映画行
    Provider-->>API: 日本語優先の映画
    API-->>UI: 200 日本語JSON
    User->>UI: 詳細を選択
    UI->>API: GET /films/{film_id}
    API->>DB: 映画と視聴状態
    DB-->>API: ローカルデータ
    API-->>UI: 詳細または日本語の欠損表示
```

外部映画APIや翻訳APIへの呼び出しはありません。

## 視聴記録

```mermaid
sequenceDiagram
    actor User as 利用者
    participant UI as React
    participant API as FastAPI
    participant DB as PostgreSQL

    User->>UI: 評価・タグ・メモを入力
    UI->>API: POST /films/log (film_id)
    API->>DB: 映画IDとタグIDを検証
    alt すでに記録済み
        API-->>UI: 409 日本語エラー
    else 登録可能
        API->>DB: 履歴とタグ関連を保存
        DB-->>API: 保存済み履歴
        API-->>UI: 201 日本語タグ・評価ラベル
    end
```

旧クライアントが`tmdb_id`を送った場合は、ローカルカタログで照合して同じ`film_id`へ保存します。

## ローカル推薦

```mermaid
sequenceDiagram
    actor User as 利用者
    participant UI as React
    participant API as FastAPI
    participant Engine as ローカル推薦
    participant DB as PostgreSQL

    User->>UI: 今の気分を選択
    UI->>API: POST /recommendations
    API->>Engine: mood, limit, user
    Engine->>DB: 視聴履歴・タグ・全映画
    DB-->>Engine: ローカルデータ
    Engine->>Engine: 視聴済み除外
    Engine->>Engine: 気分・ジャンル・タグ・最近傾向を採点
    Engine->>Engine: 決定的に整列・重複除外
    Engine-->>API: 日本語理由と候補不足状態
    API-->>UI: 200
```

クラウドLLM、乱数、外部照合は使いません。

## データインポート

```mermaid
sequenceDiagram
    actor Admin as データ管理者
    participant CLI as import_films.py
    participant Validator as Pydantic
    participant DB as PostgreSQL

    Admin->>CLI: 出典マニフェスト + 映画JSON
    CLI->>Validator: 権利情報・JP地域・ローカル画像パスを検証
    alt 検証失敗
        Validator-->>Admin: 日本語エラー
    else 検証成功
        CLI->>DB: 出典を更新
        CLI->>DB: source_key + external_idで映画を更新
        DB-->>Admin: 取り込み件数
    end
```

## チームと主担当

Film-likeは3名で共同開発・保守しています。Reactフローは`aoi-dev`、FastAPIとローカル業務ロジックは`zahin-dev`、DockerとCIは`sakamoto-dev`が主担当です。主担当は単独作者を意味せず、3名がレビュー、デバッグ、テスト、設計、文書化を横断的に行います。`zahin-dev`アカウントは管理上のホスト兼公開連絡先であり、単独所有を意味しません。
