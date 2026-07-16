# Film-like Development Process Retrospective

This document explains how the current repository relates to the development-history claims in the submitted Japanese entry sheet (ES). It is a retrospective written after the work; it is not an original timestamped project artifact. It does not create evidence for dates, collaborators, contribution percentages, issues, pull requests, or process records that were not retained.

## Original Project Context

The following statements are self-reported retrospective facts from the repository owner:

- The original Film-like project was developed over approximately three months by a three-person team.
- The team used GitHub-based iterative development.
- The repository owner led backend design and implementation.
- Pair programming was used when work stalled, and the team adjusted its process to resolve blockers and improve progress.

No collaborator names or contribution percentages are asserted here. The current checkout also cannot establish that every present-day file existed or was complete during that original three-month period.

## Evidence Classification

### Repository-verifiable facts

The current source tree and Git history can be inspected directly to verify:

- a Python 3.12/FastAPI backend with Pydantic schemas, SQLAlchemy repositories, Alembic migrations, and PostgreSQL configuration;
- a React frontend with authenticated diary, film-catalog, film-detail, recommendation, and diary-insight interfaces;
- separate route, service, repository, and external-client boundaries;
- TMDB-based film identity and metadata resolution, with only `tmdb_id` stored locally for film identity;
- request-time recommendation context built from current mood and stored viewing tags;
- strict Mistral JSON Schema requests, Pydantic validation, candidate filtering, at most one retry, TMDB resolution, and controlled error responses;
- automated backend tests, frontend lint/build scripts, GitHub Actions configuration, Docker Compose configuration, and English public-text audit tooling; and
- incremental commits in the retained Git history.

Repository-verifiable means that a reviewer can reproduce or inspect the fact in this checkout. It does not show when every line was originally written or who wrote every line.

### Self-reported retrospective facts

The team size, approximate duration, backend leadership, original GitHub workflow, use of pull requests, pair-programming sessions, blocker-resolution discussions, and July 15, 2026 manual live-verification result are retrospective statements from the repository owner. Unless separately supported by retained timestamped artifacts, this repository alone does not independently prove each event.

## Scope Separation

### Original team MVP period

The original three-person, approximately three-month period established the project direction and team MVP work. The owner reports leading the backend design and implementation during this period. The repository does not preserve a reliable file-by-file boundary for that historical snapshot, so current files must not all be attributed to the original period.

### Later individual completion and hardening

The current repository contains later individual work after the original team period. That later work includes frontend completion, Mistral integration hardening, expanded automated tests, GitHub Actions CI, manual live verification, diary reaction insights, reproducible metrics and audits, and documentation alignment.

The present application is therefore evidence of the combined project history: original team MVP work followed by later individual completion, testing, frontend completion, AI hardening, CI, live verification, and documentation. It remains an MVP and is not described as production-ready.

## Engineering Practices

### Layered implementation

FastAPI routes handle HTTP concerns and authentication dependencies. Services coordinate application behavior. Repositories isolate database access. External clients isolate TMDB and Mistral HTTP communication. The Recommendation Facade composes these boundaries while treating AI output as untrusted.

### Incremental GitHub workflow

The retained history shows incremental commits. The owner retrospectively reports that the original team used GitHub branches and pull requests for iterative development. The current checkout does not independently reconstruct every historical pull request, review, or issue, so no missing identifiers or counts are invented.

### Tests and CI

The backend suite uses isolated test configuration and mocks external TMDB and Mistral calls. GitHub Actions runs the English public-text audit, backend tests, frontend dependency installation, lint, and production build. These checks verify current contracts; they do not prove current availability of external services.

### Pair programming and blocker resolution

The owner retrospectively reports that pair programming and process changes were used when work stalled. This document records that statement as retrospective context, not as a timestamped KPT record, screenshot, or activity metric.
