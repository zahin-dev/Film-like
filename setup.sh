#!/usr/bin/env bash
# Film-like 日本語・ローカル完結版の初回セットアップ
set -e

if ! command -v docker >/dev/null 2>&1; then
    echo "Dockerが見つかりません。Docker EngineまたはDocker Desktopをインストールしてください。"
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Docker Compose v2が見つかりません。"
    exit 1
fi

echo "PostgreSQL、バックエンド、フロントエンドをビルドして起動します。"
docker compose up -d --build

echo "Film-likeを起動しました。"
echo "フロントエンド: http://localhost:5173"
echo "バックエンド:   http://localhost:8000"
echo "APIドキュメント: http://localhost:8000/docs"
