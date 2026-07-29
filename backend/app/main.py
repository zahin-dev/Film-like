"""Film-like 日本語・ローカル完結版のFastAPIエントリーポイント。"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import auth, film, insight, recommendation, tag


app = FastAPI(
    title="Film-like 日本語版 API",
    description=(
        "ローカル映画カタログ、視聴記録、タグ分析、決定的な推薦を提供します。"
        "クラウド映画APIやクラウドLLMのAPIキーは必要ありません。"
    ),
    version="1.0.0-ja-offline",
    responses={
        401: {"description": "ログインまたは有効な認証情報が必要です。"},
        404: {"description": "指定された情報が見つかりません。"},
        409: {"description": "既存データと競合しました。"},
        422: {"description": "入力内容が正しくありません。"},
        500: {"description": "サーバー内部で予期しないエラーが発生しました。"},
    },
    openapi_tags=[
        {"name": "認証", "description": "アカウント登録とログイン"},
        {"name": "映画", "description": "ローカル映画検索、詳細、視聴記録"},
        {"name": "タグ", "description": "日本語の感想タグ"},
        {"name": "分析", "description": "視聴記録から算出する説明可能な集計"},
        {"name": "推薦", "description": "外部AIを使わないローカル推薦"},
        {"name": "システム", "description": "APIの稼働状態と地域設定"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_POSTER_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "posters"
app.mount(
    "/posters",
    StaticFiles(directory=_POSTER_DIRECTORY),
    name="posters",
)


_FIELD_LABELS = {
    "first_name": "名",
    "last_name": "姓",
    "email": "メールアドレス",
    "password": "パスワード",
    "age": "年齢",
    "query": "検索語",
    "film_id": "映画ID",
    "tmdb_id": "旧TMDB ID",
    "tag_ids": "タグ",
    "mood": "気分",
    "limit": "件数",
    "personal_note": "メモ",
}


def _validation_message(error: dict) -> str:
    field = _FIELD_LABELS.get(str(error.get("loc", ["入力"])[-1]), "入力値")
    error_type = str(error.get("type", ""))
    if error_type == "missing":
        return f"{field}は必須です。"
    if "too_short" in error_type:
        return f"{field}が短すぎます。"
    if "too_long" in error_type:
        return f"{field}が長すぎます。"
    if "greater_than" in error_type or "less_than" in error_type:
        return f"{field}が指定できる範囲外です。"
    if error_type in {"int_parsing", "int_type"}:
        return f"{field}は整数で入力してください。"
    if error_type == "value_error":
        context_error = error.get("ctx", {}).get("error")
        if context_error:
            return str(context_error)
    if error_type == "enum":
        return f"{field}の選択肢が正しくありません。"
    return f"{field}の入力内容が正しくありません。"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return Japanese validation errors without exposing invalid payloads."""
    details = [
        {
            "loc": list(error.get("loc", [])),
            "msg": _validation_message(error),
            "type": error.get("type", "value_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Keep unexpected implementation details out of user-facing responses."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "サーバーで予期しないエラーが発生しました。時間をおいて再試行してください。"
        },
    )


app.include_router(auth.router)
app.include_router(film.router)
app.include_router(insight.router)
app.include_router(recommendation.router)
app.include_router(tag.router)


@app.get(
    "/",
    summary="稼働確認",
    description="APIの稼働状態と地域設定を返します。",
    tags=["システム"],
)
def root() -> dict[str, str]:
    return {
        "message": "Film-like 日本語版 API は稼働中です。",
        "locale": settings.APP_LOCALE,
        "region": settings.APP_REGION,
        "timezone": settings.APP_TIMEZONE,
    }
