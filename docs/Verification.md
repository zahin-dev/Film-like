# 検証記録

検証日: 2026-07-29

ブランチ: `feat/japanese-offline-version`

環境: Windows、Python 3.12.13、ローカルNode.js 24.15.0、Docker Desktop

CI環境: GitHub Actions、Node.js 20

## バックエンド

### 自動テストとカバレッジ

```powershell
Push-Location backend
.\venv\Scripts\python.exe -m pytest -q
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term
Pop-Location
```

実測結果:

- pytest: `38 passed`
- カバレッジ: `94%`

外部ソケット接続を禁止する自動フィクスチャの下で、認証、日本語映画検索、映画詳細、評価・タグ・メモ付き視聴記録、分析、ローカル推薦、旧データ照合、ローカルインポートを確認しました。

### 日本語公開文とローカル完結構成

```powershell
.\backend\venv\Scripts\python.exe scripts/check_japanese_public_text.py
.\backend\venv\Scripts\python.exe scripts/check_offline_dependencies.py
```

実測結果:

- 日本語公開文監査: 合格
- ローカル完結構成監査: 合格
- クラウドAPIキー: 不要

### OpenAPIと地域設定

OpenAPIの分類は次の6種類であることを確認しました。

- 認証
- 映画
- タグ
- 分析
- 推薦
- システム

`GET /`は「システム」分類です。地域設定は次の値を確認しました。

- ロケール: `ja-JP`
- 地域: `JP`
- タイムゾーン: `Asia/Tokyo`

## フロントエンド

```powershell
Push-Location frontend
npm run test
npm run lint
npm run build
Pop-Location
```

実測結果:

- 日本語UI契約テスト: 成功
- ESLint: 成功、エラーなし
- Vite Production build: 成功
- 変換モジュール数: 92
- 生成JavaScript: 約307.81 kB、gzip約99.02 kB

### 依存関係の追加監査

2026-07-29に、`--force`を付けずに次を実行しました。

```powershell
Push-Location frontend
npm audit fix
npm audit
npm ls @react-router/dev @vitejs/plugin-rsc
Pop-Location
```

依存更新結果:

| パッケージ | 更新前 | 更新後 |
| --- | --- | --- |
| `axios` | 1.16.1 | 1.18.1 |
| `brace-expansion` | 5.0.6 | 5.0.8 |
| `react-router` | 7.15.1 | 7.18.2 |
| `react-router-dom` | 7.15.1 | 7.18.2 |

`axios`と`brace-expansion`に対する既知の警告は、この更新によって解消しました。

#### npm auditに残る警告

`npm audit`には現在もhigh 2件が残っています。いずれも`GHSA-qwww-vcr4-c8h2`に由来するReact Router RSC Modeの警告です。

`npm audit fix --force`は破壊的変更を提示するため実施していません。通常の`npm audit fix`のみを適用し、残存する2件の警告を明記しています。

#### 本アプリでは非該当と判断した根拠

本アプリはReact Server Components（RSC）を使用していません。フロントエンドを対象に次の実装参照を検索し、すべて0件であることを確認しました。

```powershell
git grep -n -E 'unstable_reactRouterRSC|@vitejs/plugin-rsc|matchRSCServerRequest|entry\.rsc|use server' -- frontend
```

検索対象:

- `unstable_reactRouterRSC`
- `@vitejs/plugin-rsc`
- `matchRSCServerRequest`
- `entry.rsc`
- `use server`

また、`npm ls @react-router/dev @vitejs/plugin-rsc`の結果は`(empty)`であり、RSC用パッケージは依存ツリーに含まれていません。以上から、残存high 2件は監査上の警告として記録を維持しつつ、現在の本アプリの実行経路には該当しないと判断しました。

#### 依存更新後の再検証

依存更新後に次を再実行し、すべて成功しました。

- `npm run test`
- `npm run lint`
- `npm run build`
- 日本語公開文監査
- ローカル完結構成監査
- `git diff --check`
- Docker Compose再ビルド

Compose再ビルド後は`db`、`backend`、`frontend`のすべてがhealthyで、frontendのHTTP応答は200でした。

### 配色変更

UI全体を次の「霞んだ緑」パレットへ統一しました。

- forest: `#04202C`
- evergreen: `#304040`
- pine: `#5B7065`
- fog: `#C9D1C8`

通常UIから旧オレンジ、青、金のアクセントを除去し、赤系はエラー、削除、ログアウトなどのdanger用途に限定して維持しています。ファビコンもforestとfogを使ったFilm-like配色へ変更しました。

## Docker Compose

```powershell
docker compose up -d --build
docker compose ps
```

実測結果:

- `docker compose up -d --build`: 成功
- `db`: healthy
- `backend`: healthy
- `frontend`: healthy
- backend HTTP応答: 200
- frontend HTTP応答: 200

フロントエンドのhealthcheck先は、コンテナ内での名前解決差異を避けるため、`http://localhost/`から`http://127.0.0.1/`へ修正しました。

## PostgreSQLとマイグレーション

実際のCompose上のPostgreSQLで次を確認しました。

| 確認項目 | 実測結果 |
| --- | ---: |
| Alembic head | `c7d4e8f1a2b3` |
| 日本語タグ | 50件 |
| 日本語デモ映画 | 12件 |
| `legacy-tmdb`映画 | 5件 |
| 映画総数 | 17件 |
| 既存視聴履歴 | 5件 |
| `film_id`設定済みの既存視聴履歴 | 5件 |
| `missing_film_id` | 0件 |

既存視聴履歴5件すべてにローカル`film_id`が設定され、移行後に欠損がないことを確認しました。

## API検索

同じ作品を異なる表記で検索し、すべて成功することを確認しました。

| 検索語 | 結果 |
| --- | --- |
| `羅生門` | 成功 |
| `らしょうもん` | 成功 |
| `Rashomon` | 成功 |

日本語タイトル、読み別名、原題の各検索経路が機能しています。

## ブラウザ操作

Codex内蔵ブラウザからCompose上のフロントエンドを操作し、次を確認しました。

- 新規登録
- ログイン
- 日本語映画検索
- 映画詳細
- 評価、タグ、メモ付きの視聴記録
- 視聴履歴への反映
- 分析への反映
- おすすめの取得
- 視聴記録の削除
- プロフィール
- ログアウト
- Compose再起動後のデータ永続化

## 表示確認

次のビューポートで目視確認しました。

| ビューポート | 結果 |
| --- | --- |
| 1440 × 900 | 問題なし |
| 768 × 1024 | 問題なし |
| 390 × 844 | 問題なし |
| 320 × 844 | 問題なし |

確認結果:

- ページ全体の横スクロールなし
- 文字重なりなし
- ボタン重なりなし
- 320px幅でナビゲーション4項目が画面内に収まる
- ブラウザコンソールの警告・エラー: 0件

## 過去のDocker Desktop障害

過去の検証では、Docker Desktopのデータディスク検出時に次のエラーが発生しました。

```text
preparing environment: provisioning data: detecting disk:
no sd* disk in /sys/block with wwid ending by ...: file does not exist
```

この障害は履歴として残しますが、2026-07-29の再検証では再発しませんでした。同日の再検証では、Composeのビルドと起動、3サービスのhealthy状態、バックエンドとフロントエンドのHTTP 200、ブラウザからの実操作、Compose再起動後のデータ永続化まで確認できています。現在の検証を妨げる環境ブロッカーではありません。

## 未確認事項と検証範囲

未確認事項:

- Chrome、Firefox、Safariの実機横断確認
- OS強制ハイコントラストモード

ブラウザ確認はCodex内蔵ブラウザで実施しました。

## 差分整合性

```powershell
git diff --check
```

結果: 空白エラーなし。WindowsのGit設定によるLFからCRLFへの変換予告のみです。
