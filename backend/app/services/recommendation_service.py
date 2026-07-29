"""Deterministic local recommendation engine with Japanese explanations."""

from collections import Counter
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.film_catalog import FilmCatalog
from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.repositories import viewing_history_repository
from app.schemas.recommendation import (
    Mood,
    Recommendation,
    RecommendationResponse,
)
from app.services import film_service


MOOD_LABELS: dict[Mood, str] = {
    Mood.RELAXED: "リラックスしたい",
    Mood.UPLIFTING: "前向きになりたい",
    Mood.EXCITED: "刺激がほしい",
    Mood.THOUGHTFUL: "じっくり考えたい",
    Mood.EMOTIONAL: "思いきり感動したい",
    Mood.ROMANTIC: "恋愛気分を味わいたい",
    Mood.ADVENTUROUS: "冒険したい",
    Mood.SCARED: "怖い映画を観たい",
}

MOOD_GENRES: dict[Mood, set[str]] = {
    Mood.RELAXED: {"コメディ", "日常", "ファミリー"},
    Mood.UPLIFTING: {"コメディ", "青春", "音楽", "ファミリー"},
    Mood.EXCITED: {"アクション", "SF", "サスペンス"},
    Mood.THOUGHTFUL: {"ドラマ", "ミステリー", "社会派", "SF"},
    Mood.EMOTIONAL: {"ドラマ", "家族", "青春"},
    Mood.ROMANTIC: {"恋愛", "ドラマ", "青春"},
    Mood.ADVENTUROUS: {"冒険", "アクション", "ファンタジー", "SF"},
    Mood.SCARED: {"ホラー", "サスペンス", "ミステリー"},
}

TAG_MOOD_AFFINITY: dict[str, set[Mood]] = {
    "feel-good": {Mood.RELAXED, Mood.UPLIFTING},
    "heartwarming": {Mood.RELAXED, Mood.UPLIFTING, Mood.EMOTIONAL},
    "heartbreaking": {Mood.EMOTIONAL},
    "hilarious": {Mood.RELAXED, Mood.UPLIFTING},
    "terrifying": {Mood.SCARED},
    "fun-jump-scares": {Mood.SCARED, Mood.EXCITED},
    "epic": {Mood.EXCITED, Mood.ADVENTUROUS},
    "cozy-watch": {Mood.RELAXED},
    "unsettling": {Mood.SCARED, Mood.THOUGHTFUL},
    "bittersweet": {Mood.EMOTIONAL, Mood.ROMANTIC},
    "mind-blowing": {Mood.THOUGHTFUL, Mood.EXCITED},
    "conversation-starter": {Mood.THOUGHTFUL},
    "visual-feast": {Mood.ADVENTUROUS, Mood.EXCITED},
    "slow-burn": {Mood.THOUGHTFUL},
    "perfect-for-a-date": {Mood.ROMANTIC},
    "family-friendly": {Mood.RELAXED, Mood.UPLIFTING},
}

RECENT_HISTORY_LIMIT = 5


@dataclass(frozen=True)
class _ScoredFilm:
    film: FilmCatalog
    score: int
    mood_match: bool
    matched_genres: tuple[str, ...]
    history_signal: str | None
    recent_genre: str | None


def recommend(
    db: Session,
    user: User,
    mood: Mood,
    limit: int,
) -> RecommendationResponse:
    """Rank local films without randomness, network calls, or API keys."""
    entries = viewing_history_repository.get_by_user(db, user.id)
    watched_ids = {entry.film_id for entry in entries}
    tag_counts = _tag_frequencies(entries)
    recent_genres = _recent_genre_frequencies(entries)
    candidates = [
        record
        for record in film_service.get_catalog_records(db)
        if record.id not in watched_ids
    ]

    scored = [
        _score_film(record, mood, tag_counts, recent_genres)
        for record in candidates
    ]
    scored.sort(
        key=lambda item: (
            -item.score,
            item.film.title_ja or "",
            item.film.release_date.isoformat() if item.film.release_date else "",
            item.film.id,
        )
    )

    positive = [item for item in scored if item.score > 0]
    fallback_used = (
        len(positive) < min(limit, len(scored))
        or len(scored) < limit
    )
    selected = positive[:limit]
    selected_ids = {item.film.id for item in selected}
    if len(selected) < limit:
        selected.extend(
            item
            for item in scored
            if item.film.id not in selected_ids
        )
        selected = selected[:limit]

    recommendations = [
        Recommendation(
            film=film_service.film_from_record(item.film),
            reason=_build_reason(item, mood, fallback_used=item.score == 0),
        )
        for item in selected
    ]
    history_tags_used = [
        display_name
        for _, (display_name, _) in sorted(
            tag_counts.items(),
            key=lambda item: (-item[1][1], item[1][0]),
        )
    ][:5]
    message = None
    if not candidates:
        message = "未視聴の候補がありません。カタログに映画を追加してください。"
    elif len(recommendations) < limit:
        message = "未視聴の候補が少ないため、取得できた範囲で表示しています。"
    elif fallback_used:
        message = "条件に強く一致する候補が少ないため、未視聴作品から補完しました。"

    return RecommendationResponse(
        mood=mood,
        mood_label=MOOD_LABELS[mood],
        history_tags_used=history_tags_used,
        recommendations=recommendations,
        fallback_used=fallback_used,
        message=message,
    )


def _tag_frequencies(
    entries: list[ViewingHistoryEntry],
) -> dict[str, tuple[str, int]]:
    counts = Counter(tag.key for entry in entries for tag in entry.tags)
    labels = {
        tag.key: tag.display_name_ja
        for entry in entries
        for tag in entry.tags
    }
    return {
        key: (labels[key], count)
        for key, count in counts.items()
    }


def _recent_genre_frequencies(
    entries: list[ViewingHistoryEntry],
) -> Counter[str]:
    recent = entries[-RECENT_HISTORY_LIMIT:]
    return Counter(
        genre
        for entry in recent
        for genre in (entry.film.genres or [])
    )


def _score_film(
    film: FilmCatalog,
    mood: Mood,
    tag_counts: dict[str, tuple[str, int]],
    recent_genres: Counter[str],
) -> _ScoredFilm:
    film_moods = set(film.recommendation_moods or [])
    mood_match = mood.value in film_moods
    score = 50 if mood_match else 0

    matched_genres = tuple(sorted(set(film.genres or []) & MOOD_GENRES[mood]))
    score += len(matched_genres) * 12

    history_signal = None
    for key, (display_name, count) in sorted(
        tag_counts.items(),
        key=lambda item: (-item[1][1], item[1][0]),
    ):
        if mood in TAG_MOOD_AFFINITY.get(key, set()):
            score += min(count, 3) * 5
            history_signal = display_name
            break

    recent_overlap = [
        (genre, recent_genres[genre])
        for genre in (film.genres or [])
        if recent_genres[genre] > 0
    ]
    recent_overlap.sort(key=lambda item: (-item[1], item[0]))
    recent_genre = recent_overlap[0][0] if recent_overlap else None
    if recent_genre:
        score += min(recent_genres[recent_genre], 3) * 3

    return _ScoredFilm(
        film=film,
        score=score,
        mood_match=mood_match,
        matched_genres=matched_genres,
        history_signal=history_signal,
        recent_genre=recent_genre,
    )


def _build_reason(item: _ScoredFilm, mood: Mood, fallback_used: bool) -> str:
    title = item.film.title_ja or "この作品"
    if fallback_used:
        return (
            f"「{MOOD_LABELS[mood]}」に強く一致する候補が少ないため、"
            f"未視聴の{title}をカタログから選びました。"
        )

    parts = [f"「{MOOD_LABELS[mood]}」という今の気分に合う作品です"]
    if item.matched_genres:
        parts.append(f"{'・'.join(item.matched_genres)}の要素があります")
    if item.history_signal:
        parts.append(f"視聴記録の「{item.history_signal}」という傾向も反映しました")
    elif item.recent_genre:
        parts.append(f"最近よく観ている{item.recent_genre}の傾向も反映しました")
    return "。".join(parts) + "。"
