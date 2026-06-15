# 🎬 Film-like - High-Level Sequence Diagrams

This document illustrates the key interaction flows of the Film-like application.
Each diagram shows how the system components communicate step by step for a given use case.

---

## Table of Contents

- [1. User Registration](#user-registration)
- [2. User Login](#user-login)
- [3. Searching for a Movie](#searching-for-a-movie)
- [4. Log a Film](#log-a-film)
- [5. Film Recommendation](#film-recommendation)
- [6. Author](#author)

---

## User Registration

This sequence covers the full flow when a new user creates an account on Film-like.

**Actors:**

- `User` - user interacting through the React frontend
- `Backend` - the `/auth/register` route of the `FastAPI`
- `Business Logic` - the  User Service of the `FastAPI`
- `Database` - the PostgreSQL database

**Key steps:**

1. The user submits the registration form via the frontend
2. The frontend sends a POST request to /auth/register
3. The backend routes the request to the User Service
4. The User Service validates the input data (name, email, password format)
5. The User Service hashes the password using bcrypt
6. The User Service inserts the new user record into the database
7. If the email already exists, a 409 Conflict is returned
8. If the insert fails, a 500 Internal Server Error is returned
9. If successful, a JWT token is generated and returned with a 201 Created response
10. The frontend redirects the authenticated user to the dashboard

```mermaid
sequenceDiagram
    actor User as User (Frontend)
    participant Back as Backend<br>(FastAPI<br>/auth/register)
    participant BL as Business Logic<br>(User Service)
    participant DB as PostgreSQL<br>Database

    User->>Back: Register account
    Note over User,Back: Fills in registration form<br>first name, last name,<br>email, password

    Back->>BL: Validate and process registration
    Note over Back,BL: POST /auth/register<br>{first_name, last_name,<br>email, password}

    BL->>BL: Validate user data
    Note over BL: validate_name()<br>validate_email()<br>validate_password()

    alt Invalid input data
        BL-->>Back: Reject registration
        Note over BL,Back: 400 Bad Request<br>Validation error details

        Back-->>User: Display error message
        Note over Back,User: Invalid name, email,<br>or password format

    else Valid input data
        BL->>BL: Hash password
        Note over BL: bcrypt hash<br>Password is never stored<br>in plain text

        BL->>DB: Create user
        Note over BL,DB: INSERT INTO users<br>(first_name, last_name,<br>email, hashed_password, ...)
        DB->>DB: Execute INSERT

        alt Email already exists
            DB-->>BL: Reject insert
            Note over DB,BL: Unique constraint violation<br>on users.email

            BL-->>Back: Email conflict
            Note over BL,Back: 409 Conflict<br>"email already in use"

            Back-->>User: Display error message
            Note over Back,User: Account cannot be created<br>with this email address

        else Insert fails
            DB-->>BL: Database error
            Note over DB,BL: Unexpected database<br>or server error

            BL-->>Back: Server error
            Note over BL,Back: 500 Internal Server Error

            Back-->>User: Display generic error
            Note over Back,User: Registration failed<br>Please try again later

        else Insert successful
            DB-->>BL: User created
            Note over DB,BL: New user record<br>returned from database

            BL->>BL: Generate JWT
            Note over BL: Create access token<br>linked to user_id

            BL-->>Back: Return success response
            Note over BL,Back: 201 Created<br>{jwt_token, user_id}

            Back-->>User: Redirect to dashboard
            Note over Back,User: User is authenticated<br>and redirected
        end
    end
```

---

## User Login

This sequence covers the flow when a returning user logs into their account.

**Actors:**

- `User` - user interacting through the React frontend
- `Backend` - the `/auth/login` route of the `FastAPI`
- `Business Logic` - the User Service of the `FastAPI`
- `Database` - the PostgreSQL database

**Key steps:**

1. The user submits their email and password via the frontend
2. The frontend sends a POST request to /auth/login
3. The backend routes the request to the User Service
4. The User Service queries the database for the user by email
5. If the user is not found, a 401 Unauthorized is returned
6. The User Service verifies the password against the stored bcrypt hash
7. If the password is incorrect, a 401 Unauthorized is returned
8. If valid, a JWT token is generated and returned with a 200 OK response
9. The frontend stores the token and redirects to the dashboard

```mermaid
sequenceDiagram
    actor User as User (Frontend)
    participant Back as Backend<br>(FastAPI<br>/auth/login)
    participant BL as Business Logic<br>(User Service)
    participant DB as PostgreSQL<br>Database

    User->>Back: Log in
    Note over User,Back: Submits login form<br>email, password

    Back->>BL: Route login request
    Note over Back,BL: POST /auth/login<br>{email, password}

    BL->>DB: Fetch user by email
    Note over BL,DB: SELECT * FROM users<br>WHERE email = ?

    DB->>DB: Execute SELECT

    alt User not found
        DB-->>BL: Empty result
        Note over DB,BL: No user matching<br>this email address
        BL-->>Back: User not found
        Note over BL,Back: 401 Unauthorized<br>"invalid credentials"
        Back-->>User: Display error message
        Note over Back,User: Intentionally vague to prevent<br>email enumeration attacks
    else User found
        DB-->>BL: User record
        Note over DB,BL: Returns user including<br>hashed_password

        BL->>BL: Verify password
        Note over BL: verify_password()<br>Compare input with<br>bcrypt hash

        alt Password incorrect
            BL-->>Back: Invalid password
            Note over BL,Back: 401 Unauthorized<br>"invalid credentials"
            Back-->>User: Display error message
            Note over Back,User: Same message as user not found<br>to prevent enumeration
        else Password correct
            BL->>BL: Generate JWT
            Note over BL: Create access token<br>linked to user_id
            BL-->>Back: Return success response
            Note over BL,Back: 200 OK<br>{jwt_token, user_id}
            Back-->>User: Return success
            Note over Back,User: User is authenticated<br>and redirected to dashboard
        end
    end
```

> ***Security note**: why both error cases return the same message?<br>
> When a login attempt fails, the API always returns the same error message: `"invalid credentials"` - whether the email does not exist or the password is incorrect.
> This is a deliberate security practice known as **credential enumeration prevention**.<br>
> If the API returned different messages ("email not found" vs "wrong password"), an attacker could systematically test email addresses to discover which ones are registered in the system.<br>
> By returning the same message in both cases, the system reveals no information about which part of the credentials was wrong.*

---

## Searching for a Movie

This sequence covers the flow when a user searches for a movie in the TMDB catalog, in order to log it or add it to their watchlist.

**Actors:**

- `User` - user interacting through the React frontend
- `Backend` - the `/films/search` route of the `FastAPI`
- `Business Logic` - the Film Service of the `FastAPI`
- `API` - the TMDB API

**Key steps:**

0. The user navigates through the app to the movie search page
1. The user types a movie title in the search bar and confirms
2. The frontend sends a GET request to `/films/search?query=...`
3. The backend routes the request to the Film Service
4. The Film Service calls the TMDB search endpoint
5. TMDB returns a list of matching films (multilingual search by default)
6. The backend returns the results to the frontend
7. The user selects a film from the results

```mermaid
sequenceDiagram
    actor User as User (Frontend)
    participant Back as Backend<br>(FastAPI<br>/films/search)
    participant BL as Business Logic<br>(Film Service)
    participant API as TMDB API

    User->>Back: Search for a movie
    Note over User,Back: Submits search query<br>movie title

    Back->>BL: Route search request
    Note over Back,BL: GET /films/search<br>?query=title

    BL->>API: Search movie catalog
    Note over BL,API: GET /search/movie<br>?query=title

    alt TMDB unavailable
        API-->>BL: Error or timeout
        Note over API,BL: External service<br>unreachable
        BL-->>Back: Service error
        Note over BL,Back: 503 Service Unavailable
        Back-->>User: Display error message
        Note over Back,User: Movie search is temporarily<br>unavailable
    else No results found
        API-->>BL: Empty results list
        Note over API,BL: No movie matches<br>the search query
        BL-->>Back: Empty response
        Note over BL,Back: 200 OK<br>{results: []}
        Back-->>User: Display no results message
        Note over Back,User: No movie found<br>for this search
    else Results found
        API-->>BL: List of matching movies
        Note over API,BL: tmdb_id, title, year,<br>poster_url for each result
        BL-->>Back: Return search results
        Note over BL,Back: 200 OK<br>{results: [{tmdb_id, title,<br>year, poster_url}]}
        Back-->>User: Display search results
        Note over Back,User: User sees matching<br>movie cards
    end
```

> ***Note on multilingual search**:<br>
> The TMDB /search/movie endpoint supports multilingual queries by default.
> A search for "Les Évadés" will return "The Shawshank Redemption", and vice versa, regardless of the language parameter set for the response.<br>
> The language parameter only affects the language of the returned data (titles, synopses, genres), not the search matching itself.<br>
> For the MVP, all responses are returned in English (language=en-US).**

---

## Log a Film

This sequence covers the flow when a user views a film's details page and logs it to their viewing history.

**Actors:**

- `User` - user interacting through the React frontend
- `Backend` - the `/films/*` routes of the `FastAPI`
- `Business Logic - Film Service` - the Film Service of the `FastAPI`
- `Business Logic - User Service` - the User Service of the `FastAPI`
- `API` - the TMDB API
- `Database` - the PostgreSQL database

**Key steps:**

0. The user navigates through the app to a film's details page (from search results)
1. The backend fetches full film details from TMDB
2. The backend checks if the film is already in the user's viewing history or watchlist
3. The frontend displays the film details and adapts the action buttons accordingly
4. The user clicks "Log this film" and selects tags
5. The backend creates a viewing history entry and links the selected tags
6. A `201 Created` response confirms the film has been logged

```mermaid
sequenceDiagram
    actor User as User (Frontend)
    participant Back as Backend<br>(FastAPI /films)
    participant BLF as Business Logic<br>(Film Service)
    participant BLU as Business Logic<br>(User Service)
    participant API as TMDB API
    participant DB as PostgreSQL<br>Database

    User->>Back: Open film details page
    Note over User,Back: Navigates from search results<br>GET /films/{tmdb_id}

    Back->>BLF: Fetch film details
    Note over Back,BLF: tmdb_id from URL

    BLF->>API: Get full film data
    Note over BLF,API: GET /movie/{tmdb_id}<br>?append_to_response=credits

    API-->>BLF: Film details
    Note over API,BLF: title, synopsis, cast,<br>genres, runtime, poster

    BLF->>BLU: Check film status for user
    Note over BLF,BLU: Is this film already in<br>viewing history or watchlist?

    BLU->>DB: Query user film status
    Note over BLU,DB: SELECT FROM viewing_history_entries<br>AND watchlist_entries<br>WHERE user_id = ? AND tmdb_id = ?

    DB-->>BLU: Film status
    Note over DB,BLU: {in_viewing_history: bool,<br>in_watchlist: bool}

    BLU-->>BLF: Return status
    BLF-->>Back: Film details + status
    Back-->>User: Display film page
    Note over Back,User: Film details displayed
    Note over DB,User: Buttons adapt to film status:<br>"Log this film" or "Remove from history"<br>"Add to watchlist" or "Remove from watchlist"

    alt User clicks "Log this film"
        User->>Back: Log film with tags
        Note over User,Back: POST /films/log<br>{tmdb_id, tag_ids[]}

        Back->>BLF: Create viewing history entry
        BLF->>DB: Insert entry
        Note over BLF,DB: INSERT INTO viewing_history_entries<br>(user_id, tmdb_id, ...)

        DB->>DB: Execute INSERT

        alt Insert fails
            DB-->>BLF: Database error
            BLF-->>Back: Server error
            Note over BLF,Back: 500 Internal Server Error
            Back-->>User: Display error message

        else Insert successful
            DB-->>BLF: Entry created
            BLF->>DB: Link selected tags
            Note over BLF,DB: INSERT INTO viewing_history_tags<br>(entry_id, tag_id) for each tag
            DB-->>BLF: Tags linked
            BLF-->>Back: Success
            Note over BLF,Back: 201 Created<br>{entry_id}
            Back-->>User: Confirm film logged
            Note over Back,User: Film added to viewing history<br>Button switches to "Remove from history"
        end

    else User clicks "Remove from history"
        User->>Back: Remove film from history
        Note over User,Back: DELETE /films/log/{entry_id}

        Back->>BLF: Delete viewing history entry
        BLF->>DB: Delete entry
        Note over BLF,DB: DELETE FROM viewing_history_entries<br>WHERE id = entry_id<br>CASCADE removes linked tags

        DB-->>BLF: Entry deleted
        BLF-->>Back: Success
        Note over BLF,Back: 200 OK
        Back-->>User: Display confirmation removal message
        Note over Back,User: Film removed from history<br>Button switches back to "Log this film"
    end
```

> ***Note on film status check**:<br>
> When a user opens a film details page, the backend automatically checks whether that film is already present in the user's viewing history and watchlist.<br>
> This check runs before the page is displayed, so the action buttons always reflect the current state: "Log this film" or "Remove from history", "Add to watchlist" or "Remove from watchlist".<br>
> On the frontend side, no page reload is required after an action - React updates the button state immediately using local component state, providing an instant and seamless experience.*

---

## Film Recommendation

This sequence covers the full recommendation flow, from the mood questionnaire to the final film suggestions.

**Actors:**

- `User` - user interacting through the React frontend
- `Backend` - the `/recommendation/*` routes of the `FastAPI`
- `Business Logic - Recommendation Facade` - the Recommendation Facade of the `FastAPI`
- `Business Logic - User Service` - the User Service of the `FastAPI`
- `API` - the TMDB API
- `LLM` - the Mistral AI API
- `Database` - the PostgreSQL database

**Key steps:**

0. The user navigates from the home screen to the Recommendation experience
1. The user starts the recommendation experience
2. The user completes a mood questionnaire (handled entirely on the frontend)
3. The user swipes through film cards (right = interested, left = not interested)
4. The user optionally adds a free-text prompt before final submission
5. The backend retrieves the user's viewing history and platform preferences
6. The backend sends a structured prompt to the LLM
7. The LLM returns film suggestions
8. The backend enriches the suggestions with TMDB data and streaming availability
9. The frontend displays the final recommendation list

```mermaid
sequenceDiagram
    actor User as User (Frontend)
    participant Back as Backend<br>(FastAPI<br>/recommendations)
    participant BLR as Business Logic<br>(Recommendation Facade)
    participant BLU as Business Logic<br>(User Service)
    participant DB as PostgreSQL<br>Database
    participant LLM as Mistral AI
    participant API as TMDB API

    User->>Back: Start recommendation experience

    Note over User: Mood questionnaire<br>(handled on frontend)
    Note over User: Film card swiping session<br>(swipe data held in memory)
    Note over User: Optional free-text prompt<br>("I want something like...")

    User->>Back: Submit recommendation request
    Note over User,Back: POST /recommendations/start<br>{mood, swipe_results[], optional_prompt}

    Back->>BLR: Process recommendation request
    BLR->>BLU: Fetch user context
    BLU->>DB: Get viewing history + platform preferences
    Note over BLU,DB: SELECT viewing_history + user_platforms<br>WHERE user_id = ?
    DB-->>BLU: User data
    BLU-->>BLR: Viewing history + platforms

    BLR->>BLR: Build structured prompt
    Note over BLR: Combines mood, swipe results,<br>optional prompt, history,<br>and platform preferences

    BLR->>LLM: Send prompt
    Note over BLR,LLM: POST to Mistral API<br>Structured JSON output requested

    alt LLM unavailable
        LLM-->>BLR: Error or timeout
        BLR-->>Back: Service error
        Note over BLR,Back: 503 Service Unavailable
        Back-->>User: Display error message
        Note over Back,User: Recommendation service<br>temporarily unavailable
    else LLM responds
        LLM-->>BLR: Film suggestions
        Note over LLM,BLR: [{tmdb_id, title, reason}]

        BLR->>API: Fetch film details + streaming availability
        Note over BLR,API: GET /movie/{tmdb_id}<br>GET /movie/{tmdb_id}/watch/providers<br>for each suggested film

        API-->>BLR: Enriched film data
        BLR->>BLR: Filter by user platform preferences
        BLR-->>Back: Final recommendations
        Note over BLR,Back: 200 OK<br>[{film, platform, reason}]

        Back-->>User: Display recommendation list
        Note over Back,User: Curated film suggestions<br>with streaming availability

        opt User adds film to watchlist
            User->>Back: Add to watchlist
            Note over User,Back: POST /films/watchlist<br>{tmdb_id}
            Back->>DB: INSERT INTO watchlist_entries
            DB-->>Back: 201 Created
            Back-->>User: Confirm film added
        end
    end
```

> ***Note on the recommendation flow**
> The mood questionnaire and swipe session are handled entirely on the frontend and held in memory - no intermediate data is sent to the backend until the user submits the final request.<br>
> This keeps the backend stateless and reduces unnecessary API calls.<br>
> The optional free-text prompt allows the user to add a personal touch to the recommendation request before it is sent to the LLM.*

---

## Author

**Félix Besançon**
Holberton School Bordeaux - Bachelor CDA, Year 1
Specialisation: Fullstack Development & Machine Learning

- GitHub: [@zahin-dev](https://github.com/zahin-dev)

---
