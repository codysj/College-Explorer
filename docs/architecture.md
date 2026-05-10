# Architecture

This document captures the target architecture for the College Exploration Platform. It is a placeholder until the application layers are implemented.

## Target Shape

- `apps/web`: Next.js frontend for onboarding, search, school profiles, comparison, and decision workflows.
- `apps/api`: FastAPI backend for typed REST endpoints, validation, search, ranking, comparison, and data access.
- PostgreSQL: canonical structured college data and user-owned decision state. The V1.2 schema exists under `apps/api/alembic`.
- pgvector: semantic retrieval for V2 after structured V1 search is stable.
- Redis: cache-aside layer for repeated read-heavy queries after V1 APIs exist.
- `data/raw`: raw source snapshots, usually large and not committed.
- `data/processed`: cleaned local development data.
- `data/seed`: small deterministic fixtures for tests and demos.
- `infra`: local and cloud infrastructure notes and configuration.

## Boundaries

- The frontend must not query PostgreSQL directly.
- The backend owns validation, persistence, scoring, ranking, and API contracts.
- Data ingestion should stay separate from user-facing API routes.
- Deterministic ranking and reason codes must stay separate from any future LLM copy generation.

## Backend Structure

The V1.3 FastAPI foundation lives in `apps/api`:

- `main.py`: app factory, router registration, and exception handler registration.
- `api/`: HTTP routers and request dependencies.
- `core/`: settings, logging, and global error handling.
- `db/`: SQLAlchemy base, engine, and session factory.
- `models/`: SQLAlchemy ORM models matching the Alembic schema.
- `schemas/`: Pydantic API request/response models.
- `repositories/`: data access layer. SQL belongs here, not in route handlers.
- `services/`: business logic layer placeholders between routes and repositories.
- `tests/`: pytest tests for backend behavior.

Request flow should be `routes -> services -> repositories -> database`. Routes own HTTP concerns, services own product logic, repositories own persistence, and models mirror database tables.

## School API Query Strategy

`GET /schools/search` uses the standard backend layers:

- `api/routes/schools.py` parses and validates query parameters.
- `services/schools.py` builds response metadata.
- `repositories/schools.py` composes a SQLAlchemy query over `schools`, `school_costs`, and `school_academics`.

The repository uses left joins so schools with missing optional cost or academic fields can still appear when filters allow them. Filters are composed with SQLAlchemy expressions, keeping values parameterized. The response returns only search-card fields and avoids full school profile data. Search logs include query execution time, returned row count, total results, page, and page size.

Indexes from V1.2 support common filters and sorts on state, region, type, setting, enrollment, acceptance rate, graduation rate, tuition, and net price. To inspect a slow query locally, run the generated SQL through `EXPLAIN ANALYZE` against Postgres.

`GET /schools/{id}` follows the same layering:

- `api/routes/schools.py` handles path parsing, response typing, and HTTP 404 behavior.
- `services/schools.py` composes the nested profile response and computes missing-data metadata.
- `repositories/schools.py` reads the profile with one left-joined query across `schools`, `school_academics`, `school_costs`, `school_outcomes`, and `school_campus_life`.

Profile responses keep missing values as `null`, list missing dot-paths in `data_fields_missing`, and expose a simple completeness-based `data_confidence_score`. Ranking and similar-school placeholders remain empty until later roadmap steps.

`POST /rankings` follows the same layering:

- `api/routes/rankings.py` validates the ranking request and response shape.
- `services/ranking_service.py` owns deterministic category scoring, normalized weights, hard constraints, confidence, reason codes, tradeoffs, and stable ordering.
- `repositories/schools.py` fetches all V1 ranking inputs with one left-joined query across core, academic, cost, outcome, and campus-life tables.

Ranking is computed in memory for V1 scale after the repository query. Missing values remain unknown: they produce neutral category fit and lower confidence rather than zero-valued penalties. The ranking version is currently `v1.0`.

## Frontend Structure

The V1 frontend lives in `apps/web`:

- `app/`: App Router layout, landing page, onboarding page, search page, loading state, not-found page, and route-level error boundary.
- `components/ui/`: Small typed UI primitives that follow shadcn/ui-compatible composition patterns without introducing a generated component registry yet.
- `components/onboarding/`: Multi-step local preference quiz for academic, cost, career, location, campus, admissions, and category-weight inputs.
- `components/search/`: URL-synced school search experience, result cards, filter panel, pagination, and local compare tray.
- `lib/api-client.ts`: Safe fetch wrapper for backend calls, JSON error handling, and typed response usage.
- `lib/preferences.ts`: Local preference profile schema, completeness calculation, localStorage persistence, and search-parameter handoff.
- `lib/search.ts`: Frontend search filter parsing, API query serialization, and sort mapping.
- `lib/env.ts`: Environment-based API base URL resolution using `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://localhost:8000`.
- `types/api.ts`: Frontend TypeScript contracts for currently consumed API shapes.

The frontend talks to the backend over HTTP only. It does not query PostgreSQL and does not compute ranking scores. The onboarding page stores a typed V1 local preference profile in browser storage because `POST /preferences` is still planned. After completion, it routes to `/search` with the subset of preferences currently supported by `GET /schools/search`. The search page keeps filters, sort, and pagination in the URL, calls `GET /schools/search`, and treats ranking fields as optional placeholders. Local save and compare state is intentionally browser-only until persistence arrives later in V1.

## Not Implemented Yet

Health, readiness, structured school search, school profile endpoints, deterministic ranking, the frontend foundation, onboarding, and the search UI are implemented. Backend preference persistence, persisted saved schools, full comparisons, frontend profile workflows, cache, semantic retrieval, and deployment pipeline are not implemented yet.
