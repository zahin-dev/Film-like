"""add local Japanese film catalog

Revision ID: c7d4e8f1a2b3
Revises: b3d91f6a2c04
Create Date: 2026-07-26 00:00:00.000000

"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d4e8f1a2b3"
down_revision: Union[str, None] = "b3d91f6a2c04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TAG_LABELS = {
    "Feel-Good Movie": ("feel-good", "元気をもらえる"),
    "Heartwarming": ("heartwarming", "心が温まる"),
    "Heartbreaking": ("heartbreaking", "胸が締めつけられる"),
    "Hilarious": ("hilarious", "とにかく笑える"),
    "Terrifying": ("terrifying", "本気で怖い"),
    "Fun Jump Scares": ("fun-jump-scares", "驚きも楽しい"),
    "Meh": ("meh", "可もなく不可もなく"),
    "All That for What?": ("unclear-payoff", "結末に納得できない"),
    "Epic": ("epic", "壮大で圧倒される"),
    "Cozy Watch": ("cozy-watch", "ほっとして観られる"),
    "Unsettling": ("unsettling", "不穏な余韻"),
    "Bittersweet": ("bittersweet", "ほろ苦く切ない"),
    "Mind-Blowing": ("mind-blowing", "衝撃を受けた"),
    "Hidden Gem": ("hidden-gem", "隠れた良作"),
    "Cult Classic": ("cult-classic", "熱狂的に愛される"),
    "Must-See": ("must-see", "一度は観てほしい"),
    "Nostalgia Hit": ("nostalgic", "懐かしい気持ち"),
    "Hasn't Aged Well": ("dated", "今見ると気になる"),
    "Rewatchable": ("rewatchable", "何度でも観たい"),
    "Masterpiece": ("masterpiece", "文句なしの傑作"),
    "I Can Die Now": ("deeply-satisfying", "満足感がすごい"),
    "Guilty Pleasure": ("guilty-pleasure", "欠点も含めて好き"),
    "So Stupid It's Good": ("silly-fun", "くだらなさが楽しい"),
    "Perfect for a Date": ("perfect-for-a-date", "デートで観たい"),
    "Crowd Pleaser": ("crowd-pleaser", "みんなで楽しめる"),
    "Family Friendly": ("family-friendly", "家族で観やすい"),
    "Conversation Starter": ("conversation-starter", "語りたくなる"),
    "Late-Night Watch": ("late-night", "夜に観たい"),
    "Underrated": ("underrated", "もっと評価されてほしい"),
    "Overrated": ("overrated", "評判ほどではない"),
    "Perfect Cast": ("perfect-cast", "配役がぴったり"),
    "Amazing Script": ("great-script", "脚本がすばらしい"),
    "Visual Feast": ("visual-feast", "映像が美しい"),
    "Great Soundtrack": ("great-soundtrack", "音楽がすばらしい"),
    "Comfort Movie": ("comfort-movie", "心のよりどころ"),
    "Emotional Damage": ("emotional-damage", "感情を揺さぶられた"),
    "What Did I Just Watch?": ("confusing", "何を観たのだろう"),
    "Slow Burn": ("slow-burn", "じわじわ効く"),
    "Too Long": ("too-long", "少し長く感じた"),
    "Surprisingly Good": ("surprisingly-good", "予想以上によかった"),
    "Pure Chaos": ("pure-chaos", "混沌が楽しい"),
    "Badass": ("badass", "とにかく格好いい"),
    "Smart and Clever": ("smart", "知的で巧み"),
    "Beautifully Weird": ("beautifully-weird", "美しくて不思議"),
    "Instant Classic": ("instant-classic", "新たな定番"),
    "Not for Me": ("not-for-me", "自分には合わない"),
    "Great Villain": ("great-villain", "敵役が魅力的"),
    "Strong Ending": ("strong-ending", "ラストがすばらしい"),
    "Weak Ending": ("weak-ending", "ラストが惜しい"),
    "Vibe Over Plot": ("vibe-over-plot", "物語より雰囲気"),
}


def upgrade() -> None:
    op.add_column("tags", sa.Column("key", sa.String(64), nullable=True))
    op.add_column(
        "tags", sa.Column("display_name_ja", sa.String(60), nullable=True)
    )
    op.add_column(
        "tags", sa.Column("description_ja", sa.String(255), nullable=True)
    )
    bind = op.get_bind()
    tag_rows = bind.execute(sa.text("SELECT id, name FROM tags")).mappings().all()
    for row in tag_rows:
        key, label = TAG_LABELS.get(
            row["name"],
            (f"legacy-{row['id']}", f"移行済みタグ {row['id']}"),
        )
        bind.execute(
            sa.text(
                """
                UPDATE tags
                SET key = :key,
                    display_name_ja = :label,
                    description_ja = :description
                WHERE id = :id
                """
            ),
            {
                "key": key,
                "label": label,
                "description": "既存の視聴記録を保持するために移行したタグです。",
                "id": row["id"],
            },
        )
    op.alter_column("tags", "key", nullable=False)
    op.alter_column("tags", "display_name_ja", nullable=False)
    op.alter_column("tags", "description_ja", nullable=False)
    op.create_unique_constraint("uq_tags_key", "tags", ["key"])

    op.create_table(
        "film_data_sources",
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("license_name", sa.String(160), nullable=False),
        sa.Column("license_url", sa.String(500), nullable=True),
        sa.Column("commercial_use", sa.String(40), nullable=False),
        sa.Column("redistribution", sa.String(40), nullable=False),
        sa.Column("obtained_on", sa.Date(), nullable=False),
        sa.Column("has_japanese_metadata", sa.Boolean(), nullable=False),
        sa.Column("update_method", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "films",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_key", sa.String(64), nullable=False),
        sa.Column("external_id", sa.String(160), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=True),
        sa.Column("title_ja", sa.String(300), nullable=True),
        sa.Column("original_title", sa.String(300), nullable=True),
        sa.Column("synopsis_ja", sa.Text(), nullable=True),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("runtime_minutes", sa.Integer(), nullable=True),
        sa.Column("genres", sa.JSON(), nullable=False),
        sa.Column("directors", sa.JSON(), nullable=False),
        sa.Column("cast_members", sa.JSON(), nullable=False),
        sa.Column("poster_path", sa.String(500), nullable=True),
        sa.Column("streaming_platforms", sa.JSON(), nullable=False),
        sa.Column(
            "streaming_region",
            sa.String(2),
            server_default="JP",
            nullable=False,
        ),
        sa.Column("streaming_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("normalized_title", sa.String(800), nullable=False),
        sa.Column("recommendation_moods", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_key"], ["film_data_sources.key"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tmdb_id"),
        sa.UniqueConstraint(
            "source_key",
            "external_id",
            name="uq_films_source_external_id",
        ),
    )
    op.create_index(
        "ix_films_normalized_title",
        "films",
        ["normalized_title"],
        unique=False,
    )

    source_table = sa.table(
        "film_data_sources",
        sa.column("key", sa.String),
        sa.column("display_name", sa.String),
        sa.column("license_name", sa.String),
        sa.column("license_url", sa.String),
        sa.column("commercial_use", sa.String),
        sa.column("redistribution", sa.String),
        sa.column("obtained_on", sa.Date),
        sa.column("has_japanese_metadata", sa.Boolean),
        sa.column("update_method", sa.Text),
        sa.column("notes", sa.Text),
    )
    op.bulk_insert(
        source_table,
        [
            {
                "key": "legacy-tmdb",
                "display_name": "旧TMDB識別子からの移行データ",
                "license_name": "外部識別子のみ保持",
                "license_url": None,
                "commercial_use": "識別子のみ",
                "redistribution": "識別子のみ",
                "obtained_on": date(2026, 7, 26),
                "has_japanese_metadata": False,
                "update_method": "権利確認済みのローカルデータで手動補完",
                "notes": "旧視聴記録との照合用です。TMDBの説明文や画像は保存しません。",
            }
        ],
    )

    existing_tmdb_ids = [
        row[0]
        for row in bind.execute(
            sa.text(
                "SELECT DISTINCT tmdb_id FROM viewing_history_entries "
                "WHERE tmdb_id IS NOT NULL ORDER BY tmdb_id"
            )
        ).all()
    ]
    films_table = sa.table(
        "films",
        sa.column("source_key", sa.String),
        sa.column("external_id", sa.String),
        sa.column("tmdb_id", sa.Integer),
        sa.column("title_ja", sa.String),
        sa.column("original_title", sa.String),
        sa.column("synopsis_ja", sa.Text),
        sa.column("release_date", sa.Date),
        sa.column("runtime_minutes", sa.Integer),
        sa.column("genres", sa.JSON),
        sa.column("directors", sa.JSON),
        sa.column("cast_members", sa.JSON),
        sa.column("poster_path", sa.String),
        sa.column("streaming_platforms", sa.JSON),
        sa.column("streaming_region", sa.String),
        sa.column("streaming_updated_at", sa.DateTime),
        sa.column("normalized_title", sa.String),
        sa.column("recommendation_moods", sa.JSON),
    )
    if existing_tmdb_ids:
        op.bulk_insert(
            films_table,
            [
                {
                    "source_key": "legacy-tmdb",
                    "external_id": str(tmdb_id),
                    "tmdb_id": tmdb_id,
                    "title_ja": None,
                    "original_title": None,
                    "synopsis_ja": None,
                    "release_date": None,
                    "runtime_minutes": None,
                    "genres": [],
                    "directors": [],
                    "cast_members": [],
                    "poster_path": None,
                    "streaming_platforms": [],
                    "streaming_region": "JP",
                    "streaming_updated_at": None,
                    "normalized_title": f"tmdb{tmdb_id}",
                    "recommendation_moods": [],
                }
                for tmdb_id in existing_tmdb_ids
            ],
        )

    op.add_column(
        "viewing_history_entries",
        sa.Column("film_id", sa.Integer(), nullable=True),
    )
    bind.execute(
        sa.text(
            """
            UPDATE viewing_history_entries
            SET film_id = (
                SELECT films.id
                FROM films
                WHERE films.tmdb_id = viewing_history_entries.tmdb_id
            )
            """
        )
    )
    op.create_foreign_key(
        "fk_viewing_history_entries_film_id",
        "viewing_history_entries",
        "films",
        ["film_id"],
        ["id"],
    )
    op.create_index(
        "ix_viewing_history_entries_film_id",
        "viewing_history_entries",
        ["film_id"],
        unique=False,
    )
    op.alter_column("viewing_history_entries", "film_id", nullable=False)
    op.alter_column("viewing_history_entries", "tmdb_id", nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    local_only_count = bind.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM viewing_history_entries AS history
            JOIN films ON films.id = history.film_id
            WHERE films.tmdb_id IS NULL
            """
        )
    ).scalar_one()
    if local_only_count:
        raise RuntimeError(
            "ローカル専用映画の視聴記録があります。"
            "JSONへ退避してからダウングレードしてください。"
        )
    bind.execute(
        sa.text(
            """
            UPDATE viewing_history_entries
            SET tmdb_id = (
                SELECT films.tmdb_id
                FROM films
                WHERE films.id = viewing_history_entries.film_id
            )
            """
        )
    )
    op.alter_column("viewing_history_entries", "tmdb_id", nullable=False)
    op.drop_constraint(
        "fk_viewing_history_entries_film_id",
        "viewing_history_entries",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_viewing_history_entries_film_id",
        table_name="viewing_history_entries",
    )
    op.drop_column("viewing_history_entries", "film_id")
    op.drop_index("ix_films_normalized_title", table_name="films")
    op.drop_table("films")
    op.drop_table("film_data_sources")
    op.drop_constraint("uq_tags_key", "tags", type_="unique")
    op.drop_column("tags", "description_ja")
    op.drop_column("tags", "display_name_ja")
    op.drop_column("tags", "key")
