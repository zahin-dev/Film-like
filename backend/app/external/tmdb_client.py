"""
TMDB API Client

This module handles all communication with The Movie Database (TMDB) API.
It is the only layer in the application that sends HTTP requests to TMDB —
the rest of the codebase uses the functions defined here and never calls
the API directly.

TMDB is used as the single source of truth for film metadata: titles,
posters, synopses, cast, runtime, genres, and streaming availability.

Authentication uses a Read Access Token (Bearer token), loaded from the
environment via pydantic_settings. The token is injected automatically
into every request by _get_headers().

Base URL: https://api.themoviedb.org/3
Documentation: https://developer.themoviedb.org/reference/intro/getting-started

Functions:
    - search_movie: search the TMDB catalog by title
    - get_movie_basic: fetch title and poster for a single film (lightweight)
    - get_movie_details: fetch full metadata including credits
    - get_watch_providers: fetch streaming availability by country
"""

import httpx
from app.config import settings  # centralized environment configuration

# TMDB_READ_ACCESS_TOKEN is validated at startup by pydantic_settings —
# guaranteed non-empty
TMDB_READ_ACCESS_TOKEN: str = settings.TMDB_READ_ACCESS_TOKEN

# TMDB_BASE_URL is the beginning of the URL common to all TMDB requests
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _get_headers() -> dict:
    """
    Build the HTTP headers required for every TMDB API request.

    TMDB uses Bearer token authentication. The token is injected here
    so that all functions in this module call _get_headers() instead
    of constructing the Authorization header manually each time.

    Returns:
        dict: A dictionary containing the Authorization and Accept headers.
    """
    return {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }


async def search_movie(query: str) -> list[dict]:
    """
    Search the TMDB catalog by movie title.

    TMDB's search is multilingual by default: a French title query will
    match English movies and vice versa. The language parameter only
    controls the language of the returned data (titles, synopses),
    not the search matching itself. All responses are returned in
    English (en-US) for the MVP.

    Adult content is excluded from results.

    Args:
        query (str): The movie title to search for.

    Returns:
        list[dict]: A list of matching movie objects from TMDB, each
            containing at minimum tmdb_id, title, release date, and
            poster path. Returns an empty list if no results are found.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response.
        httpx.RequestError: If the request cannot be sent (network error,
            timeout, etc.).
    """
    async with httpx.AsyncClient() as client:
        headers = _get_headers()
        params = {
            'query': query,
            'adult': "false",
            'language': "en-US"
        }
        url = TMDB_BASE_URL + "/search/movie"
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("results", [])


async def get_movie_basic(tmdb_id: int) -> dict:
    """
    Fetch the title and poster_path for a single film.

    Lighter alternative to get_movie_details() — does not request
    credits, so it is faster and should be used when only title and
    poster are needed (e.g. at viewing history log time).

    Args:
        tmdb_id (int): The TMDB unique identifier of the movie.

    Returns:
        dict: TMDB movie object containing at minimum title and
            poster_path. poster_path may be None if unavailable.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response.
        httpx.RequestError: If the request cannot be sent.
    """
    async with httpx.AsyncClient() as client:
        headers = _get_headers()
        params = {'language': "en-US"}
        url = TMDB_BASE_URL + f"/movie/{tmdb_id}"
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def get_movie_details(tmdb_id: int) -> dict:
    """
    Fetch full metadata for a single movie by its TMDB identifier.

    Uses append_to_response=credits to retrieve cast and crew in the
    same request, avoiding a second API call. The credits object is
    nested inside the returned dict under the key "credits".

    Args:
        tmdb_id (int): The TMDB unique identifier of the movie.

    Returns:
        dict: The full TMDB movie object, including title, synopsis,
            genres, runtime, poster path, and a nested "credits" object
            containing cast and crew lists.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response
            (e.g. 404 if the tmdb_id does not exist).
        httpx.RequestError: If the request cannot be sent.
    """
    async with httpx.AsyncClient() as client:
        headers = _get_headers()
        params = {
            'language': "en-US",
            'append_to_response': "credits"
        }
        url = TMDB_BASE_URL + f"/movie/{tmdb_id}"
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


async def get_watch_providers(tmdb_id: int, country: str = "FR") -> dict:
    """
    Fetch streaming availability for a movie in a given country.

    TMDB's watch providers endpoint returns availability data for all
    countries. This function filters the response to return only the
    entry for the requested country code, keeping the data minimal.

    The returned dict contains provider lists keyed by type:
    "flatrate" (subscription), "rent", and "buy". Each entry has
    at minimum provider_name and logo_path.

    Args:
        tmdb_id (int): The TMDB unique identifier of the movie.
        country (str): ISO 3166-1 alpha-2 country code.
            Defaults to "FR" (France).

    Returns:
        dict: Streaming providers available in the given country,
            or an empty dict if the movie is not available there.

    Raises:
        httpx.HTTPStatusError: If TMDB returns a non-2xx response.
        httpx.RequestError: If the request cannot be sent.
    """
    async with httpx.AsyncClient() as client:
        headers = _get_headers()
        url = TMDB_BASE_URL + f"/movie/{tmdb_id}/watch/providers"
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("results", {}).get(country, {})
