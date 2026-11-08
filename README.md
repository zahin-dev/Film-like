# Film-like — 2025年8月のMVPを対象とした後日の再構成・参考版

2025年5月〜8月の初期MVPを採用応募で説明するための参考ブランチです。チームの回顧では、3名が約3か月で初期MVPを共同開発しました。2025年8月末までのソースや日付付き一次資料は確認できず、当時の完成範囲は確定できていません。このブランチは、現存する最古のコードで確認できる機能を基に2026年11月に整備したものです。[チームの回顧](docs/DevelopmentProcess.md)

GitHub上のリポジトリ作成日は2026年6月14日です。最古のコミット `70a6e9e`（2026年6月15日）には登録・ログイン、TMDB映画検索・詳細、視聴記録の登録・一覧・削除、感想タグ、評価、メモのコードがあります。APIスキーマが欠けていたため、機能を実行できるようにした2026年7月の修復コミット `20569ae` を基点にしました。[初回コミット](https://github.com/zahin-dev/Film-like/commit/70a6e9e) · [スキーマ修復](https://github.com/zahin-dev/Film-like/commit/20569ae)

## このブランチの機能

- React画面でユーザー登録とログイン、サインアウト。
- 今回追加した簡易画面でTMDB映画検索、視聴記録の登録・一覧・削除、タグとメモの入力。
- FastAPIのSwagger UIで映画詳細や評価付きの登録を含むAPIを操作。PostgreSQLにはユーザー、視聴記録、英語タグ、記録時の映画タイトルとポスターURLを保存。
- 推薦と分析は対象外。現履歴で確認できる実装は2026年7月のMistral推薦と視聴傾向集計です。初回READMEの構想から2025年の稼働は判断できません。[推薦のPR](https://github.com/zahin-dev/Film-like/pull/2) · [分析のPR](https://github.com/zahin-dev/Film-like/pull/3)

2026年7月の日本語UI・ローカル映画カタログ、ローカル推薦、TMDB・Mistral依存の廃止、旧ID・タグの互換移行、追加分析、ポートフォリオ指標・監査の実行スクリプトは対象外です。監査・設計の記録はGit履歴に残っており、現行版の[検証記録](docs/Verification.md)と[移行計画](docs/JapaneseOfflineMigrationPlan.md)もこのブランチで参照できます。これらの記録は現行版に関する資料です。[日本語ローカル化のPR](https://github.com/zahin-dev/Film-like/pull/5)

## ローカルで起動する

Python 3.12、Node.js 24、Docker Composeを用意します。新規の専用PostgreSQLを使用してください。このブランチのAlembicは `e5f8a2b3c491` までです。

リポジトリのルートで実行します。

```sh
docker compose up -d --wait
```

Composeプロジェクトは `film-like-mvp-2025-scope` で、専用ボリュームを使い、DBは `127.0.0.1:55432` で待ち受けます。既存の `DATABASE_URL` がシェルに設定されている場合は、新規DBの接続先に設定し直してください。

`backend` に移動し、Python 3.12の仮想環境を作成・有効化します。`.env.example` を `.env` にコピーし、専用DBのURL、生成した `SECRET_KEY`、有効な `TMDB_READ_ACCESS_TOKEN` を設定します。

```sh
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m seeds.seed_tag
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

別のターミナルで `frontend` に移動します。

```sh
npm ci
npm run dev -- --host 127.0.0.1
```

- 画面は [localhost:5173](http://localhost:5173)、Swagger UIは [localhost:8000/docs](http://localhost:8000/docs)。
- Swagger UIの保護ルートには `POST /auth/login` で受け取ったJWTを `Authorize` に入力します。視聴記録は `GET /films/history`、`POST /films/log`、`DELETE /films/log/{tmdb_id}` を使います。

## 検証

`backend` で `python -m pytest -q --cov=app` を実行します。テストはインメモリSQLiteとTMDBのモックを使用します。`frontend` で `npm run lint` と `npm run build` を実行します。

| 項目 | 結果 |
| --- | --- |
| バックエンド pytest・カバレッジ | Python 3.12.16で79件成功、91%。インメモリSQLite・TMDBモック |
| フロントエンド | Node.js 24で `npm ci`、`npm run lint`、`npm run build` が成功 |
| PostgreSQL | 新規のローカルPostgreSQL 16でAlembic 4件を適用し、`e5f8a2b3c491` と50件のタグ投入を確認 |
| ブラウザ統合 | Reactのビルド、FastAPI、新規PostgreSQLを接続。登録、ログイン失敗・成功、検索、タグ・メモ付き記録、再読込後の記録表示、削除、サインアウトに成功。映画詳細のAPI応答も確認。TMDB応答はモック |
| Docker | `docker compose config --quiet` は成功。Docker DesktopのLinuxデーモンに接続できず、`docker compose up -d --wait` は未完了 |
| 外部TMDB | 有効なトークンでの実通信は未確認 |
| 依存関係監査 | npmが14件（高8件、中6件）を報告。開発依存を除いても高2件が残存 |
