"""Local film catalogue and viewing-history routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.film import Film, FilmWithStatus
from app.schemas.viewing_history import (
    ViewingHistoryEntryCreate,
    ViewingHistoryEntryResponse,
)
from app.services import film_service, viewing_history_service


router = APIRouter(prefix="/films", tags=["映画"])


@router.get(
    "/search",
    response_model=list[Film],
    summary="映画を検索",
    description="ローカルカタログを日本語タイトル優先で検索します。",
)
def search_films(
    query: str = Query(
        ...,
        min_length=1,
        max_length=200,
        description="検索する日本語タイトルまたは原題",
    ),
    db: Session = Depends(get_db),
) -> list[Film]:
    return film_service.search_films(db, query)


@router.get(
    "/history",
    response_model=list[ViewingHistoryEntryResponse],
    summary="視聴記録を取得",
    description="ログイン中のユーザーが保存した視聴記録を返します。",
)
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ViewingHistoryEntryResponse]:
    return viewing_history_service.get_history(db, current_user)


@router.get(
    "/by-tmdb/{tmdb_id}",
    response_model=Film,
    summary="旧TMDB IDで映画を照合",
    description="移行済みデータの照合に使う後方互換エンドポイントです。",
)
def get_film_by_tmdb(
    tmdb_id: int,
    db: Session = Depends(get_db),
) -> Film:
    film = film_service.get_film_by_tmdb_id(db, tmdb_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された外部IDに対応する映画は見つかりません。",
        )
    return film


@router.get(
    "/{film_id}",
    response_model=FilmWithStatus,
    summary="映画詳細を取得",
    description="ローカル映画IDで詳細と視聴記録の登録状態を返します。",
)
def get_film(
    film_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FilmWithStatus:
    result = film_service.get_film_with_status(db, current_user, film_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された映画はローカルカタログにありません。",
        )
    return result


@router.post(
    "/log",
    response_model=ViewingHistoryEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="視聴記録へ追加",
    description="ローカル映画IDと感想・評価・タグを保存します。",
)
def log_film(
    payload: ViewingHistoryEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ViewingHistoryEntryResponse:
    return viewing_history_service.create_entry(db, current_user, payload)


@router.delete(
    "/log/by-tmdb/{tmdb_id}",
    summary="旧TMDB IDで視聴記録を削除",
    description="旧クライアント向けの後方互換エンドポイントです。",
)
def remove_film_by_tmdb(
    tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    viewing_history_service.remove_entry_by_tmdb(db, current_user, tmdb_id)
    return {"detail": "視聴記録から削除しました。"}


@router.delete(
    "/log/{film_id}",
    summary="視聴記録から削除",
    description="ローカル映画IDに一致する自分の視聴記録を削除します。",
)
def remove_film(
    film_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    viewing_history_service.remove_entry(db, current_user, film_id)
    return {"detail": "視聴記録から削除しました。"}
