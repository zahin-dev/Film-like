"""
Film Service

This module implements the business logic for film-related operations
in the Film-like application.

Its sole responsibility is to bridge the TMDB client and the Film schema:
it calls the raw TMDB API functions, extracts the relevant fields, and
returns structured Film objects. Routes never interact with tmdb_client
directly.

Functions:
    - search_films: search the TMDB catalog and return a list of Films
    - get_film_details: fetch full metadata for a single film
    - get_film_with_status: fetch full metadata and indicate if the film
      is already in the authenticated user's viewing history
"""

from sqlalchemy.orm import Session
from app.schemas.film import Film, FilmWithStatus
from app.external import tmdb_client
from app.repositories import viewing_history_repository
from app.models.user import User

# Base URL for TMDB poster images — w500 is a good balance for the frontend
POSTER_PATH_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Number of cast members included in film detail responses
CAST_LIMIT = 5


def _extract_year(release_date: str | None) -> int | None:
    """Extract the 4-digit year from a TMDB release_date string (YYYY-MM-DD)."""
    if not release_date:
        return None
    return int(release_date[:4])


def _build_poster_url(poster_path: str | None) -> str | None:
    """Return the full poster URL from a TMDB poster_path, or None."""
    if poster_path is None:
        return None
    return POSTER_PATH_BASE_URL + poster_path


async def search_films(query: str) -> list[Film]:
    """
    Search the TMDB catalog and return a list of Film objects.

    Maps raw TMDB search results to Film schemas. Genre names are not
    available in search results (TMDB returns integer genre_ids only),
    so genres is always None here. Full genre names are available via
    get_film_details().

    Args:
        query (str): Movie title to search for.

    Returns:
        list[Film]: Partial Film objects with only the fields available
            from the search endpoint: tmdb_id, title, year, poster_url,
            and synopsis. All other fields are None.

    Raises:
        httpx.HTTPStatusError: If the TMDB API returns a non-2xx response.
        httpx.RequestError: If the request cannot be sent.
    """
    raw_results = await tmdb_client.search_movie(query)
    return [
        Film(
            tmdb_id=raw_film["id"],
            title=raw_film["title"],
            year=_extract_year(raw_film.get("release_date")),
            poster_url=_build_poster_url(raw_film.get("poster_path")),
            synopsis=raw_film.get("overview") or None,
        )
        for raw_film in raw_results
    ]


async def get_film_details(tmdb_id: int) -> Film:
    """
    Fetch full metadata for a single film from TMDB.

    Calls get_movie_details() and get_watch_providers() and maps the
    combined response to a fully populated Film object.

    Mapping decisions:
        - Director: first crew member with job == "Director".
        - Cast: top CAST_LIMIT billed actors (ordered by TMDB billing).
        - Streaming platforms: flatrate (subscription) providers only.
          Rent and buy options are excluded for the MVP.

    Args:
        tmdb_id (int): TMDB unique identifier of the movie.

    Returns:
        Film: A fully populated Film object.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response
            (e.g. 404 if the tmdb_id does not exist).
        httpx.RequestError: If the request cannot be sent.
    """
    details = await tmdb_client.get_movie_details(tmdb_id)

    providers = await tmdb_client.get_watch_providers(tmdb_id)

    credits = details.get("credits", {})

    director = next(
        (member["name"] for member in credits.get("crew", [])
        if member.get("job") == "Director"),
        None
    )

    cast = [member["name"] for member in credits.get("cast", [])[:CAST_LIMIT]]

    seen = set()
    streaming_platforms = [
        p["provider_name"] for p in providers.get("flatrate", [])
        if not (p["provider_name"] in seen or seen.add(p["provider_name"]))
    ]

    return Film(
        tmdb_id=details["id"],
        title=details["title"],
        year=_extract_year(details.get("release_date")),
        genres=[g["name"] for g in details.get("genres", [])] or None,
        poster_url=_build_poster_url(details.get("poster_path")),
        synopsis=details.get("overview") or None,
        director=director,
        cast=cast or None,
        runtime=details.get("runtime") or None,
        streaming_platforms=streaming_platforms or None,
    )


async def get_film_with_status(
    db: Session, user: User, tmdb_id: int
) -> FilmWithStatus:
    """
    Fetch full metadata for a single film and indicate its history status.

    Combines get_film_details() with a database lookup to tell the frontend
    whether the authenticated user has already logged this film. This allows
    the film detail page to render the correct UI state (log vs. remove)
    in a single request.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI.
        user (User): The authenticated user, injected by get_current_user.
        tmdb_id (int): TMDB unique identifier of the movie.

    Returns:
        FilmWithStatus: The fully populated Film object alongside
            in_history (True if the user has logged this film).

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response.
        httpx.RequestError: If the request cannot be sent.
    """
    film = await get_film_details(tmdb_id)
    in_history = viewing_history_repository.get_by_user_and_tmdb(
        db, user.id, tmdb_id
    ) is not None
    return FilmWithStatus(film=film, in_history=in_history)
