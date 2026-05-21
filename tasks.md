# College Exploration Platform Task Tracker

Legend: `[ ]` not started, `[~]` in progress, `[x]` complete.

## V1: Production-Quality MVP

- [x] V1.1 Repo foundation and documentation
  - Monorepo directories, foundation docs, root agent instructions, environment example, and CI skeleton are in place.
  - Validation is limited to manual structure checks because no app runtime exists yet.
- [x] V1.2 Database schema and seed data
  - Added Docker Compose PostgreSQL, Alembic initial schema, search indexes, deterministic synthetic seed data, seed loader, and data dictionary.
  - Local execution depends on Docker and Python tooling being available.
- [x] V1.3 FastAPI foundation
  - Added FastAPI app factory, health/readiness endpoints, Pydantic settings, SQLAlchemy session wiring, ORM models, schemas, repository/service placeholders, structured logging, error handlers, and pytest health coverage.
- [x] V1.4 Structured search API
  - Added `/schools/search` with typed filters, range validation, sorting, pagination, SQLAlchemy repository query, query timing logs, response placeholders for future ranking, and endpoint tests.
  - Runtime validation and `.venv` creation still need a shell with Python available on PATH.
- [x] V1.5 School profile API
  - Added `/schools/{id}` full profile responses composed from core, academic, cost, outcome, and campus-life tables.
  - Added explicit missing-data metadata, completeness confidence scoring, 404 handling, tests, and API/README documentation.
- [x] V1.6 Next.js frontend foundation
  - Added a Next.js App Router TypeScript app, Tailwind styling foundation, route metadata/loading/error states, shadcn-compatible UI primitives, typed API client, and landing page.
  - Frontend validation uses `npm run lint` and `npm run build` from `apps/web`.
- [x] V1.7 Search UI
  - Added `/search` with URL-synced filters, sort controls, active chips, API-backed school cards, pagination, loading/empty/error states, local save/compare actions, and a compare tray.
  - Added a Playwright smoke test that loads search, applies a state filter, and verifies updated results.
- [x] V1.8 Onboarding and preference profile
  - Added `/onboarding` multi-step preference capture for academic, cost, career, location, campus, admissions, and category-weight inputs.
  - Stores a typed local `PreferenceProfile`, computes completeness, forwards supported filters to `/search`, and documents the backend/ranking integration gap.
- [x] V1.9 Deterministic ranking engine
  - Added backend deterministic ranking service, weighted category scoring, confidence, hard constraints, reason-code explanations, `POST /rankings`, tests, and scoring/API documentation.
- [x] V1.10 School profile frontend
  - Added `/schools/[id]` with typed profile fetching, metadata, loading/error states, profile sections, explicit unavailable-data handling, local save/compare integration, and Playwright smoke coverage.
- [x] V1.11 Saved schools and comparison MVP
  - Added typed browser-local saved school state with statuses, dashboard grouping, quick status updates, removal, duplicate prevention, and profile links.
  - Added typed browser-local compare state, sticky cross-page tray, 5-school limit, `/compare` workspace, deterministic metric summaries, category winners, and tradeoff summaries.
  - Persistence remains localStorage-only until auth-backed V2/V3 user persistence exists.
- [x] V1.12 Redis cache-aside
  - Cache repeated search, profile, and ranking reads with versioned keys.
- [x] V1.13 Deployment and README polish
  - Added Dockerfiles for frontend/backend, full-stack Docker Compose wiring, CORS environment configuration, CI typecheck and Docker Compose validation, deployment notes, performance notes, screenshot checklist, and recruiter-facing README polish.
  - No public hosted deployment or production performance metrics have been claimed.

## V2: Recommendation and Decision Intelligence

- [x] V2.1 Data ingestion pipeline
  - Added deterministic raw import, normalization, missing-value handling, derived attributes, validation, and seed/refresh CSV output.
  - Added source metadata fields, public-data-style fixtures, and focused ingestion tests.
  - Full local pytest validation still needs a Python 3.12 environment with project dependencies installed; dependency-light CLI and manual ingestion test validation passed.
- [x] V2.2 pgvector semantic search
  - Added pgvector embedding storage, deterministic school search documents, local/test hash embeddings, refresh CLI, semantic endpoint, hybrid retrieval with deterministic re-ranking, Redis cache keys, and focused backend tests.
  - Full migration validation against PostgreSQL still needs local Docker/Postgres because the current shell did not have system Python on PATH; `.venv` Python test validation passed for semantic-search coverage.
- [x] V2.3 Similar-school discovery
  - Added `GET /schools/{id}/similar`, semantic/fallback source-school retrieval, deterministic variant constraints, similarity scoring, cache keys, backend tests, and profile-page variant cards.
  - Frontend runtime validation still needs local Node/npm dependencies; backend validation passed in the available `.venv`.
- [x] V2.4 Acceptance decision mode
  - Added acceptance/finalist offer capture, deterministic decision reports, confidence flags for missing financial/preferences/outcomes data, backend decision endpoints, report-ready frontend workspace, and focused backend/frontend tests.
  - Full frontend runtime validation still needs Node/npm dependencies available in the shell.
- [x] V2.5 Cost/value calculator
  - Added `POST /cost-calculator`, deterministic yearly/four-year cost, debt exposure, repayment sensitivity scenarios, outcome-adjusted directional value, affordability indicators, confidence warnings, and frontend calculator surfaces in `/decision` and `/compare`.
  - Frontend runtime validation still needs Node/npm dependencies available in the shell.
- [x] V2.6 Sensitivity analysis
  - Added `POST /sensitivity`, deterministic scenario reranking through the existing ranking engine, movement/stability/volatility outputs, confidence impacts, category drivers, Redis cache support, and compare-page slider UI.
  - Full frontend runtime validation still needs Node/npm dependencies available in the shell.
- [x] V2.7 Shareable decision report
  - Expanded `POST /decision/report` into a structured briefing with top recommendation, finalist ranking table, category scores, cost/value comparison, deterministic sensitivity highlights, major tradeoffs, unresolved questions, confidence flags, methodology/disclaimer language, snapshot support, and printable/shareable frontend route.
  - Production-grade authenticated sharing, hosted URLs, and PDF generation remain V3 scope.
- [x] V2.8 Analytics and ranking evaluation
  - Added typed privacy-safe analytics events, `/analytics/events`, `/analytics/summary`, backend instrumentation for search/profile/ranking/semantic/sensitivity/report flows, frontend save/compare/onboarding/report fallback event logging, internal `/analytics` dashboard, ranking evaluation aggregations, and bias/privacy documentation.
  - Production observability, authenticated user-scoped analytics, alerting, and warehouse-style BI remain V3 scope.

## V3: Production Hardening and Portfolio Polish

- [ ] V3.1 Authentication and account persistence
- [ ] V3.2 Observability and performance dashboard
- [ ] V3.3 Load testing and query optimization
- [ ] V3.4 Admin data quality console
- [ ] V3.5 Security and privacy hardening
- [ ] V3.6 End-to-end test suite
- [ ] V3.7 Portfolio/demo polish

## Session Log

- 2026-05-09: Completed V1.1 foundation pass. Preserved the existing skeleton, added root documentation and guardrails, created `.env.example`, added non-failing CI placeholders, and kept implementation scope limited to repository foundation.
- 2026-05-09: Completed V1.2 database foundation. Added local PostgreSQL Compose config, Alembic migration, seed CSV and loader, README setup commands, and updated data dictionary.
- 2026-05-09: Completed V1.3 FastAPI foundation. Added backend app structure, health/readiness endpoints, DB session wiring, typed schema placeholders, repository/service layers, logging/error handling, tests, and API docs.
- 2026-05-09: Completed V1.4 structured search API. Added local venv/dependency docs, root requirements entrypoint, typed search endpoint, repository query composition, search tests, and API contract examples.
- 2026-05-09: Stabilized backend dependency setup for Windows. Standardized Python `>=3.12,<3.13`, relaxed wheel-friendly dependency ranges, updated install troubleshooting, and documented how to avoid native Rust/MSVC builds.
- 2026-05-09: Completed V1.5 school profile API. Added a single-query profile read across all school profile tables, structured profile schemas, missing-field tracking, completeness confidence scoring, route tests, and profile docs.
- 2026-05-09: Completed V1.6 Next.js frontend foundation. Added the App Router app, Tailwind setup, reusable UI primitives, safe API client, polished landing page, and frontend setup documentation.
- 2026-05-09: Completed V1.7 Search UI. Added API-backed structured search, shareable URL filter state, result cards, local save/compare UI, pagination, and Playwright smoke coverage.
- 2026-05-09: Completed V1.8 onboarding and preference profile. Added the local multi-step preference quiz, completeness indicator, local profile persistence, search handoff, schema docs, and Playwright smoke coverage.
- 2026-05-09: Completed V1.9 deterministic ranking engine. Added V1.0 category scoring, normalized weights, hard constraints, deterministic reasons/tradeoffs, ranked API output, backend tests, and scoring methodology docs.

- 2026-05-11: Completed V1.10 school profile frontend. Added the detail route, profile presentation sections, shared local save/compare state, dynamic metadata, profile smoke test, and docs updates. API assumption: `GET /schools/{id}` does not currently include `confidence_score` or `ranking_version`; the page uses `data_confidence_score` for data completeness and marks ranking fields unavailable.
- 2026-05-15: Completed V1.11 saved schools and comparison MVP. Added localStorage-backed saved school statuses, `/dashboard`, a cross-page compare tray, `/compare`, deterministic comparison helpers, Playwright coverage, docs updates, and `acceptance_rate` on `GET /schools/{id}` for comparison metrics.
- 2026-05-15: Completed V1.12 Redis cache-aside. Added Docker Redis support, environment-driven cache settings, centralized cache service, cache-aside reads for search/profile/ranking responses, versioned ranking keys, TTL policy documentation, hit/miss/fallback logging, and mock-backed cache tests.
- 2026-05-15: Completed V1.13 deployment and README polish. Added production-oriented Dockerfiles, full-stack Compose services, local/prod environment documentation, narrow CORS configuration, CI frontend typecheck and Compose validation, architecture diagram, screenshot checklist, honest performance notes, and a recruiter-facing README. Public cloud deployment remains unverified.
- 2026-05-20: Completed V2.1 data ingestion pipeline. Added deterministic raw import, normalization, missing-value handling, derived attributes, validation, seed/refresh CSV output, source metadata columns, fixture coverage, and ingestion usage docs.
- 2026-05-21: Completed V2.2 pgvector semantic search. Added school embedding table/migration, structured document generation, local deterministic embedding provider, refresh CLI, `POST /semantic-search`, pgvector/fallback candidate retrieval, structured hard-constraint preservation, semantic reason tags, cache keys, and tests.
- 2026-05-21: Completed V2.3 similar-school discovery. Added variant-aware similar-school API, deterministic fallback, source exclusion, Redis cache support, explainable reasons/tradeoffs, frontend profile integration with variant controls, and backend/frontend test coverage updates.
- 2026-05-21: Completed V2.4 acceptance decision mode. Added accepted/finalist offer models, `/decision/offers` and `/decision/report`, deterministic category-based decision summaries, confidence/uncertainty flags, a browser-local accepted-schools workspace with editable offer cards and report panel, and updated docs/tests.
- 2026-05-21: Completed V2.5 cost/value calculator. Added deterministic cost/value API and service, calculator schemas, backend tests for cost, aid, debt sensitivity, missing data, and validation, plus editable calculator experiences in decision and compare workflows with Playwright smoke coverage updates.
- 2026-05-21: Completed V2.6 sensitivity analysis. Added deterministic sensitivity schemas/service/route, selected-school candidate reads, scenario weight normalization, stable/volatile classification, category drivers, confidence impacts, cache keys, compare-page sliders, movement table, stability badges, backend tests, and docs updates.
- 2026-05-21: Completed V2.7 shareable decision report. Expanded the decision report contract, reused deterministic ranking/cost/sensitivity logic, added cost/value and sensitivity report sections, persisted report snapshots, added browser-local latest-report storage, built `/decision/report` printable briefing view, extended Playwright coverage, and updated docs.
- 2026-05-21: Completed V2.8 analytics and ranking evaluation. Added privacy-safe event schemas, analytics repository/service/routes, endpoint and frontend instrumentation, internal analytics dashboard, ranking evaluation metrics for fit buckets/rank positions/reason codes/confidence/version usage, tests, and documentation of limitations.

## Next Recommended Task

V3 Production Hardening and Portfolio Polish.
