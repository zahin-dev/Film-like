# Film-like

Film-like is a working end-to-end film-diary MVP. A user can register, sign in, search TMDB, inspect a film, record tags/tier/notes, revisit enriched viewing history, and request mood-based recommendations from Mistral AI. AI candidates are validated, filtered, and resolved through TMDB before they reach the UI.

This repository demonstrates an MVP architecture; it is not a production-ready service. Live film features depend on TMDB, and live recommendations additionally require a Mistral API key.

## Core MVP Flow

```text
authentication
  -> TMDB search
  -> protected film details
  -> viewing-history log or removal
  -> TMDB-enriched diary display
  -> mood + history-tag recommendation context
  -> Mistral structured candidates
  -> TMDB verification
  -> recommendation deck
```

## Implemented Features

| Area | Backend | Frontend |
|---|---|---|
| Authentication | Registration, login, bcrypt hashes, HS256 JWT validation | Accessible registration/login forms, session state, protected routes, logout |
| Film catalog | TMDB search, details, credits, runtime, genres, posters, and French watch-provider names | Search states, result cards, protected detail view |
| Viewing history | Create, list, and delete user-owned records | Diary cards, tags, prestige tier, notes, dates, retry/empty/error states |
| Reactions | Seeded tags, optional `PrestigeTier`, optional personal note | Tag picker, tier selector, note input, log/remove state updates |
| Recommendations | Authenticated `POST /recommendations`, Mistral JSON Schema output, Recommendation Facade, TMDB verification | Eight documented mood choices, reasons, next/skip interaction, retry/exhausted states |
| Profile | Public user fields returned by authentication | Read-only profile and logout; no invented edit API |
| Automation | Mock-only backend tests and GitHub Actions | CI runs `npm ci`, lint, and production build |

The Pydantic v2 schema package is present under `backend/app/schemas`, application imports succeed with valid environment settings, and tests use isolated configuration rather than a developer's private `.env`.

## Recommendation Design

The service-layer Recommendation Facade isolates routes and frontend code from external AI communication. For each request it:

1. reads the authenticated user's viewing history;
2. counts history tags and resolves recent viewed titles where possible;
3. combines that context with the selected mood;
4. requests strict JSON Schema output from Mistral's chat-completions API;
5. parses candidates through strict Pydantic models;
6. rejects malformed, empty, duplicate, and unreasonable candidates;
7. searches TMDB by candidate title and prefers a supplied year match;
8. excludes watched and duplicate TMDB IDs; and
9. returns only verified `Film` objects with concise reasons.

Structured-output or resolution shortfalls receive at most one retry. Missing configuration, timeouts, connection failures, rejected credentials, rate limits, malformed output, and insufficient verified results are mapped to controlled API errors without exposing keys, authorization headers, or internal prompts.

Supported moods are `relaxed`, `uplifting`, `excited`, `thoughtful`, `emotional`, `romantic`, `adventurous`, and `scared`.

## Data Ownership

TMDB is the source of truth for film metadata. Film-like does not have a local `films` table and persists only `tmdb_id` for film identity. A viewing-history record stores:

- user and TMDB identifiers;
- optional prestige tier and personal note;
- tag associations; and
- timestamps.

Titles and poster URLs are retrieved from TMDB when history is returned. Enrichment requests run concurrently, preserve deterministic database ordering, and retain an entry with null display metadata if an individual TMDB lookup fails.

No synopsis, genre, cast, director, runtime, poster, title, or streaming-provider metadata is persisted locally.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router 7, Axios, Tailwind CSS 4, Vite 8 |
| Backend | Python 3.12, FastAPI, Pydantic v2, httpx |
| Persistence | PostgreSQL 16, SQLAlchemy 2, Alembic |
| Authentication | JWT (HS256), bcrypt |
| Film metadata | TMDB API |
| AI recommendations | Mistral chat-completions API with strict JSON Schema output |
| Verification | pytest, pytest-cov, ESLint, Vite build, GitHub Actions |

## Architecture

```text
React pages + AuthContext + centralized Axios client
    -> FastAPI auth / film / tag / recommendation routes
    -> authentication / film / viewing-history services
    -> Recommendation Facade
    -> repositories -> PostgreSQL
    -> TMDB client -> TMDB API
    -> Mistral client -> official Mistral API
```

Routes handle HTTP concerns, services coordinate business behavior, repositories isolate database access, and external clients isolate outbound HTTP. See [System Architecture](docs/diagrams/Architecture.md), [Class Diagram](docs/diagrams/ClassDiagram.md), [ER Diagram](docs/diagrams/ERDiagram.md), and [Sequence Diagrams](docs/diagrams/SequenceDiagrams.md).

## Project Structure

```text
Portfolio/
├── .github/workflows/ci.yml
├── backend/
│   ├── alembic/versions/
│   ├── app/
│   │   ├── external/       # TMDB and Mistral HTTP clients
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schemas/        # Pydantic request/response contracts
│   │   └── services/       # Includes Recommendation Facade
│   ├── seeds/
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       ├── context/
│       ├── pages/
│       ├── services/
│       └── utils/
└── docs/diagrams/
```

## Getting Started

### Prerequisites

- Python 3.12 (the pinned backend dependencies are verified on 3.12)
- Node.js 20 or newer
- Docker Engine with Docker Compose v2
- TMDB Read Access Token
- Mistral API key for live recommendations only

### Setup

On a supported Bash environment:

```bash
./setup.sh
```

The setup script creates local environment files, installs dependencies, starts PostgreSQL, applies migrations, and seeds tags. Copy values into `backend/.env` from `backend/.env.example`:

```dotenv
DATABASE_URL=postgresql://cinemood:cinemood@localhost:5432/cinemood
SECRET_KEY=replace_with_a_long_random_secret
TMDB_READ_ACCESS_TOKEN=replace_with_your_tmdb_token
MISTRAL_API_KEY=replace_with_your_mistral_key
MISTRAL_MODEL=mistral-small-latest
MISTRAL_API_BASE_URL=https://api.mistral.ai/v1
```

`MISTRAL_API_KEY` is optional for application startup. Without it, all non-recommendation features remain available and `POST /recommendations` returns a clear `503` rather than fabricated recommendations.

Start a development session:

```bash
source backend/venv/bin/activate
./start.sh
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## API Overview

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/` | API health message | Public |
| POST | `/auth/register` | Create an account and return public user data plus JWT | Public |
| POST | `/auth/login` | Validate credentials and return public user data plus JWT | Public |
| GET | `/tags` | List seeded reaction tags | Public |
| GET | `/films/search?query={title}` | Search TMDB | Public |
| GET | `/films/history` | Return user records enriched with current TMDB title/poster | Bearer token |
| GET | `/films/{tmdb_id}` | Return complete TMDB details plus `in_history` | Bearer token |
| POST | `/films/log` | Validate TMDB ID and persist only ID plus user reaction | Bearer token |
| DELETE | `/films/log/{tmdb_id}` | Remove the user's matching history record | Bearer token |
| POST | `/recommendations` | Generate and verify mood-based recommendations | Bearer token |

### Recommendation Contract

Request:

```json
{
  "mood": "thoughtful",
  "limit": 5
}
```

Successful response:

```json
{
  "mood": "thoughtful",
  "history_tags_used": ["Masterpiece", "Emotional Damage"],
  "recommendations": [
    {
      "film": {
        "tmdb_id": 329865,
        "title": "Arrival",
        "year": 2016,
        "genres": null,
        "poster_url": "https://image.tmdb.org/t/p/w500/example.jpg",
        "synopsis": "TMDB synopsis",
        "director": null,
        "cast": null,
        "runtime": null,
        "streaming_platforms": null
      },
      "reason": "A reflective science-fiction story with an emotional core."
    }
  ]
}
```

## Verification

Backend tests use an in-memory SQLite database and mock all TMDB and Mistral calls:

```bash
cd backend
python -m pytest -q
python -m pytest --cov=app
```

Frontend verification uses the committed lockfile:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

The GitHub Actions workflow runs backend pytest and frontend lint/build with dummy configuration values. Passing mock-based tests demonstrates local contracts and error handling; it does not prove that TMDB or Mistral is currently available, that a supplied key is valid, or that every model response will yield enough verifiable films.

## MVP Boundaries and Roadmap

Current limitations are explicit:

- This is an MVP, not a production-ready deployment.
- Profile information is read-only in the UI because no profile-update API exists.
- Watchlists, social features, shared lists, platform-preference storage, payments, and subscription filtering are not implemented.
- TMDB watch-provider names are informational and are not user subscriptions.
- External service availability and generated recommendation quality vary outside the mocked test suite.

Possible future work includes watchlists, profile editing, stored platform preferences, shared lists, additional languages, cinema listings, mobile clients, and viewing-history export.

## Author

**zahin-dev**

- University: Kanagawa Institute of Technology
- Faculty: Faculty of Information Technology
- Department: Department of Information Systems
- Year: 3rd Year Undergraduate Student
- E-mail: islam.zahin.0116@gmail.com
- GitHub: [@zahin-dev](https://github.com/zahin-dev)
