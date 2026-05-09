# College Exploration Platform

College Exploration Platform is a full-stack decision-support product for helping prospective and admitted students discover, compare, rank, and justify college choices with transparent data and deterministic scoring.

Status: V1.2 database foundation complete. API routes, frontend pages, ranking logic, Redis, pgvector, and deployment are intentionally not implemented yet.

## Project Thesis

Students need more than a searchable college directory. The platform should help them move from a noisy set of schools to an explainable shortlist or enrollment decision using structured institutional data, user preferences, ranking transparency, and honest tradeoff analysis.

## Product Purpose

The product is designed around three jobs:

- Discover schools that match academic, financial, career, location, and campus preferences.
- Compare schools using consistent metrics and visible tradeoffs.
- Explain why a school ranks well without pretending to provide guaranteed admissions or financial advice.

## Architecture Placeholder

Target architecture is documented in [docs/architecture.md](docs/architecture.md). The planned stack is:

- `apps/web`: Next.js frontend.
- `apps/api`: FastAPI backend and Alembic migrations.
- PostgreSQL for structured college data. pgvector is planned for V2 semantic retrieval and is not enabled yet.
- Redis for cache-aside reads after the core V1 flows exist.
- `data/raw`, `data/processed`, and `data/seed` for source snapshots, cleaned data, and deterministic fixtures.
- `infra` for local and cloud infrastructure notes.
- `tests/e2e` for future end-to-end coverage.

## Local Setup

No API or frontend runtime exists yet. The local PostgreSQL database can be started with Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
```

Install backend database tooling:

```powershell
cd apps/api
python -m pip install -r requirements.txt
```

Run migrations:

```powershell
cd apps/api
alembic upgrade head
```

Load deterministic seed data:

```powershell
cd apps/api
python scripts/seed_database.py --reset
```

Optional schema verification with `psql`:

```powershell
psql postgresql://college:college@localhost:5432/college_exploration -f scripts/verify_schema.sql
```

The seed set lives in `data/seed/schools_seed.csv` and contains 50 synthetic schools for local development and tests.

## Roadmap Summary

- V1: Production-quality MVP with database schema, FastAPI foundation, structured search, school profiles, frontend foundation, onboarding, deterministic ranking, saved schools, comparison, Redis caching, and deployment polish.
- V2: Recommendation and decision intelligence with ingestion, pgvector semantic search, similar schools, acceptance decision mode, cost/value analysis, sensitivity analysis, decision reports, and analytics.
- V3: Production hardening with auth, observability, load testing, admin data quality tools, security review, end-to-end tests, and portfolio polish.

See [tasks.md](tasks.md) for the working checklist.

## Validation Commands

There are no frontend or API test commands yet. Current database validation commands are:

```powershell
docker compose up -d postgres
cd apps/api
alembic upgrade head
python scripts/seed_database.py --reset
```

Expected future commands:

- Frontend: `cd apps/web && pnpm lint && pnpm build`
- Backend: `cd apps/api && pytest`
- E2E: `pnpm exec playwright test`

## Limitations

- No API endpoints, UI pages, ranking engine, Redis cache, pgvector integration, or deployment exists yet.
- No performance metrics are available.
- Seed data is synthetic and intended for deterministic local development, not factual school reporting.
- App-specific validation will be added when the API and frontend runtimes exist.
- Documentation is intentionally concise and should be updated as each implementation step lands.
