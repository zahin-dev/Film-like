"""remove cached film metadata from viewing history

Revision ID: b3d91f6a2c04
Revises: e5f8a2b3c491
Create Date: 2026-07-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b3d91f6a2c04"
down_revision: Union[str, None] = "e5f8a2b3c491"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Keep TMDB as the only source of film metadata."""
    op.drop_column("viewing_history_entries", "poster_url")
    op.drop_column("viewing_history_entries", "title")


def downgrade() -> None:
    """Restore the former nullable metadata cache columns."""
    op.add_column(
        "viewing_history_entries",
        sa.Column("title", sa.Text(), nullable=True),
    )
    op.add_column(
        "viewing_history_entries",
        sa.Column("poster_url", sa.Text(), nullable=True),
    )
