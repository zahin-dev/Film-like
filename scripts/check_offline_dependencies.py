#!/usr/bin/env python3
"""Reject cloud API credentials and outbound clients from active runtime paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "backend" / "app" / "config.py",
    ROOT / "backend" / ".env.example",
    ROOT / "docker-compose.yml",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / "backend" / ".dockerignore",
    ROOT / "frontend" / ".dockerignore",
]
FILES.extend((ROOT / "backend" / "app").rglob("*.py"))

FORBIDDEN = {
    "TMDB_READ_ACCESS_TOKEN": "クラウド映画APIトークン",
    "MISTRAL_API_KEY": "クラウドLLMキー",
    "OPENAI_API_KEY": "クラウドLLMキー",
    "GEMINI_API_KEY": "クラウドLLMキー",
    "ANTHROPIC_API_KEY": "クラウドLLMキー",
    "GROQ_API_KEY": "クラウドLLMキー",
    "api.themoviedb.org": "TMDB HTTP接続先",
    "api.mistral.ai": "Mistral HTTP接続先",
    "api.openai.com": "OpenAI HTTP接続先",
    "httpx.AsyncClient(": "アプリケーションの外部HTTPクライアント",
    "requests.get(": "アプリケーションの外部HTTPクライアント",
    "requests.post(": "アプリケーションの外部HTTPクライアント",
}


def main() -> int:
    failures: list[str] = []
    for path in sorted(set(FILES)):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token, description in FORBIDDEN.items():
            if token in text:
                relative = path.relative_to(ROOT).as_posix()
                failures.append(f"{relative}: {description} ({token})")

    external_dir = ROOT / "backend" / "app" / "external"
    unexpected = [
        path for path in external_dir.glob("*.py")
        if path.name != "__init__.py"
    ]
    failures.extend(
        f"{path.relative_to(ROOT).as_posix()}: 外部クラウドアダプターが残っています"
        for path in unexpected
    )
    for relative in ("backend/.dockerignore", "frontend/.dockerignore"):
        ignore_text = (ROOT / relative).read_text(encoding="utf-8").splitlines()
        if ".env" not in ignore_text:
            failures.append(f"{relative}: .envがビルド対象から除外されていません")

    if failures:
        print("ローカル完結構成の監査に失敗しました。")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("ローカル完結構成の監査に合格しました。クラウドAPIキーは不要です。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
