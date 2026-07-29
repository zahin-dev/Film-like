#!/usr/bin/env bash
# バックエンド、監査、フロントエンドをまとめて検証
set -e

echo "バックエンドテストを実行します。"
(
    cd backend
    python -m pytest -q
    python -m pytest --cov=app
)

echo "日本語表示とローカル完結構成を監査します。"
python scripts/check_japanese_public_text.py
python scripts/check_offline_dependencies.py

echo "フロントエンドを検証します。"
(
    cd frontend
    npm ci
    npm run test
    npm run lint
    npm run build
)
