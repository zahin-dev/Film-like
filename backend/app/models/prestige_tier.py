"""
Prestige Tier

This module defines the PrestigeTier enum used to rate a film entry
in the user's viewing history.

Storage note: SQLAlchemy's Enum type stores the VALUE of each member
(e.g. "Platinum"), not the Python name (PLATINUM). The Python names
are just identifiers used in code; only the value strings matter at
the database level.
"""

import enum


class PrestigeTier(enum.Enum):
    """
    Ordered rating scale a user assigns to a viewed film.

    The value of each member (e.g. "Platinum") is what gets stored
    in the database and sent to the frontend. The Python name
    (e.g. PLATINUM) is only used in application code.

    Members (best to worst):
        PLATINUM: Exceptional — an all-time favourite.
        GOLD:     Great — very enjoyable and memorable.
        SILVER:   Good — solid film, worth watching.
        BRONZE:   Decent — had its moments.
        COAL:     Poor — mostly disappointing.
        TRASH:    Bad — regretted watching it.
    """
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    COAL = "Coal"
    TRASH = "Trash"
