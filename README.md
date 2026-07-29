# Film-like 日本語・ローカル完結版

Film-likeは、映画の検索、詳細確認、視聴記録、感想タグの分析、今の気分に合う推薦を行うセルフホスト型の映画日記です。主要機能はPostgreSQLのローカル映画カタログだけで動作し、クラウド映画API、クラウドLLM、翻訳APIのキーを必要としません。

このリポジトリはMVPです。公開インターネットサービスとしての本番運用、リアルタイム配信情報、大規模な映画データセットを提供するものではありません。

## 主な機能

- 日本語タイトルと原題によるローカル映画検索
- 日本語タイトル、あらすじ、ジャンル、監督、出演者、上映時間の表示
- 評価、感想タグ、個人メモを含む視聴記録
- 選択したタグだけを使う説明可能な視聴傾向の集計
- 気分、過去のタグ、最近のジャンル、視聴済み除外を考慮する推薦
- 日本向けの`ja-JP`、`JP`、`Asia/Tokyo`設定
- 出典・ライセンス情報を伴うローカルJSONインポート
- 旧`tmdb_id`を失わずにローカル`film_id`へ移行するAlembicマイグレーション

## このリポジトリでいう「完全無料版」

主要機能は次のものに依存しません。

- クレジットカード登録
- 期間限定の無料枠や無料クレジット
- 月間トークン数やリクエスト数
- 従量課金のクラウドAPI
- 有料プランへの移行
- APIキー

保証できる範囲は、自分のPCまたは自前サーバーでPostgreSQL、バックエンド、フロントエンドを動かすセルフホスト構成です。PC、ストレージ、通信回線、電気、ドメイン、公開サーバーの費用は含みません。Render、Vercel、Herokuなどの無料枠を恒久運用の前提にはしていません。

## 構成

```mermaid
flowchart LR
    User["日本の利用者"]
    Frontend["Reactフロントエンド<br/>主担当: aoi-dev"]
    Backend["FastAPIバックエンド<br/>主担当: zahin-dev"]
    DB[("PostgreSQL<br/>映画・履歴・タグ")]
    Infra["Docker / CI<br/>主担当: sakamoto-dev"]

    User --> Frontend
    Frontend --> Backend
    Backend --> DB
    Infra -. 構築・検証 .-> Frontend
    Infra -. 構築・検証 .-> Backend
    Infra -. 構築・検証 .-> DB
```

すべての矢印はセルフホスト環境内で完結します。映画検索や推薦のための外向きHTTP通信はありません。

## ローカル映画データ

映画は`films`テーブルへ保存されます。

- ローカル映画ID
- 出典キーと出典側ID
- 移行照合用の任意`tmdb_id`
- 日本語タイトル、原題、日本語あらすじ
- 公開日、上映時間、ジャンル
- 監督、出演者
- 権利確認済みローカルポスターへのパス
- 日本地域の配信サービス情報と情報更新日
- 検索用の正規化タイトル
- 推薦用の安定した気分コード
- 作成日時、更新日時

検索文字列はUnicode NFKC、大小文字、記号、空白を正規化します。日本語タイトルがある場合は必ず日本語タイトルを表示します。日本語情報がない場合は「日本語タイトル情報はありません」「日本語のあらすじ情報はありません」などの欠損表示を使います。人名はデータ提供元が明示した表記をそのまま使い、勝手な翻訳やカタカナ化は行いません。

### デモデータ

`backend/data/demo_films.json`には12件の小規模な日本語デモデータがあります。

- 提供元: Film-like日本語デモカタログ
- 取得日: 2026-07-26
- 内容: 題名、公開年などの事実情報と、このデモ用に新規作成した短い説明
- ポスター: 収録なし
- 日本語情報: あり
- 商用利用・再配布: リポジトリ自体に明示ライセンスがない場合、許諾済みとはみなせないため個別確認が必要

第三者サイトから転載したあらすじや画像、大量に取得した映画データは含みません。詳細は[映画データの取り込み手順](docs/FilmDataImport.md)を参照してください。

## 推薦ロジック

`POST /recommendations`は外部AIを呼び出しません。同じ入力と同じDB状態では同じ順序を返します。

1. ローカルカタログから視聴済みの`film_id`を除外
2. 選んだ気分と映画の気分コードが一致すれば加点
3. 気分とジャンルの対応が一致すれば加点
4. 過去によく選んだ感想タグと気分の対応を加点
5. 直近5件でよく観たジャンルとの重なりを加点
6. 点数、タイトル、公開日、ローカルIDで決定的に整列
7. 候補不足時は未視聴作品で補完し、その事実を日本語で表示

推薦理由は日本語テンプレートで生成します。ランダム抽選は行いません。カタログが空、または全作品を視聴済みの場合も、500系エラーにはせず制御された空結果を返します。

## 必要な環境

- Docker EngineまたはDocker Desktop
- Docker Compose v2

手動開発を行う場合はPython 3.12系、Node.js 20系、PostgreSQL 16も使用します。

## Docker Composeで起動

```bash
docker compose config
docker compose up -d --build
```

起動後:

- フロントエンド: `http://localhost:5173`
- バックエンド: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

バックエンド起動時にAlembicマイグレーション、日本語タグ、小規模デモカタログを冪等に投入します。

停止:

```bash
docker compose down
```

DBボリュームを削除しない限り、アカウント、視聴履歴、タグ、評価、メモ、日時は保持されます。

## 環境変数

バックエンドの例は`backend/.env.example`です。

```dotenv
DATABASE_URL=postgresql://cinemood:cinemood@localhost:5432/cinemood
SECRET_KEY=change_this_local_secret
RECOMMENDATION_ENGINE=local
APP_LOCALE=ja-JP
APP_REGION=JP
APP_TIMEZONE=Asia/Tokyo
```

映画API、クラウドLLM、翻訳APIのキーは設定しません。

## データのインポート

権利情報を記述した出典マニフェストと映画JSONを用意します。

```bash
cd backend
python scripts/import_films.py \
  --source path/to/source.json \
  --films path/to/films.json
```

インポーターは次を検証します。

- 出典、ライセンス、商用利用、再配布、取得日、更新方法
- 日本地域`JP`
- 対応する気分コード
- ポスターが`/posters/`以下のローカルパスであること
- 検索に使えるタイトルまたは別名があること

外部URLのポスターは拒否します。権利を確認した画像だけを`backend/data/posters`へ置いてください。形式仕様と確認手順は[FilmDataImport.md](docs/FilmDataImport.md)にあります。

## マイグレーション

```bash
cd backend
alembic upgrade head
python seeds/seed_tag.py
python seeds/seed_film.py
```

`c7d4e8f1a2b3`は次を行います。

- `film_data_sources`と`films`を追加
- 既存タグへ安定した`key`、日本語表示名、日本語説明を追加
- 既存の各`tmdb_id`に対して照合用のローカル映画行を作成
- 視聴記録へ`film_id`外部キーを追加して既存データを関連付け
- `tmdb_id`は削除せず任意列として保持

ロールバック時、ローカル専用映画の視聴記録が存在するとマイグレーションは停止します。これは映画識別情報の無言な消失を防ぐためです。対象データをJSONへ退避してから実行してください。

## テストと監査

バックエンド:

```bash
cd backend
python -m pytest -q
python -m pytest --cov=app
```

フロントエンド:

```bash
cd frontend
npm ci
npm run test
npm run lint
npm run build
```

監査:

```bash
python scripts/check_japanese_public_text.py
python scripts/check_offline_dependencies.py
```

テストでは実ソケット接続を禁止しています。CIはPostgreSQL上で旧`tmdb_id`データのアップグレードとロールバックも検証します。

## APIの主な経路

| メソッド | パス | 内容 | 認証 |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | アカウント登録 | 不要 |
| `POST` | `/auth/login` | ログイン | 不要 |
| `GET` | `/films/search?query=` | ローカル映画検索 | 不要 |
| `GET` | `/films/{film_id}` | 映画詳細と記録状態 | 必要 |
| `GET` | `/films/by-tmdb/{tmdb_id}` | 旧外部IDの照合 | 不要 |
| `POST` | `/films/log` | 視聴記録を追加 | 必要 |
| `DELETE` | `/films/log/{film_id}` | 視聴記録を削除 | 必要 |
| `GET` | `/films/history` | 視聴履歴 | 必要 |
| `GET` | `/tags` | 日本語タグ | 不要 |
| `GET` | `/insights` | 視聴傾向 | 必要 |
| `POST` | `/recommendations` | ローカル推薦 | 必要 |

## 任意のローカルLLM

現在の実装にはOllamaなどのローカルLLMアダプターを含めていません。モデルのライセンス、必要メモリー、出力検証を一律に保証できないためです。推薦はローカルLLMなしで動作します。

将来追加する場合も、クラウドへ送信しないこと、モデルを自動必須ダウンロードしないこと、出力をスキーマ検証すること、日本語以外の理由を返さないこと、現在の決定的推薦を必須フォールバックとして残すことが条件です。

## 開発メンバーと主担当

| 分野 | GitHubユーザー | 主担当内容 |
| --- | --- | --- |
| バックエンド | `zahin-dev` | FastAPI、API設計、認証、DB、外部連携、推薦処理 |
| フロントエンド | `aoi-dev` | React、画面、フォーム、操作、API接続 |
| インフラ | `sakamoto-dev` | Docker、サーバー、デプロイ、CI/CD、環境構築 |

これは主担当領域を示すもので、排他的な単独作者や貢献割合を示すものではありません。3名は実装、レビュー、デバッグ、テスト、設計、文書化を役割横断で行います。リポジトリが`zahin-dev`アカウント配下にあることも、プロジェクト全体の単独所有や全ファイルの単独執筆を意味しません。過去のGit作者情報は変更していません。

詳しくは[CONTRIBUTORS.md](CONTRIBUTORS.md)と[Ownership.md](docs/Ownership.md)を参照してください。

## 既知の制限

- 同梱カタログは動作確認用の12件だけです。
- 配信サービス情報はリアルタイムではありません。登録した更新日がある場合だけ表示します。
- デモにはポスター画像がありません。
- 日本語タイトルや説明がないインポートデータは欠損表示になります。
- 表記ゆれ検索はNFKC、空白、記号、大小文字の正規化までです。高度な読み推定は行いません。
- プロフィール編集、共有、決済、リアルタイム配信検索は未実装です。
- インターネット公開時のTLS、バックアップ、監視、シークレット管理は利用者が構成する必要があります。

## 関連文書

- [日本語・ローカル完結版の調査と移行計画](docs/JapaneseOfflineMigrationPlan.md)
- [担当領域](docs/Ownership.md)
- [映画データの取り込み](docs/FilmDataImport.md)
- [アーキテクチャ](docs/diagrams/Architecture.md)
- [ER図](docs/diagrams/ERDiagram.md)
- [クラス構成](docs/diagrams/ClassDiagram.md)
- [主要シーケンス](docs/diagrams/SequenceDiagrams.md)
- [検証記録](docs/Verification.md)
