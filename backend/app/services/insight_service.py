"""Deterministic aggregation of user-selected diary reaction tags."""

from collections import Counter

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.viewing_history_entry import ViewingHistoryEntry
from app.repositories import viewing_history_repository
from app.schemas.insight import DiaryInsightsResponse, ReactionSignalSummary


# Top signals keep the dashboard concise. Recent signals use the latest five
# diary entries in the repository's deterministic chronological ordering.
TOP_REACTION_SIGNAL_LIMIT = 5
RECENT_HISTORY_LIMIT = 5


def get_diary_insights(db: Session, user: User) -> DiaryInsightsResponse:
    """Aggregate only the authenticated user's stored reaction tags.

    Percentages represent the share of tagged films containing a signal and
    are rounded to two decimal places. Recent percentages use tagged films
    within the latest ``RECENT_HISTORY_LIMIT`` entries as their denominator.
    No external service or inferred sentiment is involved.
    """
    entries = viewing_history_repository.get_by_user(db, user.id)
    tagged_films = _count_tagged_films(entries)
    all_signals = _summarize_signals(entries, tagged_films)

    recent_entries = entries[-RECENT_HISTORY_LIMIT:]
    recent_tagged_films = _count_tagged_films(recent_entries)
    recent_signals = _summarize_signals(recent_entries, recent_tagged_films)

    return DiaryInsightsResponse(
        total_films=len(entries),
        tagged_films=tagged_films,
        unique_reaction_signals=len(all_signals),
        top_reaction_signals=all_signals[:TOP_REACTION_SIGNAL_LIMIT],
        recent_reaction_signals=recent_signals,
    )


def _count_tagged_films(entries: list[ViewingHistoryEntry]) -> int:
    """Count diary entries with at least one selected reaction tag."""
    return sum(bool(entry.tags) for entry in entries)


def _summarize_signals(
    entries: list[ViewingHistoryEntry],
    tagged_films: int,
) -> list[ReactionSignalSummary]:
    """Return counts ordered by count descending, then tag name ascending."""
    if tagged_films == 0:
        return []

    counts = Counter(tag.name for entry in entries for tag in entry.tags)
    ordered_counts = sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0].casefold(), item[0]),
    )
    return [
        ReactionSignalSummary(
            tag=tag,
            count=count,
            percentage=round(count / tagged_films * 100, 2),
        )
        for tag, count in ordered_counts
    ]
