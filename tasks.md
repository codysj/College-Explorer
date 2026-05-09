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
- [ ] V1.6 Next.js frontend foundation
  - Add Next.js App Router app, styling foundation, reusable UI primitives, and frontend validation.
- [ ] V1.7 Search UI
  - Add filterable search experience, cards, sorting, pagination, empty states, and error states.
- [ ] V1.8 Onboarding and preference profile
  - Capture student preferences and produce a profile usable by deterministic ranking.
- [ ] V1.9 Deterministic ranking engine
  - Implement tested weighted scoring, reason codes, tradeoffs, confidence, and `ranking_version`.
- [ ] V1.10 School profile frontend
  - Build school detail pages using profile data, fit summaries, and honest missing-data states.
- [ ] V1.11 Saved schools and comparison MVP
  - Add saved school state and side-by-side comparison workflow.
- [ ] V1.12 Redis cache-aside
  - Cache repeated search, profile, and ranking reads with versioned keys.
- [ ] V1.13 Deployment and README polish
  - Deploy the app, add screenshots, document measured performance, and finalize setup notes.

## V2: Recommendation and Decision Intelligence

- [ ] V2.1 Data ingestion pipeline
- [ ] V2.2 pgvector semantic search
- [ ] V2.3 Similar-school discovery
- [ ] V2.4 Acceptance decision mode
- [ ] V2.5 Cost/value calculator
- [ ] V2.6 Sensitivity analysis
- [ ] V2.7 Shareable decision report
- [ ] V2.8 Analytics and ranking evaluation

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

## Next Recommended Task

V1.6 Next.js frontend foundation.
