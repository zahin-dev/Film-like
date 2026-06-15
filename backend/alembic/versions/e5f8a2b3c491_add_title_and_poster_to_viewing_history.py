"""add title and poster_url to viewing_history_entries

Revision ID: e5f8a2b3c491
Revises: d8e7c3a1f052
Create Date: 2026-06-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'e5f8a2b3c491'
down_revision: Union[str, None] = 'd8e7c3a1f052'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Both columns are nullable: existing entries logged before this
    # migration have no cached title/poster — they will be None.
    op.execute("ALTER TABLE viewing_history_entries ADD COLUMN title TEXT")
    op.execute("ALTER TABLE viewing_history_entries ADD COLUMN poster_url TEXT")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE viewing_history_entries DROP COLUMN poster_url")
    op.execute("ALTER TABLE viewing_history_entries DROP COLUMN title")
