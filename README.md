# 🎬 Film-like

> A personal film diary and AI-powered recommendation engine.<br>
> Log what you watch, rate it your way, and get suggestions based on your mood and streaming platforms.

![Status]
![Python]
![FastAPI]
![React]
![PostgreSQL]

---

## Table of Contents

- [🎬 Film-like](#-film-like)
  - [Table of Contents](#table-of-contents)
  - [About the Project](#about-the-project)
  - [Features](#features)
    - [Film Logging](#film-logging)
    - [Original Rating System](#original-rating-system)
    - [Mood-Based Recommendation Engine](#mood-based-recommendation-engine)
    - [Personal Dashboard](#personal-dashboard)
  - [Tech Stack](#tech-stack)
  - [Architecture](#architecture)
  - [Database](#database)
  - [Project Structure](#project-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [One time installation](#one-time-installation)
      - [Clone the repository](#clone-the-repository)
      - [Run the setup script](#run-the-setup-script)
    - [Each working session](#each-working-session)
    - [Cleaning the project](#cleaning-the-project)
  - [API Overview](#api-overview)
  - [Git Workflow](#git-workflow)
    - [Branch Strategy](#branch-strategy)
    - [Step-by-step workflow for each issue](#step-by-step-workflow-for-each-issue)
      - [Start a new issue](#start-a-new-issue)
      - [Work and commit regularly](#work-and-commit-regularly)
      - [Before opening a Pull Request](#before-opening-a-pull-request)
      - [Open a Pull Request on GitHub](#open-a-pull-request-on-github)
      - [After the merge](#after-the-merge)
    - [Commit Convention](#commit-convention)
    - [Closing Issues via Commits](#closing-issues-via-commits)
  - [Testing](#testing)
  - [Documentation](#documentation)
    - [Portfolio Project Progress Reports](#portfolio-project-progress-reports)
    - [Technical Diagrams](#technical-diagrams)
    - [UI Prototype](#ui-prototype)
  - [Roadmap](#roadmap)
    - [MVP (current scope)](#mvp-current-scope)
    - [Future versions](#future-versions)
  - [Author](#author)

---

## About the Project

Film-like was born out of a simple frustration: choosing what to watch is harder than it should be.

Existing tools like Letterboxd or IMDb let you rate films - but they rarely combine your personal taste, your current mood, and what you actually have access to on your streaming subscriptions.

Film-like is different. It acts as a personal film companion that:
- Remembers everything you have watched and how you felt about it
- Uses your mood as a starting point, not an afterthought
- Only recommends films you can actually watch tonight

This project is the end-of-year portfolio project for the Bachelor CDA program at Holberton School Bordeaux.

---

## Features

### Film Logging

🎞️ **The tool lets users add movies to personal “watched” or “to-watch” lists**
- Search for any film by title (powered by the TMDB API)
- Add it to your viewing history or watchlist
- Log it with emotional and contextual tags instead of a simple star rating

### Original Rating System

🏷️ **The tool lets users rate films with tags that actually mean something**:
| Tag | Meaning |
|---|---|
| Great with a group | Best experienced with others |
| Perfect background watch | Can scroll while it's on |
| Emotional wreck | Unexpectedly moving |
| Guilty pleasure | Bad but you loved it |
| Mind blowing | Changed how you think |
| Needs full attention | Do not disturb |
| Would rewatch immediately | Says it all |
| Instant classic | Timeless |

Optionally assign a prestige tier: **Platinum / Gold / Silver / Bronze / Trash**

### Mood-Based Recommendation Engine

🎭 **The tool provides personalized AI-powered recommendations through a comprehensive user experience**
- Answer a short mood questionnaire
- Swipe through film cards (right = interested, left = not interested)
- Optionally add a custom prompt
- Receive a curated list of personalised recommendations
- Filtered by the streaming platforms you actually have

### Personal Dashboard
📋 **The tool allows users to keep track of the movies they've watched and the emotional impact they had on them at the time of viewing**
- View your full watching history
- Browse your watchlist
- See your tags and tiers at a glance

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Frontend | React 19 + Tailwind CSS | Component-based UI, responsive design |
| Routing | React Router | Client-side navigation |
| Backend | Python 3.11 + FastAPI | REST API, business logic, async support |
| Database | PostgreSQL 16 | Relational data persistence |
| Authentication | JWT | Stateless user authentication |
| Film data | TMDB API | Film metadata, posters, streaming availability |
| AI recommendations | Mistral AI | Mood-based LLM recommendation engine |
| Testing | pytest + pytest-cov | Unit and integration tests |
| Version control | Git + GitHub | Source control and project history |

---

## Architecture

The application follows a classic three-tier architecture separating the presentation layer, business logic, and data layer.<br>
External services (TMDB and Mistral AI) are called exclusively by the backend — never directly by the frontend.

→ [View Architecture Diagrams](docs/diagrams/Architecture.md)

---

## Database

Film-like uses PostgreSQL as its relational database. Film metadata is not stored locally — only the `tmdb_id` is persisted, and full film details are fetched from TMDB on demand.

→ [View Entity Relationship Diagram](docs/diagrams/ERDiagram.md)

---

## Project Structure

```
PORTFOLIO/
├── README.md
├── docker-compose.yml
├── clean.sh
├── setup.sh
├── start.sh
├── docs/
│   └── diagrams/
│       ├── Architecture.md
│       ├── ClassDiagram.md
│       ├── ERDiagram.md
│       └── SequenceDiagrams.md   
└── frontend/               
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── FilmCard/
│       │   ├── TagSelector/
│       │   ├── PlatformSelector/
│       │   ├── SwipeDeck/
│       │   └── NavBar/
│       ├── pages/
│       │   ├── AuthPage/
│       │   ├── DashboardPage/
│       │   ├── CatalogPage/
│       │   ├── FilmDetailPage/
│       │   ├── RecommendationPage/
│       │   └── ProfilePage/
│       └── services/
│           └── api.js
└── backend/
    ├── alembic/
    ├── app/
    │   ├── main.py
    │   ├── database.py
    │   ├── models/
    │   ├── routes/
    │   ├── services/
    │   └── repositories/
    ├── tests/
    ├── requirements.txt
    └── .env.example
```

---

## Getting Started

### Prerequisites

Before running the setup script, make sure the following tools are installed:

- Python >= 3.11
- Node.js >= 18
- Docker Engine with Docker Compose v2
- A [TMDB API key] *(required from Sprint 2)*
- A [Mistral AI API key] *(required from Sprint 5)*

> The setup script checks that Python, Node.js, Docker, and Docker Compose are available.  
> It also creates the virtual environment, installs project dependencies, creates local `.env` files, and starts the PostgreSQL container.

If Docker is not installed on Ubuntu, you can install it with:
```bash
sudo apt update
sudo apt install ca-certificates curl -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Then log out and log back in before running:
```bash
./setup.sh
```

### One time installation

#### Clone the repository

#### Run the setup script

Run **`setup.sh`** to initialize the project in one command.<br>
This script handles everything in one command, for Frontend and Backend initialization:
- Checks Python 3.11+, Node.js 18+, Docker, and Docker Compose are available
- Creates the Python virtual environment into backend directory
- Installs all backend dependencies
- Installs all frontend dependencies
- Creates your `.env` files from `.env.example`
- Starts the PostgreSQL container via Docker

```bash
./setup.sh
```

### Each working session

- **Activate the virtual environment**
```bash
source backend/venv/bin/activate
```

- **Start both servers (frontend + backend)**
```bash
./start.sh
```

The app will be available at `http://localhost:5173` *(frontend - Sprint 2)*
The API will be available at `http://localhost:8000`
The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

### Cleaning the project

From time to time, you can run the clean script to remove generated files and temporary caches:
```bash
./clean.sh
```

This script removes common development artifacts such as:
- Python cache files (`__pycache__`, `.pyc`, `.pyo`)
- pytest cache and coverage reports
- frontend build artifacts (`dist`, `dist-ssr`)
- OS-generated files such as (`.DS_Store`, `Thumbs.db`)

For a complete reset of the local development environment, use:
```bash
./clean.sh --hard
```

**Caution: hard mode removes reinstallable local files**:
- `backend/venv`
- `frontend/node_modules`
- backend and frontend `.env` files

> ⚠️ **Note:** Do not run `./clean.sh --hard` while the virtual environment is active.<br>
Run `deactivate` first.

---

## API Overview

> Full API specification is available in the [Stage 3 Technical Documentation]

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /auth/register | Create a new user account | ❌ |
| POST | /auth/login | Log in and receive a JWT token | ❌ |
| GET | /films/search | Search for a film by title | ✅ |
| GET | /films/{tmdb_id} | Get film details and user status | ✅ |
| POST | /films/log | Log a watched film with tags | ✅ |
| DELETE | /films/log/{entry_id} | Remove a film from history | ✅ |
| GET | /films/history | Retrieve the user's viewing history | ✅ |
| POST | /films/watchlist | Add a film to the watchlist | ✅ |
| DELETE | /films/watchlist/{tmdb_id} | Remove a film from the watchlist | ✅ |
| GET | /films/watchlist | Retrieve the user's watchlist | ✅ |
| GET | /users/me | Get current user profile | ✅ |
| PATCH | /users/me | Update user profile | ✅ |
| GET | /users/me/platforms | Get platform preferences | ✅ |
| PUT | /users/me/platforms | Update platform preferences | ✅ |
| POST | /recommendations/start | Get mood-based recommendations | ✅ |

> ✅ Requires authentication — a valid JWT token must be included in the `Authorization: Bearer <token>` header.<br>
> ❌ Public endpoint — no authentication required.

---

## Git Workflow

### Branch Strategy

```
main        → stable, production-ready code
develop     → integration branch
feature/*   → one branch per issue, created from develop
fix/*       → bug fixes, created from develop
```

### Step-by-step workflow for each issue

#### Start a new issue

Always start from an up-to-date develop:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/s1-2-frontend-setup
```

#### Work and commit regularly

```bash
# Stage your changes
git add .

# Commit with a conventional message
git commit -m "chore(frontend): initialize React project with Vite"
```

#### Before opening a Pull Request

Sync with develop to catch any changes made in the meantime:

```bash
git fetch origin
git merge origin/develop
# If nano opens for the merge commit message: Ctrl+X then Enter
```

Then push your branch:

```bash
git push origin feature/s1-2-frontend-setup
```

#### Open a Pull Request on GitHub

- Go to your repository on GitHub
- Click **New Pull Request**
- Set `base: develop` ← `compare: feature/s1-2-frontend-setup`
- Add a title and description
- Click **Merge Pull Request**

#### After the merge

Back in your terminal — never merge locally, always pull:

```bash
git checkout develop
git pull origin develop

# Delete the feature branch locally
git branch -d feature/s1-2-frontend-setup

# Delete it on GitHub
git push origin --delete feature/s1-2-frontend-setup
```

### Commit Convention

This project follows the [Conventional Commits]
specification:

```
<type>(<scope>): <short description>
```

| Type | Usage |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code change without feature or fix |
| `chore` | Setup, config, dependencies |
| `style` | Formatting, missing semicolons, etc... |

**Examples:**
```bash
feat(auth): add JWT token generation on registration
fix(films): correct TMDB search query encoding
docs(readme): update setup instructions
test(users): add unit tests for validate_email
chore(backend): add alembic migration for users table
```

### Closing Issues via Commits

Each commit that completes an issue should reference it:

```bash
git commit -m "feat(auth): add user registration endpoint (closes #3)"
```

This automatically closes the issue and moves it to `Done` on the GitHub Projects board.

---

## Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run a specific test file
pytest tests/test_auth.py -v
```

Target: **minimum 50% coverage** on the backend codebase, focusing on the service layer and critical endpoints.

---

## Documentation

All project documentation is managed as part of the portfolio creation process:

### Portfolio Project Progress Reports

- [Stage 1 - Team Formation, Brainstorming, MVP]
  > Definition of individual projects, brainstorming, evaluation of ideas using MoSCoW, and selection of the final MVP, including scope, SMART goals, and risk analysis.
- [Stage 2 - Project Plan]
  > An overview of the five-stage project plan, a detailed breakdown by phase, a timeline overview, a summary of SMART goals, and an overview of key risks.
- [Stage 3 - Technical Documentation]
  > Completed technical design documents: user stories (MoSCoW), system architecture, class diagrams, ER diagrams, API specifications (internal and external), React component architecture, UI mockups, sequence diagrams, SCM and QA strategies, and rationale for the selection of the overall technology stack.

### Technical Diagrams

- [Architecture Diagrams]
  > High-level overview and detailed component architecture showing how the frontend, backend, database, and external services interact. Includes design patterns (Repository, Facade, REST).
- [Class Diagram]
  > Backend business logic layer: all persistent entities (User, WatchlistEntry, ViewingHistoryEntry), the Film DTO, Tag, Platform, and PrestigeTier enumeration with attributes, methods, and UML relationships.
- [Entity Relationship Diagram]
  > PostgreSQL database schema with all tables, columns, primary/foreign keys, and relationship summary. Includes design notes on UUID vs integer IDs and the absence of a local films table.
- [Sequence Diagrams])
  > Step-by-step interaction flows for the 5 key use cases: user registration, user login, film search, film logging, and the full mood-based recommendation experience.

### UI Prototype

- [Figma Interactive Prototype]
  > Navigable mockup covering all main screens: dashboard, authentication, film catalog, mood questionnaire, swipe interface, recommendation results, and user profile.

---

## Roadmap

### MVP (current scope)
- [x] Project planning and technical documentation
- [x] User authentication (Sprint 1)
- [ ] Film search and logging with tags (Sprint 2)
- [ ] Watchlist and personal dashboard (Sprint 3)
- [ ] Mood questionnaire and swipe interface (Sprint 4)
- [ ] AI-powered recommendations via Mistral AI (Sprint 5)
- [ ] Streaming availability display (Sprint 5)

### Future versions
- [ ] Guest mode - full navigation (search, recommendations) without an account, with a sign-up prompt at the end of the recommendation flow to save results
- [ ] French language support
- [ ] Social features (follow users, shared lists)
- [ ] Cinema listings and nearby showtimes
- [ ] Native mobile application
- [ ] Export viewing history

---

## Author

**zahin - dev**
University: Kanagawa Institute of Technology  
Faculty: Faculty of Information Technology  
Deapartment：Department of Information Systems   
Year: 3rd Year Undergraduate Student  
E-mail: islam.zahin.0116@gmail.com  

- GitHub: [@zahin-dev](https://github.com/zahin-dev)

---
