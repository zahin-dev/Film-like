# Film-like Verification Evidence

This document records verification of the current MVP checkout. Automated tests use mocks for TMDB and Mistral and do not make live requests. Passing results verify current application contracts, not permanent external-service availability or production readiness.

## Automated Verification

The commands below were run on July 16, 2026 with Python 3.12.13 from the supported local virtual environment.

### Backend tests

```powershell
cd backend
..\backend\venv\Scripts\python.exe -m pytest -q
```

Result: `102 passed in 40.05s`.

### Backend coverage

```powershell
cd backend
..\backend\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Result: `102 passed in 41.36s`; total application coverage was `90%` (`689` statements, `67` missed). The diary-insight route, schema, and service each measured `100%` statement coverage.

### Application import without Mistral configuration

The process was given deterministic non-secret database/auth/TMDB test settings, `MISTRAL_API_KEY` was removed only from that child process, and the application was imported without reading or printing any local secret value.

Result: `Film-like API: import ok without MISTRAL_API_KEY`.

### Alembic single-head check

```powershell
cd backend
..\backend\venv\Scripts\python.exe -m alembic heads
```

Result: one head, `b3d91f6a2c04 (head)`.

### Frontend clean install

```powershell
cd frontend
npm ci
```

Result after the advisory remediation: `180` packages added and `181` packages audited from the committed lockfile; npm reported `0 vulnerabilities`.

### Frontend dependency audits

```powershell
cd frontend
npm audit
npm audit --omit=dev
```

Result: both the complete dependency audit and the production-only audit reported `0 vulnerabilities`. The lockfile refresh moved the production transitive dependency `form-data` from 4.0.5 to 4.0.6 and the development dependency Vite from 8.0.14 to 8.1.5 within the existing declared semver ranges. No dependency override, forced update, major-version change, or new direct package was added.

### Frontend lint

```powershell
cd frontend
npm run lint
```

Result: ESLint exited `0` with no reported violations.

### Frontend production build

```powershell
cd frontend
npm run build
```

Result: Vite 8.1.5 transformed `91` modules and completed successfully in `366ms`. Output sizes were `0.45 kB` HTML (`0.29 kB` gzip), `26.24 kB` CSS (`6.55 kB` gzip), and `303.82 kB` JavaScript (`97.33 kB` gzip). The generated `frontend/dist` directory remains ignored and untracked.

### Docker Compose validation

```powershell
docker compose config
```

Result: exit `0`; the resolved configuration retained the `postgres_data` named volume and included the PostgreSQL `pg_isready` healthcheck. The sandbox printed a warning that it could not read the user's Docker client configuration, but Compose still rendered and validated this project configuration. No container or volume was created, recreated, or deleted.

This Compose file is a reproducible PostgreSQL 16 development environment, not production configuration.

### Git and repository hygiene

```powershell
git diff --check
```

Result: no whitespace errors. Git printed only working-copy LF-to-CRLF notices on this Windows checkout.

The tracked-environment-file scan found no committed local `.env` file. The tracked-secret signature scan found no private-key, common token-prefix, or non-placeholder key assignment. The tracked generated-artifact scan found no `node_modules`, `__pycache__`, coverage, build, or distribution output. Scans report file/line locations only and do not print credential values.

### English public-text audit

```powershell
python scripts/check_english_public_text.py
```

Result: no Hiragana, Katakana, or CJK characters were found in public Markdown documentation or in backend/frontend source comments and docstrings. The script prints the exact file and line and exits non-zero if it finds a violation. It does not inspect environment files, dependency trees, generated output, identifiers, URLs, database contents, or user-entered data.

### Reproducible project metrics

```powershell
python scripts/project_metrics.py
```

Physical UTF-8 lines include blank and comment-only lines. Counts exclude virtual environments, dependency trees, caches, coverage output, and build output.

| Scope | Files | Physical lines |
|---|---:|---:|
| `backend/app` Python | 35 | 2,430 |
| `backend/tests` Python | 6 | 1,470 |
| Migration Python | 5 | 217 |
| Total backend Python | 48 | 4,429 |
| `frontend/src` text source | 20 | 2,779 |

The total backend category also includes Alembic support and seed Python files. These are current-checkout measurements and must not be treated as the line count of the initial approximately three-month MVP phase, which was followed by continued development by the same three-person team.

## Manual Live End-to-End Verification

The project team retrospectively reports that manual live end-to-end verification was completed on July 15, 2026. This was manual verification within the continuing three-person development effort, not an automated test run or a repository-verifiable timestamped artifact. It covered:

- account registration;
- login;
- TMDB search;
- film-detail display;
- viewing-history persistence;
- diary display;
- mood selection;
- live Mistral recommendation;
- historical viewing tags used as recommendation context; and
- TMDB-resolved recommendation results.

This record does not include or commit keys, tokens, screenshots, response bodies, or fabricated metrics. External TMDB and Mistral availability, credentials, model behavior, and recommendation quality can change after the recorded verification.

## Remaining Boundaries

- Film-like remains an MVP and is not production-ready.
- Malformed Mistral output remains possible; strict schema requests, Pydantic validation, filtering, at most one retry, and controlled errors prevent malformed candidates from being displayed as recommendations.
- Automated tests mock external services and therefore do not prove live availability.
- Diary insights aggregate user-selected reaction tags. They are not clinical emotion analysis, sentiment inference, personality analysis, or mental-health analysis.
- The retrospective development-history statements are classified separately in [DevelopmentProcess.md](DevelopmentProcess.md).
