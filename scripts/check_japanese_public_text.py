#!/usr/bin/env python3
"""Audit critical user-facing surfaces for Japanese text and legacy English."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "frontend/index.html": ['<html lang="ja">', "日本語の映画日記"],
    "frontend/src/components/PageState.jsx": [
        "読み込み中です",
        "読み込みに失敗しました",
        "もう一度試す",
    ],
    "frontend/src/pages/AuthPage/AuthPage.jsx": [
        "ログイン",
        "アカウントを作成",
        'aria-label="主な機能"',
    ],
    "frontend/src/pages/CatalogPage/index.jsx": [
        "映画タイトルを検索",
        "ローカルカタログ",
    ],
    "frontend/src/pages/DashboardPage/index.jsx": [
        "Intl.DateTimeFormat('ja-JP'",
        "Asia/Tokyo",
        "視聴履歴",
    ],
    "frontend/src/pages/RecommendationPage/index.jsx": [
        "ローカル推薦エンジン",
        "外部AI",
        'aria-label="現在の気分"',
    ],
    "frontend/src/pages/FilmDetailPage/index.jsx": [
        "日本語のあらすじ情報はありません",
        "出演者情報はありません",
        "配信情報はありません",
    ],
    "backend/app/main.py": [
        "Film-like 日本語版 API",
        "クラウド映画API",
    ],
}

FORBIDDEN_PHRASES = [
    "We hit a snag",
    "Try again",
    "Search films",
    "Searching TMDB",
    "TMDB catalog",
    "Streaming in France",
    "Viewing history",
    "Diary Insights",
    "Mistral AI",
    "Asking Mistral",
    "Recommendations are not available",
    "Sign in to Film-like",
    "Create your account",
    "Log out",
    "No matching films",
    "Year unavailable",
    "Not available",
    "Personal note",
    "Current mood",
    '<html lang="en">',
    "Intl.DateTimeFormat('en'",
]

# Product/technology names, internal values, API paths, and original titles are
# intentionally outside this exact-phrase audit.


def main() -> int:
    failures: list[str] = []
    for relative, fragments in REQUIRED.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"{relative}: 必須の日本語契約がありません: {fragment}")

    frontend_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "frontend" / "src").rglob("*")
        if path.suffix in {".js", ".jsx"}
    )
    frontend_text += (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in frontend_text:
            failures.append(f"旧英語表示が残っています: {phrase}")

    backend_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "backend" / "app").rglob("*.py")
    )
    for match in re.finditer(
        r"detail\s*=\s*[\"']([A-Za-z][^\"']*)[\"']",
        backend_text,
    ):
        failures.append(f"英語のAPIエラー候補があります: {match.group(1)}")

    if failures:
        print("日本語公開文監査に失敗しました。")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("日本語公開文監査に合格しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
