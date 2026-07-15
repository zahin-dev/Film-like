# Film-like - Sequence Diagrams

These flows are implemented by the current FastAPI and React source. External calls are real in live use and fully mocked in the automated backend suite.

## Authentication and Protected Navigation

```mermaid
sequenceDiagram
    actor User
    participant UI as React AuthPage
    participant Auth as AuthContext + Axios
    participant Route as Auth routes
    participant Service as auth_service
    participant Repo as user_repository
    participant DB as PostgreSQL

    alt Registration
        User->>UI: Submit profile, email, password
        UI->>Route: POST /auth/register
        Route->>Service: register_user(payload)
        Service->>Repo: Check email and create user
        Repo->>DB: SELECT then INSERT
        DB-->>Service: Created user
        Service-->>UI: 201 {user, token}
        UI->>Auth: Login with the new credentials
    else Login
        User->>UI: Submit email and password
        UI->>Auth: login(email, password)
    end

    Auth->>Route: POST /auth/login
    Route->>Service: login_user(payload)
    Service->>Repo: Load user by email
    Repo->>DB: SELECT user
    Service->>Service: Verify bcrypt hash and sign JWT
    Service-->>Auth: 200 {public user, token}
    Auth->>Auth: Store JWT and user snapshot in sessionStorage
    Auth-->>UI: Navigate to protected diary
```

Pydantic validation returns `422`, duplicate registration returns `409`, and invalid credentials return a non-enumerating `401` response. Protected React routes redirect unauthenticated users to the authentication page. The centralized Axios client attaches the Bearer token and clears rejected sessions.

## Catalog Search and Film Detail

```mermaid
sequenceDiagram
    actor User
    participant UI as Catalog / FilmDetail pages
    participant Route as Film routes
    participant Service as film_service
    participant Repo as viewing_history_repository
    participant DB as PostgreSQL
    participant TMDB as TMDB API

    User->>UI: Search for a title
    UI->>Route: GET /films/search?query=title
    Route->>Service: search_films(query)
    Service->>TMDB: Search movie
    TMDB-->>Service: Candidate metadata
    Service-->>UI: 200 Film array

    User->>UI: Open one result
    UI->>Route: GET /films/{tmdb_id} with JWT
    Route->>Service: get_film_with_status(user, tmdb_id)
    Service->>TMDB: Movie details + credits
    Service->>TMDB: Watch providers for France
    Service->>Repo: Find user entry by TMDB ID
    Repo->>DB: SELECT viewing history
    DB-->>Repo: Entry or no result
    Service-->>UI: 200 {film, in_history}
```

The frontend displays loading, error, and no-result states. TMDB `404` becomes an API `404`; other TMDB/network failures are controlled `503` responses.

## Log, Retrieve, and Remove Viewing History

```mermaid
sequenceDiagram
    actor User
    participant UI as FilmDetail / Diary pages
    participant Route as Film routes
    participant Service as viewing_history_service
    participant Repo as viewing_history_repository
    participant DB as PostgreSQL
    participant TMDB as TMDB API

    User->>UI: Choose tags, tier, note
    UI->>Route: POST /films/log with JWT and tmdb_id/reaction
    Route->>Service: create_entry(user, payload)
    Service->>TMDB: Validate GET /movie/{tmdb_id}
    TMDB-->>Service: Transient title/poster data
    Service->>Repo: Resolve tag IDs
    Repo->>DB: SELECT tags
    Service->>Repo: Create entry without film metadata
    Repo->>DB: INSERT tmdb_id, reaction, associations
    Service-->>UI: 201 entry with transient display metadata

    User->>UI: Open or refresh diary
    UI->>Route: GET /films/history with JWT
    Route->>Service: get_history(user)
    Service->>Repo: get_by_user(user.id)
    Repo->>DB: SELECT entries and joined tags in deterministic order
    DB-->>Service: Persisted reactions
    Note over Service,TMDB: asyncio.gather preserves entry order
    loop Concurrent lookup per entry
        Service->>TMDB: GET /movie/{tmdb_id}
        TMDB-->>Service: Current title/poster or isolated error
    end
    Service-->>UI: 200 enriched history array

    User->>UI: Remove film
    UI->>Route: DELETE /films/log/{tmdb_id}
    Route->>Service: remove_entry(user, tmdb_id)
    Service->>Repo: Remove matching user entry
    Repo->>DB: DELETE and commit
    Service-->>UI: 200 confirmation or 404
```

TMDB data returned during logging is never assigned to mapped columns. A failed retrieval enrichment produces null title/poster values for that item and never deletes or mutates the record.

## Mood-Based Recommendation Facade

```mermaid
sequenceDiagram
    actor User
    participant UI as RecommendationPage
    participant Route as POST /recommendations
    participant Facade as Recommendation Facade
    participant Repo as viewing_history_repository
    participant DB as PostgreSQL
    participant MistralClient as mistral_client
    participant Mistral as Mistral API
    participant TMDB as TMDB API

    User->>UI: Select one supported mood
    UI->>Route: {mood, limit} with JWT
    Route->>Facade: recommend(user, mood, limit)
    Facade->>Repo: Read viewing history and tags
    Repo->>DB: SELECT entries and associations
    DB-->>Facade: User-owned reactions and TMDB IDs
    Facade->>Facade: Count tag frequencies
    Facade->>TMDB: Resolve recent viewed titles concurrently
    Facade->>Facade: Build controlled mood/history context
    Facade->>MistralClient: Messages + strict Pydantic JSON Schema
    MistralClient->>Mistral: POST /v1/chat/completions
    Mistral-->>Facade: Structured title/year/reason candidates
    Facade->>Facade: Strict parse, year checks, title deduplication

    loop Candidate verification
        Facade->>TMDB: Search candidate title
        TMDB-->>Facade: TMDB Film matches
        Facade->>Facade: Prefer year; exclude watched/duplicate IDs
    end

    alt Enough verified results
        Facade-->>Route: Mood, tags used, verified films and reasons
        Route-->>UI: 200 RecommendationResponse
        UI->>UI: Display next/skip recommendation deck
    else Structured/resolution shortfall on first attempt
        Facade->>MistralClient: Retry once with different-candidate instruction
    else Missing key or controlled upstream/output error
        Facade-->>UI: 503, 504, or 502 safe error
    end
```

The model never supplies a trusted TMDB ID. Only TMDB-resolved `Film` objects are returned. The API key, authorization header, raw prompt, and raw upstream response are not included in HTTP error details. The application starts without a Mistral key, but this endpoint then returns `503` rather than fake results.

## Future Flows - Not Implemented

Watchlists, profile editing, stored platform subscriptions, social/shared lists, payment flows, and platform-based recommendation filtering have no current routes or persistence. `/films/watchlist`, `/users/me`, `/users/me/platforms`, and `/recommendations/start` are not registered endpoints.

## Author

**zahin-dev**

- University: Kanagawa Institute of Technology
- GitHub: [@zahin-dev](https://github.com/zahin-dev)
