"""Minimal async client for Mistral's official chat-completions API."""

from typing import Any

import httpx

from app.config import settings


class MistralNotConfiguredError(RuntimeError):
    """Raised when live recommendations are requested without an API key."""


class MistralResponseError(RuntimeError):
    """Raised when the upstream response envelope has no usable content."""


async def complete_structured(
    messages: list[dict[str, str]],
    response_schema: dict[str, Any],
) -> str:
    """Return structured assistant content from Mistral as a JSON string."""
    if not settings.MISTRAL_API_KEY:
        raise MistralNotConfiguredError

    url = settings.MISTRAL_API_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.MISTRAL_MODEL,
        "messages": messages,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "film_recommendation_candidates",
                "schema": response_schema,
                "strict": True,
            },
        },
        "temperature": 0.4,
        "max_tokens": 1800,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(20.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise MistralResponseError from exc

    if isinstance(content, str) and content.strip():
        return content
    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        joined = "".join(text_parts).strip()
        if joined:
            return joined
    raise MistralResponseError
