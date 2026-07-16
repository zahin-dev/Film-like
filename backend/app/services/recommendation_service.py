"""Recommendation Facade combining user context, Mistral, and TMDB."""

import asyncio
from collections import Counter
from datetime import datetime, timezone
import json

import httpx
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.external import mistral_client, tmdb_client
from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.repositories import viewing_history_repository
from app.schemas.film import Film
from app.schemas.recommendation import (
    AICandidate,
    AICandidateList,
    Mood,
    Recommendation,
    RecommendationResponse,
)
from app.services import film_service


class RecommendationServiceError(RuntimeError):
    """Safe application error that can be exposed by the API route."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


_SYSTEM_PROMPT = """You recommend feature films for a personal movie diary.
Return only the requested JSON object. Suggest real, released feature films
that fit the current mood and the supplied preference context. Never invent
TMDB identifiers. Avoid every recently viewed title and give one concise,
specific reason per candidate."""

_RECENT_HISTORY_LIMIT = 10
_MAX_ATTEMPTS = 2


async def recommend(
    db: Session,
    user: User,
    mood: Mood,
    limit: int,
) -> RecommendationResponse:
    """Return Mistral-suggested candidates only after TMDB verification."""
    entries = viewing_history_repository.get_by_user(db, user.id)
    watched_ids = {entry.tmdb_id for entry in entries}
    tag_counts = _tag_frequencies(entries)
    recent_titles = await _resolve_recent_titles(entries)
    candidate_count = min(20, max(8, limit * 2))

    recommendations: list[Recommendation] = []
    seen_candidate_titles: set[str] = set()
    seen_tmdb_ids: set[int] = set()
    parsed_at_least_once = False

    for attempt in range(_MAX_ATTEMPTS):
        messages = _build_messages(
            mood=mood,
            tag_counts=tag_counts,
            recent_titles=recent_titles,
            candidate_count=candidate_count,
            retry=attempt > 0,
        )
        try:
            raw_output = await mistral_client.complete_structured(
                messages=messages,
                response_schema=AICandidateList.model_json_schema(),
            )
        except mistral_client.MistralNotConfiguredError as exc:
            raise RecommendationServiceError(
                503, "AI recommendation service is not configured."
            ) from exc
        except httpx.TimeoutException as exc:
            raise RecommendationServiceError(
                504, "AI recommendation service timed out."
            ) from exc
        except httpx.RequestError as exc:
            raise RecommendationServiceError(
                503, "AI recommendation service is temporarily unreachable."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = _upstream_status_detail(exc.response.status_code)
            raise RecommendationServiceError(503, detail) from exc
        except mistral_client.MistralResponseError:
            raw_output = ""

        try:
            candidate_list = AICandidateList.model_validate_json(raw_output)
        except ValidationError:
            continue

        parsed_at_least_once = True
        candidates = _unique_candidates(
            candidate_list.candidates, seen_candidate_titles
        )
        verified = await _verify_candidates(
            candidates,
            watched_ids=watched_ids,
            seen_tmdb_ids=seen_tmdb_ids,
        )
        recommendations.extend(verified)
        if len(recommendations) >= limit:
            return RecommendationResponse(
                mood=mood,
                history_tags_used=list(tag_counts),
                recommendations=recommendations[:limit],
            )

    if not parsed_at_least_once:
        raise RecommendationServiceError(
            502, "AI recommendation service returned malformed output."
        )
    raise RecommendationServiceError(
        502, "Not enough verified recommendations were available."
    )


def _tag_frequencies(entries: list[ViewingHistoryEntry]) -> dict[str, int]:
    counts = Counter(tag.name for entry in entries for tag in entry.tags)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())))


async def _resolve_recent_titles(
    entries: list[ViewingHistoryEntry],
) -> list[str]:
    recent = entries[-_RECENT_HISTORY_LIMIT:]

    async def resolve(entry: ViewingHistoryEntry) -> str | None:
        try:
            data = await tmdb_client.get_movie_basic(entry.tmdb_id)
        except httpx.HTTPError:
            return None
        title = data.get("title")
        return title.strip() if isinstance(title, str) and title.strip() else None

    if not recent:
        return []
    resolved = await asyncio.gather(*(resolve(entry) for entry in recent))
    return [title for title in resolved if title]


def _build_messages(
    mood: Mood,
    tag_counts: dict[str, int],
    recent_titles: list[str],
    candidate_count: int,
    retry: bool,
) -> list[dict[str, str]]:
    context = {
        "current_mood": mood.value,
        "history_tag_frequencies": [
            {"tag": tag, "count": count} for tag, count in tag_counts.items()
        ],
        "recent_viewed_titles": recent_titles,
        "candidate_count": candidate_count,
        "requirements": [
            "Return different titles with no duplicates.",
            "Use release years only when reasonably confident.",
            "Do not repeat any recent viewed title.",
        ],
    }
    if retry:
        context["retry_instruction"] = (
            "The previous candidates could not all be validated. Return different, "
            "well-known films that are likely to resolve unambiguously in TMDB."
        )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(context, ensure_ascii=True)},
    ]


def _unique_candidates(
    candidates: list[AICandidate],
    seen_titles: set[str],
) -> list[AICandidate]:
    unique: list[AICandidate] = []
    current_year = datetime.now(timezone.utc).year
    for candidate in candidates:
        key = " ".join(candidate.title.casefold().split())
        if key in seen_titles:
            continue
        seen_titles.add(key)
        if candidate.year is not None and not 1888 <= candidate.year <= current_year + 2:
            continue
        unique.append(candidate)
    return unique


async def _verify_candidates(
    candidates: list[AICandidate],
    watched_ids: set[int],
    seen_tmdb_ids: set[int],
) -> list[Recommendation]:
    async def search(candidate: AICandidate) -> tuple[AICandidate, list[Film]]:
        try:
            films = await film_service.search_films(candidate.title)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            films = []
        return candidate, films

    resolved = await asyncio.gather(*(search(candidate) for candidate in candidates))
    recommendations: list[Recommendation] = []
    for candidate, films in resolved:
        film = _select_film(films, candidate.year)
        if film is None:
            continue
        if film.tmdb_id in watched_ids or film.tmdb_id in seen_tmdb_ids:
            continue
        seen_tmdb_ids.add(film.tmdb_id)
        recommendations.append(Recommendation(film=film, reason=candidate.reason))
    return recommendations


def _select_film(films: list[Film], year: int | None) -> Film | None:
    if not films:
        return None
    if year is not None:
        matched = next((film for film in films if film.year == year), None)
        if matched is not None:
            return matched
    return films[0]


def _upstream_status_detail(status_code: int) -> str:
    if status_code in {401, 403}:
        return "AI recommendation service credentials were rejected."
    if status_code == 429:
        return "AI recommendation service is rate limited. Please try again later."
    return "AI recommendation service is temporarily unavailable."
