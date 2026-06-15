"""create viewing history tables

Revision ID: d8e7c3a1f052
Revises: 58a93fa0f7fc
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd8e7c3a1f052'
down_revision: Union[str, None] = '58a93fa0f7fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Pure SQL — bypasses SQLAlchemy's Enum type event system entirely.
    # Using op.create_table() with sa.Enum triggers an _on_table_create hook
    # registered by the imported models (via Base.metadata in env.py), which
    # fires CREATE TYPE unconditionally and cannot be suppressed with
    # create_type=False on the migration's local variable.

    # Drop any orphan type left by a previous failed migration, then recreate.
    # Safe even on a fresh database: DROP IF EXISTS is a no-op when absent.
    op.execute("DROP TYPE IF EXISTS prestigetier")
    op.execute("""
        CREATE TYPE prestigetier AS ENUM (
            'Platinum', 'Gold', 'Silver', 'Bronze', 'Coal', 'Trash'
        )
    """)
    op.execute("""
        CREATE TABLE viewing_history_entries (
            id          UUID        NOT NULL DEFAULT gen_random_uuid(),
            created_at  TIMESTAMP   NOT NULL DEFAULT now(),
            updated_at  TIMESTAMP   NOT NULL DEFAULT now(),
            user_id     UUID        NOT NULL REFERENCES users (id),
            tmdb_id     INTEGER     NOT NULL,
            prestige_tier prestigetier,
            personal_note TEXT,
            PRIMARY KEY (id)
        )
    """)
    op.execute("""
        CREATE TABLE viewing_history_tags (
            viewing_history_entry_id UUID    NOT NULL REFERENCES viewing_history_entries (id),
            tag_id                   INTEGER NOT NULL REFERENCES tags (id),
            PRIMARY KEY (viewing_history_entry_id, tag_id)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS viewing_history_tags")
    op.execute("DROP TABLE IF EXISTS viewing_history_entries")
    op.execute("DROP TYPE IF EXISTS prestigetier")
