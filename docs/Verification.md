# 検証記録

検証日: 2026-07-26
ブランチ: `feat/japanese-offline-version`
環境: Windows、Python 3.12.13、Node.js 20系、Docker Desktop

## 確認できた結果

### バックエンド

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest -q
```

結果:

```text
38 passed
```

外部ソケット接続を禁止する自動フィクスチャの下で実行しています。対象には次を含みます。

- APIキーなしの起動
- 日本語OpenAPIメタデータ
- 日本語タイトル、原題、読み別名による検索
- 日本語タイトル優先と日本語の欠損表示
- 日本語タグ、認証・404・409・422エラー
- ローカル`film_id`による視聴記録
- 旧`tmdb_id`入力からローカル映画への照合
- 評価、タグ、メモ、日時の保持
- 視聴済み映画と重複の推薦除外
- 気分、履歴タグ、最近のジャンルの反映
- 日本語の推薦理由
- 同じ入力に対する決定的な推薦順
- 候補不足と候補なしの制御
- 出典マニフェスト付きローカルインポート
- 外部ポスターURLの拒否
- 旧照合用映画を補完するときのローカルID保持

```powershell
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term
```

結果:

```text
38 passed
TOTAL 822 statements, 51 missing, 94%
```

### フロントエンド

```powershell
cd frontend
npm ci
npm run test
npm run lint
npm run build
```

結果:

- `npm ci`: 成功、180パッケージをクリーンインストール
- 日本語UI契約テスト: 成功
- ESLint: 成功、エラーなし
- Vite Production build: 成功、92モジュールを変換
- 生成JavaScript: 約307.81 kB、gzip約99.02 kB

静的UI契約は`lang="ja"`、日本語ローディング・空状態・エラー、`ja-JP`と`Asia/Tokyo`、日本語検索、ローカルID送信、日本語アクセシビリティラベル、推薦画面に旧クラウドサービス文言がないことを確認します。

### 公開文と外部依存の監査

```powershell
python scripts/check_japanese_public_text.py
python scripts/check_offline_dependencies.py
```

結果:

```text
日本語公開文監査に合格しました。
ローカル完結構成の監査に合格しました。クラウドAPIキーは不要です。
```

外部依存監査は、実行時設定、`.env.example`、Compose、CI、`backend/app`を対象に、クラウドAPIキー名、既知のクラウド接続先、外部HTTPクライアント、外部アダプター、Dockerイメージへの`.env`混入を検査します。

### Docker Compose構文

```powershell
docker compose config --quiet
```

結果: 成功。

PostgreSQL、バックエンド、フロントエンド、`ja-JP`、`JP`、`Asia/Tokyo`、ヘルスチェック、既存`cinemood`ボリュームとの接続互換が解決されました。

Dockerクライアントのユーザー設定ファイルについてアクセス警告が出ましたが、Compose定義の構文検証は終了コード0です。

### 差分整合性

```powershell
git diff --check
```

結果: 空白エラーなし。WindowsのGit設定によるLFからCRLFへの変換予告だけが表示されました。

## 環境側の理由で完了していない確認

### `docker compose up -d`

次を実行しました。

```powershell
docker compose up -d --build
docker compose up -d
```

どちらもアプリケーションコードへ到達する前にDocker Engineで停止しました。

確認できたDocker Desktopログ:

```text
preparing environment: provisioning data: detecting disk:
no sd* disk in /sys/block with wwid ending by ...: file does not exist
```

Docker専用WSL2ディストリビューションは`Running`でしたが、Engineの`_ping`がタイムアウトし、Composeは500またはタイムアウトになりました。Docker Desktop起動、Engine再確認、`docker-desktop`ディストリビューションの再起動まで試しましたが復旧しませんでした。

Docker Desktopのデータディスクを初期化すれば復旧する可能性がありますが、既存イメージ、コンテナ、ボリュームを失うおそれがあるため実行していません。したがって、この環境では次は未確認です。

- コンテナイメージの実ビルド
- PostgreSQL上のAlembic実行
- Composeサービスのヘルス状態
- コンテナ経由のエンドツーエンド操作

CIには専用PostgreSQLサービスと`backend/scripts/verify_migrations.py`を追加しています。このスクリプトは旧`tmdb_id`履歴を作成し、アップグレード後に`film_id`、評価、メモ、旧IDが保持されること、ダウングレード後にも旧データが保持されることを検証します。ローカルDocker Engineが復旧するまで、PostgreSQL上での実行結果は未確認です。

### ブラウザ画像確認

ViteのProduction previewは起動できましたが、アプリ内ブラウザ接続基盤がWindowsの`AppData`読み取り権限で停止しました。このため実画面キャプチャによる文字切れ確認は未完了です。

CSSには日本語システムフォント、禁則処理、折返しを設定し、UI契約テスト、Lint、Production buildは成功しています。実ブラウザでのデスクトップ・モバイル目視確認は残っています。

## 再確認手順

Docker Desktopのデータディスクを既存データを保護した方法で修復したあと、次を実行します。

```powershell
docker compose up -d --build
docker compose ps
docker compose logs backend
```

バックエンドがhealthyになったら、`http://localhost:8000/docs`と`http://localhost:5173`を開き、登録、検索、詳細、記録、分析、推薦、削除を確認します。
