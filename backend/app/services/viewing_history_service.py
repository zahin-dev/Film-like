"""Viewing-history operations using the local film catalogue."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.prestige_tier import PrestigeTier
from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.repositories import film_catalog_repository, viewing_history_repository
from app.schemas.viewing_history import (
    TagResponse,
    ViewingHistoryEntryCreate,
    ViewingHistoryEntryResponse,
)


PRESTIGE_LABELS: dict[PrestigeTier, str] = {
    PrestigeTier.PLATINUM: "最高傑作",
    PrestigeTier.GOLD: "かなり良い",
    PrestigeTier.SILVER: "良い",
    PrestigeTier.BRONZE: "まずまず",
    PrestigeTier.COAL: "いまひとつ",
    PrestigeTier.TRASH: "合わなかった",
}


def get_all_tags(db: Session) -> list[TagResponse]:
    tags = viewing_history_repository.get_all_tags(db)
    return [
        TagResponse(
            id=tag.id,
            key=tag.key,
            name=tag.display_name_ja,
            description=tag.description_ja,
        )
        for tag in tags
    ]


def create_entry(
    db: Session, user: User, payload: ViewingHistoryEntryCreate
) -> ViewingHistoryEntryResponse:
    film = None
    if payload.film_id is not None:
        film = film_catalog_repository.get_by_id(db, payload.film_id)
    elif payload.tmdb_id is not None:
        film = film_catalog_repository.get_by_tmdb_id(db, payload.tmdb_id)
    if film is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された映画はローカルカタログにありません。",
        )

    if viewing_history_repository.get_by_user_and_film(db, user.id, film.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この映画はすでに視聴記録へ追加されています。",
        )

    tags = viewing_history_repository.get_tags_by_ids(db, payload.tag_ids)
    if len(tags) != len(set(payload.tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="選択されたタグの一部が見つかりません。",
        )

    entry = ViewingHistoryEntry(
        user_id=user.id,
        film_id=film.id,
        tmdb_id=film.tmdb_id,
        tags=tags,
        prestige_tier=payload.prestige_tier,
        personal_note=payload.personal_note,
    )
    created = viewing_history_repository.create(db, entry)
    return _entry_response(created)


def get_history(
    db: Session, user: User
) -> list[ViewingHistoryEntryResponse]:
    return [
        _entry_response(entry)
        for entry in viewing_history_repository.get_by_user(db, user.id)
    ]


def _entry_response(
    entry: ViewingHistoryEntry,
) -> ViewingHistoryEntryResponse:
    film = entry.film
    return ViewingHistoryEntryResponse(
        id=entry.id,
        film_id=entry.film_id,
        tmdb_id=entry.tmdb_id,
        title=film.title_ja or "日本語タイトル情報はありません",
        poster_url=film.poster_path,
        tags=[
            TagResponse(
                id=tag.id,
                key=tag.key,
                name=tag.display_name_ja,
                description=tag.description_ja,
            )
            for tag in entry.tags
        ],
        prestige_tier=entry.prestige_tier,
        prestige_tier_label=(
            PRESTIGE_LABELS[entry.prestige_tier]
            if entry.prestige_tier
            else None
        ),
        personal_note=entry.personal_note,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def remove_entry(
    db: Session, user: User, film_id: int
) -> None:
    if not viewing_history_repository.remove_by_film(db, user.id, film_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この映画の視聴記録は見つかりません。",
        )


def remove_entry_by_tmdb(
    db: Session, user: User, tmdb_id: int
) -> None:
    """Compatibility path for records created by older clients."""
    if not viewing_history_repository.remove(db, user.id, tmdb_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この外部IDに対応する視聴記録は見つかりません。",
        )
