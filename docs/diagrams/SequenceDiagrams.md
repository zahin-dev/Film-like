# Film-like - Sequence Diagrams

This document separates flows supported by current source modules from planned product flows. The implemented film flows below describe backend API behavior; except for authentication, the corresponding frontend pages are still placeholders.

> **Repository completeness note:** the checked-in route, service, repository, model, and test source defines these backend flows, but the imported `app.schemas` package is absent from the current Git tree. Runtime verification is therefore blocked until those schema modules are restored.

## Currently Implemented Flows

### User Registration

The authentication page implements registration. It calls `POST /auth/register`, then performs a separate login call and stores the login token in session storage before navigating to the placeholder dashboard.

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React AuthPage
    participant Route as POST /auth/register
    participant Service as auth_service
    participant Repo as user_repository
    participant DB as Database

    User->>Frontend: Submit registration form
    Frontend->>Route: first_name, last_name, email, password, optional age
    Route->>Service: register_user(payload)
    Service->>Repo: get_by_email(email)
    Repo->>DB: SELECT user by email
    DB-->>Repo: User or no result

    alt Email already registered
        Service-->>Frontend: 409 "Email already registered"
    else Valid new user
        Service->>Service: bcrypt password and generate username
        Service->>Repo: create(User)
        Repo->>DB: INSERT user and commit
        DB-->>Repo: Created user
        Service->>Service: Sign 24-hour JWT
        Service-->>Frontend: 201 {user, token}
        Frontend->>Frontend: Call login and store returned token
        Frontend->>Frontend: Navigate to /dashboard placeholder
    end
```

Request-schema validation failures are handled by FastAPI/Pydantic as `422 Unprocessable Entity`. The service explicitly handles duplicate email addresses as `409 Conflict`.

### User Login

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React AuthPage and AuthContext
    participant Route as POST /auth/login
    participant Service as auth_service
    participant Repo as user_repository
    participant DB as Database

    User->>Frontend: Submit email and password
    Frontend->>Route: {email, password}
    Route->>Service: login_user(payload)
    Service->>Repo: get_by_email(email)
    Repo->>DB: SELECT user by email
    DB-->>Repo: User or no result

    alt User missing or password wrong
        Service-->>Frontend: 401 "Invalid credentials"
    else Credentials valid
        Service->>Service: Sign 24-hour JWT
        Service-->>Frontend: 200 {user, token}
        Frontend->>Frontend: Store token in sessionStorage
        Frontend->>Frontend: Navigate to /dashboard placeholder
    end
```

Both authentication failures return the same message to avoid revealing whether an email address is registered.

### TMDB Film Search

`GET /films/search?query={title}` is public. The catalog page does not yet call it.

```mermaid
sequenceDiagram
    actor Client
    participant Route as GET /films/search
    participant Service as film_service
    participant TMDBClient as tmdb_client
    participant TMDB as TMDB API

    Client->>Route: query=film title
    Route->>Service: search_films(query)
    Service->>TMDBClient: search_movie(query)
    TMDBClient->>TMDB: GET /search/movie

    alt TMDB HTTP or network error
        TMDB-->>Route: Error propagated through client and service
        Route-->>Client: 503 Service Unavailable
    else TMDB responds
        TMDB-->>TMDBClient: results array
        TMDBClient-->>Service: raw movie objects
        Service->>Service: Map id, title, year, poster URL, synopsis
        Service-->>Route: Film list
        Route-->>Client: 200 JSON array
    end
```

A missing or empty query is rejected with `422 Unprocessable Entity` by FastAPI validation.

### TMDB Film Details and History Status

`GET /films/{tmdb_id}` requires a Bearer token. It retrieves complete TMDB details and subscription watch-provider names for the TMDB client's configured country, then checks only whether the film exists in the authenticated user's viewing history. It does not check a watchlist.

```mermaid
sequenceDiagram
    actor Client
    participant Auth as JWT dependency
    participant Route as GET /films/{tmdb_id}
    participant Service as film_service
    participant TMDB as TMDB API
    participant Repo as viewing_history_repository
    participant DB as Database

    Client->>Auth: Bearer token
    Auth->>DB: Load user from JWT subject
    DB-->>Auth: Authenticated user
    Auth->>Route: current_user
    Route->>Service: get_film_with_status(user, tmdb_id)
    Service->>TMDB: GET movie details with credits
    TMDB-->>Service: Film metadata
    Service->>TMDB: GET watch providers
    TMDB-->>Service: Country provider data
    Service->>Repo: get_by_user_and_tmdb(user.id, tmdb_id)
    Repo->>DB: SELECT viewing-history entry
    DB-->>Repo: Entry or no result
    Service-->>Client: 200 {film, in_history}
```

TMDB `404` responses become an API `404`. Other TMDB HTTP failures and network failures become `503 Service Unavailable`.

### Tags and Viewing-History Creation

`GET /tags` is public. `POST /films/log` requires a Bearer token and accepts `tmdb_id`, optional `tag_ids`, optional `prestige_tier`, and optional `personal_note`.

```mermaid
sequenceDiagram
    actor Client
    participant Route as POST /films/log
    participant Service as viewing_history_service
    participant TMDB as TMDB API
    participant Repo as viewing_history_repository
    participant DB as Database

    Client->>Route: Bearer token and history payload
    Route->>Service: create_entry(user, payload)
    Service->>TMDB: GET /movie/{tmdb_id}
    TMDB-->>Service: title and poster path
    Service->>Repo: get_tags_by_ids(tag_ids)
    Repo->>DB: SELECT matching tags
    DB-->>Repo: Tag entities
    Service->>Service: Build entry with cached title and poster URL
    Service->>Repo: create(entry)
    Repo->>DB: INSERT entry and tag associations, then commit
    DB-->>Repo: Created entry
    Service-->>Client: 201 complete viewing-history entry
```

The persisted entry contains `tmdb_id`, cached `title`, cached `poster_url`, tags, prestige tier, and personal note. TMDB remains the source of truth for complete metadata.

### Viewing-History Retrieval and Deletion

Both operations require a Bearer token. Deletion uses a TMDB identifier, not a viewing-history entry UUID.

```mermaid
sequenceDiagram
    actor Client
    participant HistoryRoute as GET /films/history
    participant DeleteRoute as DELETE /films/log/{tmdb_id}
    participant Service as viewing_history_service
    participant Repo as viewing_history_repository
    participant DB as Database

    Client->>HistoryRoute: Bearer token
    HistoryRoute->>Service: get_history(user)
    Service->>Repo: get_by_user(user.id)
    Repo->>DB: SELECT entries and joined tags
    DB-->>Repo: User's entries
    Service-->>Client: 200 array including cached title and poster URL

    Client->>DeleteRoute: Bearer token and tmdb_id
    DeleteRoute->>Service: remove_entry(user, tmdb_id)
    Service->>Repo: remove(user.id, tmdb_id)
    Repo->>DB: Find and delete matching user entry

    alt No matching entry
        Service-->>Client: 404 "No history entry found for this film."
    else Entry deleted
        Repo->>DB: Commit
        DeleteRoute-->>Client: 200 {detail: "Film removed from history."}
    end
```

## Planned Flows - Not Current Implementation

The following diagram is a proposed future flow. It is not a current working sequence: there are no recommendation routes, Recommendation Facade, Mistral client, platform-preference persistence, watchlist operations, mood questionnaire, or swipe implementation in the current source.

```mermaid
sequenceDiagram
    actor User
    participant UI as Planned mood and swipe UI
    participant API as Planned recommendation endpoint
    participant Facade as Planned Recommendation Facade
    participant DB as Planned preference storage
    participant Mistral as Planned Mistral AI integration
    participant TMDB as TMDB API

    User->>UI: Complete mood questions and swipes
    UI->>API: Submit planned recommendation request
    API->>Facade: Orchestrate recommendation
    Facade->>DB: Read planned platform preferences
    Facade->>Mistral: Request film suggestions
    Mistral-->>Facade: Suggested films
    Facade->>TMDB: Enrich suggestions
    TMDB-->>Facade: Metadata and availability
    Facade-->>UI: Planned filtered recommendations
```

Watchlist and user-profile operations are also planned. No `/films/watchlist`, `/users/me`, `/users/me/platforms`, or `/recommendations/start` route is registered by the current FastAPI application.

## Author

**zahin-dev**

- University: Kanagawa Institute of Technology
- GitHub: [@zahin-dev](https://github.com/zahin-dev)
