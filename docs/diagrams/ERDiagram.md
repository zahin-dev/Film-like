# Film-like - Entity Relationship Diagram

This diagram shows the database after the current Alembic head. TMDB remains the source of truth for every film metadata field; Film-like persists only the TMDB identifier for film identity.

## Current Database Schema

```mermaid
erDiagram
    users {
        uuid id PK
        varchar first_name
        varchar last_name
        varchar username
        varchar email UK
        varchar hashed_password
        boolean is_admin
        integer age "nullable"
        timestamp created_at
        timestamp updated_at
    }

    viewing_history_entries {
        uuid id PK
        uuid user_id FK
        integer tmdb_id
        prestigetier prestige_tier "nullable"
        text personal_note "nullable"
        timestamp created_at
        timestamp updated_at
    }

    tags {
        integer id PK
        varchar name UK
        varchar description
    }

    viewing_history_tags {
        uuid viewing_history_entry_id PK,FK
        integer tag_id PK,FK
    }

    users ||--o{ viewing_history_entries : owns
    viewing_history_entries ||--o{ viewing_history_tags : has
    tags ||--o{ viewing_history_tags : labels
```

## Table Responsibilities

### `users`

Stores registration and authentication data, optional age, and reserved admin status. Email is unique. Only bcrypt password hashes are stored.

### `viewing_history_entries`

Stores the minimum film reference (`tmdb_id`) plus user-owned reaction data. The table deliberately has no `title`, `poster_url`, synopsis, genre, cast, director, runtime, provider, or foreign key to a local film entity.

`GET /films/history` retrieves title and poster data from TMDB concurrently. Display metadata can therefore change with TMDB and may be null for an individual item when enrichment fails; the database row remains intact.

### `tags`

Stores application-managed reaction tags seeded by `backend/seeds/seed_tag.py`.

### `viewing_history_tags`

Implements the many-to-many entry/tag relationship. Its composite primary key prevents the same tag association from being inserted twice for one entry.

`GET /insights` derives diary signals from these user-owned associations at request time. It creates no insight, emotion, profile, or analytics table. Percentages are explainable shares of tagged films, not inferred sentiment or clinical analysis.

## Migration State

The Alembic chain preserves the historical migration that added nullable title/poster cache columns. Revision `b3d91f6a2c04` follows it and drops those columns in `upgrade()`. Its `downgrade()` restores both as nullable text columns. Earlier migrations were not rewritten.

## Relationship Summary

| Relationship | Type | Storage |
|---|---|---|
| User to viewing-history entry | One-to-many | `viewing_history_entries.user_id` → `users.id` |
| Viewing-history entry to tag | Many-to-many | `viewing_history_tags` join table |

## Prestige Tier Values

`Platinum`, `Gold`, `Silver`, `Bronze`, `Coal`, and `Trash` are stored through the PostgreSQL `prestigetier` enum.

## Scope Boundaries

The current schema has no local `films`, `watchlist_entries`, `platforms`, `user_platforms`, recommendation, social, or payment tables. Mistral output is transient and is never persisted. Watchlists and platform preferences remain future roadmap ideas, not current database entities.

For each recommendation request, the facade reads the authenticated user's current tag associations and combines their frequencies with the selected mood. The context therefore updates as stored diary tags increase, but no model training, online learning, fine-tuning, feedback learning, or automated prompt optimization is stored in this schema.

Mistral is asked for strict JSON Schema output, which is then validated with Pydantic. Malformed candidates can occur and are rejected; the facade retries at most once and returns controlled errors if necessary. Only TMDB-resolved recommendation results reach the UI, and neither raw AI output nor recommendation results are persisted.

## Project Attribution

Film-like is jointly owned, developed, and maintained by a three-person team.

- Repository host and public contact: [@zahin-dev](https://github.com/zahin-dev)
- Hosting under this account is for administrative convenience and does not indicate sole ownership or sole authorship.
