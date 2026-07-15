# Film-like

Film-like is a personal film-diary application under active development. The current repository contains backend source for authentication, TMDB film lookup, tags, and viewing-history management. An AI-assisted recommendation experience is part of the product plan, but it is not implemented in the current source tree.

## Table of Contents

- [Current Status](#current-status)
- [Implemented Features](#implemented-features)
- [Planned or Incomplete Features](#planned-or-incomplete-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Database](#database)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Author](#author)

## Current Status

The backend source implements the main authentication and viewing-history workflows. The frontend implements a login and registration page, authentication state, JWT storage, and API interceptors. The dashboard, catalog, film-detail, recommendation, and profile routes currently render placeholder components.

This is not a complete end-to-end MVP or a production-ready application.

> **Repository completeness note:** the backend modules import an `app.schemas` package, but that package is not present in the current Git tree. The source modules and automated tests describe the implemented backend behavior listed below, but the backend cannot be imported or its tests executed successfully until the missing schema modules are restored.

## Implemented Features

| Area | Backend status | Frontend status |
|---|---|---|
| User registration | Implemented at `POST /auth/register` | Registration mode is implemented on the authentication page |
| User login | Implemented at `POST /auth/login` | Login form, session token storage, and logout state are implemented |
| JWT authentication | Token creation and protected-route validation are implemented | Axios adds the stored Bearer token to requests |
| TMDB film search | Implemented at `GET /films/search` | Catalog page is a placeholder |
| TMDB film details | Implemented at `GET /films/{tmdb_id}` | Film-detail page is a placeholder |
| Viewing history | Create, retrieve, and delete endpoints are implemented | Dashboard/history UI is a placeholder |
| Tags | Seed data, storage, association, and public `GET /tags` endpoint are implemented | Tag-selection UI is not implemented |
| Prestige tier | Optional `PrestigeTier` storage is implemented | Editing UI is not implemented |
| Personal notes | Optional text storage is implemented | Editing UI is not implemented |
| PostgreSQL | SQLAlchemy configuration and Alembic migrations are present | Not applicable |
| Docker database | A PostgreSQL 16 service is configured in `docker-compose.yml` | Not applicable |
| Backend tests | Pytest suites exist for authentication, TMDB-backed film operations, tags, history, and JWT edge cases | Not applicable |

The film-detail backend also requests TMDB watch-provider data and returns subscription provider names for the configured country. This is different from storing a user's subscriptions or filtering recommendations by them; those capabilities are not implemented.

## Planned or Incomplete Features

The following items do not have working source implementations in the current repository:

- Mistral AI integration and AI-generated recommendations
- A Recommendation Facade or `/recommendations` API routes
- Mood questionnaire and swipe interface
- Watchlist model, repository, service, API, and UI
- User profile API and working profile UI
- Stored streaming-platform preferences
- Recommendation filtering by a user's subscribed platforms
- Working dashboard, catalog, film-detail, recommendation, and profile pages
- A complete end-to-end MVP

## Tech Stack

| Layer | Technology | Current role |
|---|---|---|
| Frontend | React 19, React Router, Tailwind CSS, Axios | Authentication page, routing, auth context, and placeholder routes |
| Backend | Python 3.11+, FastAPI | Auth, film, tag, and viewing-history route source |
| Persistence | PostgreSQL 16, SQLAlchemy, Alembic | Users, tags, viewing-history entries, and tag associations |
| Authentication | JWT with HS256, bcrypt | Stateless access tokens and password hashing |
| Film data | TMDB API | Search, details, posters, credits, and watch-provider data |
| Testing | pytest, pytest-cov | Backend API and service behavior tests |
| Planned AI | Mistral AI | Not integrated in the current implementation |

## Architecture

The current implementation follows this architecture:

```text
React frontend
    -> FastAPI auth, film, and tag routes
    -> authentication, film, and viewing-history services
    -> user and viewing-history repositories
    -> PostgreSQL

FastAPI film services
    -> TMDB API
```

Mistral AI, a Recommendation Facade, watchlist components, profile APIs, and platform-preference storage belong to the planned architecture and are not part of the current implementation.

See [System Architecture](docs/diagrams/Architecture.md) for separate current and planned diagrams.

## Database

Film-like uses PostgreSQL as its relational database. TMDB is used as the source of truth for complete film metadata. The application stores the TMDB identifier and caches the film title and poster URL in viewing-history entries so that history lists can be displayed without an additional TMDB request for every item.

A viewing-history entry can also store tags, an optional prestige tier, and an optional personal note. The current schema does not contain watchlist, platform, or user-platform-preference tables.

See the [Entity Relationship Diagram](docs/diagrams/ERDiagram.md).

## Project Structure

```text
Portfolio/
├── README.md
├── docker-compose.yml
├── setup.sh
├── start.sh
├── clean.sh
├── docs/
│   └── diagrams/
│       ├── Architecture.md
│       ├── ClassDiagram.md
│       ├── ERDiagram.md
│       └── SequenceDiagrams.md
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── external/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── seeds/
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── public/
    └── src/
        ├── context/
        ├── pages/
        ├── services/
        ├── App.jsx
        └── main.jsx
```

## Getting Started

### Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- Docker Engine with Docker Compose v2
- A TMDB Read Access Token

The current implementation does not require a Mistral AI key because no Mistral integration exists yet.

### One-time setup

On a supported Bash environment, run:

```bash
./setup.sh
```

The script creates the backend virtual environment, installs backend and frontend dependencies, creates local environment files, starts PostgreSQL, applies migrations, and seeds tags.

Set `TMDB_READ_ACCESS_TOKEN` in `backend/.env` before using TMDB-backed endpoints.

> The missing `backend/app/schemas` package noted under [Current Status](#current-status) currently prevents the backend application from starting after setup.

### Development session

```bash
source backend/venv/bin/activate
./start.sh
```

When the application can start, the configured development URLs are:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Cleaning generated files

```bash
./clean.sh
```

Hard mode additionally removes reinstallable local dependencies and environment files:

```bash
./clean.sh --hard
```

Do not run hard mode while the Python virtual environment is active.

## API Overview

### Implemented API

These are the routes currently registered in `backend/app/main.py` and its included routers.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/` | API health message | Public |
| POST | `/auth/register` | Create a user and return `{ user, token }` | Public |
| POST | `/auth/login` | Validate credentials and return `{ user, token }` | Public |
| GET | `/tags` | List seeded reference tags | Public |
| GET | `/films/search?query={title}` | Search TMDB and return a JSON array of films | Public |
| GET | `/films/history` | Return the authenticated user's viewing-history entries | Bearer token |
| GET | `/films/{tmdb_id}` | Return TMDB film details plus the user's `in_history` status | Bearer token |
| POST | `/films/log` | Create a viewing-history entry and cache its title and poster URL | Bearer token |
| DELETE | `/films/log/{tmdb_id}` | Delete the user's history entry for the specified TMDB film | Bearer token |

### Planned API

No routes for the following areas are registered in the current FastAPI application. Names shown here describe planned resource areas, not a current API contract.

- Watchlist operations
- User profile operations
- Streaming-platform preference operations
- Recommendation operations, including a possible `/recommendations/start` endpoint

## Testing

Backend test files are present under `backend/tests` and use an in-memory SQLite database with mocked TMDB calls.

```bash
cd backend
pytest
```

Optional coverage output:

```bash
pytest --cov=app --cov-report=html
```

The presence of tests does not imply that they pass in every checkout. See the repository completeness note above and the latest validation results reported with the documentation change.

Frontend checks are configured as:

```bash
cd frontend
npm run lint
npm run build
```

## Documentation

- [System Architecture](docs/diagrams/Architecture.md) distinguishes current implementation from target architecture.
- [Class Diagram](docs/diagrams/ClassDiagram.md) documents current model classes and identifies planned concepts separately.
- [Entity Relationship Diagram](docs/diagrams/ERDiagram.md) shows only the tables created by current migrations.
- [Sequence Diagrams](docs/diagrams/SequenceDiagrams.md) separates implemented API flows from planned recommendation flows.

## Roadmap

### Implemented in backend source

- [x] User registration and login logic
- [x] JWT creation and protected-route validation
- [x] TMDB search and film-detail logic
- [x] Viewing-history creation, retrieval, and deletion
- [x] Tag association, prestige tier, and personal-note persistence
- [x] PostgreSQL configuration, migrations, and Docker service
- [x] Backend automated test suites

### Incomplete or planned

- [ ] Restore the missing backend schema modules required by current imports
- [ ] Connect film, tag, and viewing-history APIs to working frontend pages
- [ ] Implement the dashboard, catalog, film-detail, and profile experiences
- [ ] Implement a watchlist
- [ ] Implement user profile and streaming-platform preference APIs
- [ ] Implement the mood questionnaire and swipe interface
- [ ] Integrate Mistral AI and recommendation endpoints
- [ ] Filter recommendations by stored platform subscriptions
- [ ] Complete and validate the end-to-end MVP

### Possible future versions

- Guest mode
- Additional languages
- Social features and shared lists
- Cinema listings and nearby showtimes
- Native mobile application
- Viewing-history export

## Author

**zahin-dev**

- University: Kanagawa Institute of Technology
- Faculty: Faculty of Information Technology
- Department: Department of Information Systems
- Year: 3rd Year Undergraduate Student
- E-mail: islam.zahin.0116@gmail.com

- GitHub: [@zahin-dev](https://github.com/zahin-dev)
