# Film-like - System Architecture

This document separates the architecture represented by the current source tree from the product's planned architecture. A component appearing in the planned section must not be interpreted as implemented.

## Current Architecture

The current source contains a React frontend, FastAPI route and service layers, SQLAlchemy repositories backed by PostgreSQL, and a TMDB client.

The authentication page is implemented. The dashboard, catalog, film-detail, recommendation, and profile routes exist in React Router but currently render placeholder components.

```mermaid
flowchart LR
    User["Browser user"]

    subgraph Frontend["React frontend"]
        AuthPage["Authentication page"]
        Router["React Router"]
        Placeholders["Placeholder pages<br/>dashboard, catalog, film detail,<br/>recommendations, profile"]
        AuthContext["Auth context and Axios client"]
    end

    subgraph Backend["FastAPI backend source"]
        subgraph Routes["Registered routes"]
            RootRoute["GET /"]
            AuthRoutes["POST /auth/register<br/>POST /auth/login"]
            FilmRoutes["GET /films/search<br/>GET /films/history<br/>GET /films/{tmdb_id}<br/>POST /films/log<br/>DELETE /films/log/{tmdb_id}"]
            TagRoutes["GET /tags"]
        end

        subgraph Services["Services"]
            AuthService["Authentication service"]
            FilmService["Film service"]
            HistoryService["Viewing-history service"]
        end

        subgraph Repositories["Repositories"]
            UserRepository["User repository"]
            HistoryRepository["Viewing-history repository"]
        end

        TMDBClient["TMDB client"]
    end

    PostgreSQL[("PostgreSQL")]
    TMDB["TMDB API"]

    User -. "direct health check" .-> RootRoute
    User --> Router
    Router --> AuthPage
    Router --> Placeholders
    AuthPage --> AuthContext
    AuthContext --> AuthRoutes
    AuthContext -. "available to future page integrations" .-> FilmRoutes
    AuthRoutes --> AuthService
    FilmRoutes --> FilmService
    FilmRoutes --> HistoryService
    TagRoutes --> HistoryService
    AuthService --> UserRepository
    HistoryService --> HistoryRepository
    FilmService --> HistoryRepository
    FilmService --> TMDBClient
    HistoryService --> TMDBClient
    UserRepository --> PostgreSQL
    HistoryRepository --> PostgreSQL
    TMDBClient --> TMDB
```

### Current Component Responsibilities

| Component | Current responsibility |
|---|---|
| Root route | Return a basic API health/status message |
| React authentication page | Submits registration and login requests, displays API errors, and redirects after authentication |
| Auth context and Axios client | Stores the JWT in session storage and adds it to outgoing requests |
| Auth routes and service | Register users, hash and verify passwords, and issue JWT access tokens |
| Film routes and service | Search TMDB, retrieve complete film details and watch-provider names, and report `in_history` status |
| Tag route | Return application-managed reference tags |
| Viewing-history service | Create, list, and remove history entries; resolve tags; cache title and poster URL at log time |
| User repository | Read and create users |
| Viewing-history repository | Read tags and create, query, or delete viewing-history entries |
| PostgreSQL | Store users, tags, viewing-history entries, and tag associations |
| TMDB API | Provide complete film metadata and watch-provider data |

The source follows service and repository separation: routes handle HTTP concerns, services coordinate business logic and external calls, and repositories perform database access. There is no Recommendation Facade in the current source.

> **Repository completeness note:** current route and service modules import `app.schemas`, but the package is absent from the current Git tree. The diagram reflects the checked-in route, service, repository, model, migration, frontend, and test source; it does not claim a successfully importable runtime in this checkout.

## Target Architecture - Planned, Not Current

The following diagram is a product target only. None of the watchlist, profile, platform-preference, recommendation, or Mistral components shown here exist as working backend source in the current repository.

```mermaid
flowchart LR
    WorkingUI["Completed React pages<br/>dashboard, catalog, film detail,<br/>profile, mood and swipe flows"]

    subgraph PlannedBackend["Planned backend components - not implemented"]
        WatchlistAPI["Watchlist API and service"]
        ProfileAPI["Profile and platform-preference API"]
        RecommendationAPI["Recommendation routes"]
        RecommendationFacade["Recommendation Facade"]
        PlannedRepos["Watchlist and platform repositories"]
    end

    PlannedTables[("Planned watchlist and<br/>platform-preference tables")]
    Mistral["Mistral AI"]
    TMDBFuture["TMDB API"]

    WorkingUI --> WatchlistAPI
    WorkingUI --> ProfileAPI
    WorkingUI --> RecommendationAPI
    WatchlistAPI --> PlannedRepos
    ProfileAPI --> PlannedRepos
    PlannedRepos --> PlannedTables
    RecommendationAPI --> RecommendationFacade
    RecommendationFacade --> Mistral
    RecommendationFacade --> TMDBFuture
```

Planned behavior includes:

- Watchlist creation, retrieval, deletion, and conversion to viewing history
- Profile management and stored streaming-platform subscriptions
- A mood questionnaire and swipe interface
- Recommendation routes backed by a Recommendation Facade
- Mistral AI calls and recommendation enrichment through TMDB
- Recommendation filtering based on stored platform subscriptions

## Author

**zahin-dev**

- University: Kanagawa Institute of Technology
- GitHub: [@zahin-dev](https://github.com/zahin-dev)
