# Film-like

Film-like is a working end-to-end film-diary MVP. A user can register, sign in, search TMDB, inspect a film, record tags/tier/notes, revisit enriched viewing history, review deterministic diary reaction signals, and request mood-based recommendations from Mistral AI. AI candidates are validated, filtered, and resolved through TMDB before they reach the UI.

This repository demonstrates an MVP architecture; it is not a production-ready service. Live film features depend on TMDB, and live recommendations additionally require a Mistral API key.

## Core MVP Flow

```text
authentication
  -> TMDB search
  -> protected film details
  -> viewing-history log or removal
  -> TMDB-enriched diary display
  -> selected-tag diary insights
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
| Diary insights | Authenticated deterministic aggregation of user-selected tags | Explainable totals, top/recent reaction signals, accessible bars, loading/empty/error/retry states |
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

Malformed model output can still occur. The facade requests strict JSON Schema output, validates the response with Pydantic, rejects malformed candidates, retries at most once, and returns a controlled error if it cannot produce enough verified results. This boundary prevents malformed AI candidates from reaching the UI; it does not claim that malformed upstream output is impossible.

The recommendation service reads the authenticated user's stored diary on every request. As the user adds selected reaction tags, the tag-frequency context supplied with the current mood updates dynamically. This is request-time context assembly, not machine learning, online learning, fine-tuning, automated prompt optimization, or recommendation-quality feedback learning.

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
    -> FastAPI auth / film / tag / insight / recommendation routes
    -> authentication / film / viewing-history / insight services
    -> Recommendation Facade
    -> repositories -> PostgreSQL
    -> TMDB client -> TMDB API
    -> Mistral client -> official Mistral API
```

Routes handle HTTP concerns, services coordinate business behavior, repositories isolate database access, and external clients isolate outbound HTTP. See [System Architecture](docs/diagrams/Architecture.md), [Class Diagram](docs/diagrams/ClassDiagram.md), [ER Diagram](docs/diagrams/ERDiagram.md), and [Sequence Diagrams](docs/diagrams/SequenceDiagrams.md).

The team's retrospective development context and current implementation evidence are separated in the [Development Process Retrospective](docs/DevelopmentProcess.md). Reproducible checks and the manual live-verification boundary are recorded in [Verification Evidence](docs/Verification.md).

## Development Context

Film-like is jointly owned, developed, and maintained by a three-person team. The repository is hosted under the `zahin-dev` GitHub account for administrative convenience and as a public contact point; this hosting arrangement does not indicate sole project ownership or sole authorship.

The team built the initial MVP over approximately three months and continues to develop and improve the application with the same three members.

The members have the following primary responsibilities:

- one member primarily leads backend design and implementation, including API contracts, authentication, database integration, external-service integration, and the Mistral-based recommendation flow;
- one member primarily leads frontend development, including screens, input forms, buttons, user interactions, and client-side communication with backend APIs; and
- one member primarily leads infrastructure and project-wide coordination, including server setup, deployment, cloud configuration, CI/CD, testing, and system-design support.

These responsibilities are not exclusive. All three members contribute across role boundaries through implementation, review, debugging, testing, verification, design discussions, documentation, and improvement work. The team uses GitHub to iteratively implement, review, revise, test, and improve the application through feedback and collaborative trial and error.

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
├── scripts/              # Reproducible metrics and English public-text audit
└── docs/                 # Evidence notes and current diagrams
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

`docker-compose.yml` provides a reproducible PostgreSQL 16 development environment with a named persistent volume and a `pg_isready` healthcheck. It is development configuration, not a production database deployment. Validate the resolved configuration without starting or deleting the volume:

```bash
docker compose config
```

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
| GET | `/insights` | Aggregate the user's selected diary reaction tags | Bearer token |
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

See [Verification Evidence](docs/Verification.md) for the recorded command results, coverage, environment checks, and the scope of manual live verification.

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

Public Markdown plus backend/frontend source comments and docstrings can be audited with:

```bash
python scripts/check_english_public_text.py
```

## Reproducible Project Metrics

Run the following from the repository root:

```bash
python scripts/project_metrics.py
```

The script counts physical UTF-8 lines, including blank and comment-only lines, without hard-coded totals. It excludes virtual environments, dependencies, caches, coverage output, and build output. Frontend source totals include text-based source files under `frontend/src`; total backend Python includes application code, tests, migrations, Alembic support, and seeds.

The current measured result is 48 backend Python files and 4,429 physical lines. That measurement supports describing the current checkout as several thousand backend lines. It does not establish the size of the initial approximately three-month MVP phase, which was followed by continued development by the same three-person team. The category-level totals are recorded in [Verification Evidence](docs/Verification.md).

## MVP Boundaries and Roadmap

Current limitations are explicit:

- This is an MVP, not a production-ready deployment.
- Profile information is read-only in the UI because no profile-update API exists.
- Watchlists, social features, shared lists, platform-preference storage, payments, and subscription filtering are not implemented.
- TMDB watch-provider names are informational and are not user subscriptions.
- External service availability and generated recommendation quality vary outside the mocked test suite.

Possible future work includes watchlists, profile editing, stored platform preferences, shared lists, additional languages, cinema listings, mobile clients, and viewing-history export.

## Repository Contact

Film-like is jointly owned, developed, and maintained by all three team members. The `zahin-dev` account hosts this repository for administrative convenience and serves as its public contact point; it does not represent sole ownership or sole authorship.

**zahin-dev**

- University: Kanagawa Institute of Technology
- Faculty: Faculty of Information Technology
- Department: Department of Information Systems
- Year: 3rd Year Undergraduate Student
- E-mail: islam.zahin.0116@gmail.com
- GitHub: [@zahin-dev](https://github.com/zahin-dev)
