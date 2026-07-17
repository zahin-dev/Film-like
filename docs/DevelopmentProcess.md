# Film-like Development Process Retrospective

This document explains how the current repository relates to the development-history claims in the submitted Japanese entry sheet (ES). It is a retrospective written after the work; it is not an original timestamped project artifact. It does not create evidence for dates, team-member identities, contribution percentages, issues, pull requests, or process records that were not retained.

## Project Context and Team Roles

The following statements are retrospective facts reported by the project team:

- Film-like is jointly owned, developed, and maintained by a three-person team.
- The repository is hosted under one team member's `zahin-dev` GitHub account for administrative convenience and as a public contact point. The account name does not indicate sole project ownership or sole authorship.
- The team built the initial MVP over approximately three months and continues to develop and improve the application with the same three members.
- One member primarily led backend design and implementation, including API contracts, authentication, database integration, external-service integration, and the Mistral-based recommendation flow.
- One member primarily led frontend development, including screens, input forms, buttons, user interactions, and client-side communication with backend APIs.
- One member primarily led infrastructure and project-wide coordination, including server setup, deployment, cloud configuration, CI/CD, testing, and system-design support.
- Primary responsibilities organized the work but were not exclusive boundaries. All three members contributed outside their primary areas through implementation, review, debugging, testing, verification, design discussions, documentation, and improvement work.
- The team used GitHub to iteratively implement, review, revise, test, and improve the application through feedback and collaborative trial and error.
- Pair programming and process adjustments were used when work stalled so that the team could resolve blockers and maintain progress.

No team-member names or contribution percentages are asserted here. The current checkout also cannot establish exactly when every present-day file was written or assign every line to a specific member.

## Evidence Classification

### Repository-verifiable facts

The current source tree and retained Git history can be inspected directly to verify:

- a Python 3.12/FastAPI backend with Pydantic schemas, SQLAlchemy repositories, Alembic migrations, and PostgreSQL configuration;
- a React frontend with authenticated diary, film-catalog, film-detail, recommendation, and diary-insight interfaces;
- separate route, service, repository, and external-client boundaries;
- TMDB-based film identity and metadata resolution, with only `tmdb_id` stored locally for film identity;
- request-time recommendation context built from current mood and stored viewing tags;
- strict Mistral JSON Schema requests, Pydantic validation, candidate filtering, at most one retry, TMDB resolution, and controlled error responses;
- automated backend tests, frontend lint/build scripts, GitHub Actions configuration, Docker Compose configuration, and English public-text audit tooling; and
- incremental commits in the retained Git history.

Repository-verifiable means that a reviewer can reproduce or inspect the fact in this checkout. It does not establish when every line was written, which member wrote each line, or the exact contribution share of any member.

### Self-reported retrospective facts

The team size, approximate initial MVP duration, continuing three-person development, role allocation, cross-functional contributions, original GitHub workflow, use of branches and pull requests, pair-programming sessions, blocker-resolution discussions, and July 15, 2026 manual live-verification result are retrospective statements from the project team. Unless separately supported by retained timestamped artifacts, this repository alone does not independently prove each event.

## Development Scope and Continuity

### Initial MVP phase

The three-person team established the project direction and built the initial MVP over approximately three months. During this phase, the backend member primarily led backend design and implementation, the frontend member primarily led user-interface and client-side integration work, and the infrastructure and project-wide coordination member primarily led environment, deployment, CI/CD, testing, and cross-system support.

These roles were primary areas of responsibility rather than isolated ownership boundaries. The members coordinated API request and response formats, authentication behavior, error handling, integration issues, and system-design decisions.

### Ongoing three-person development

Development did not end after the initial MVP phase and did not transition into an individually owned project. The same three-person team continued improving the frontend, Mistral integration, automated tests, CI/CD, deployment and verification procedures, diary insights, reproducible metrics and audits, and documentation.

The current repository therefore reflects the continuing work of the three-person team. Frontend completion, Mistral hardening, test expansion, CI/CD, verification, and documentation must not be interpreted as later individual completion by the member associated with the `zahin-dev` account.

### Role ownership and cross-functional collaboration

The backend member primarily led server-side API, authentication, persistence, external-service, and Mistral-related work, with contributions and support from the other two members. The frontend member primarily led screens, forms, controls, interaction states, and client-side API communication, with contributions and support from the other two members. The infrastructure and project-wide coordination member primarily led server setup, deployment, cloud configuration, CI/CD, testing, and system-design support, with contributions and support from the other two members.

Client-side API communication and backend API contracts were coordinated across the frontend and backend roles. System-design decisions were discussed by the team, with the infrastructure and project-wide coordination member providing cross-system design support. Testing and CI/CD were primarily coordinated by the infrastructure member, while each member helped define expected behavior, review or add tests in their area, investigate failures, and improve the implementation.

## Engineering Practices

### Layered implementation

FastAPI routes handle HTTP concerns and authentication dependencies. Services coordinate application behavior. Repositories isolate database access. External clients isolate TMDB and Mistral HTTP communication. The Recommendation Facade composes these boundaries while treating AI output as untrusted.

### Incremental GitHub workflow

The retained history shows incremental commits. The team retrospectively reports using GitHub branches and pull requests to iteratively implement, review, revise, and improve the application. Team members worked through technical problems together, exchanged feedback, and contributed outside their primary areas when necessary. The current checkout does not independently reconstruct every historical pull request, review, or issue, so no missing identifiers or counts are invented.

### Tests and CI/CD

The backend suite uses isolated test configuration and mocks external TMDB and Mistral calls. GitHub Actions runs the English public-text audit, backend tests, frontend dependency installation, lint, and production build. The infrastructure and project-wide coordination member primarily led CI/CD and testing work, while the other members contributed by defining expected behavior, adding or reviewing tests in their areas, investigating failures, and improving the implementation. These checks verify current contracts; they do not prove current availability of external services.

### Pair programming and blocker resolution

The team retrospectively reports that pair programming, role-crossing support, and process changes were used when work stalled. This document records that collaborative context, not a timestamped KPT record, screenshot, activity metric, or exact contribution breakdown.
