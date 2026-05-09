# College Exploration Platform

College Exploration Platform is a full-stack decision-support product for helping prospective and admitted students discover, compare, rank, and justify college choices with transparent data and deterministic scoring.

Status: V1.1 foundation complete. Application code, database schema, API routes, ranking logic, Redis, and deployment are intentionally not implemented yet.

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
- `apps/api`: FastAPI backend.
- PostgreSQL with pgvector for structured and semantic college data.
- Redis for cache-aside reads after the core V1 flows exist.
- `data/raw`, `data/processed`, and `data/seed` for source snapshots, cleaned data, and deterministic fixtures.
- `infra` for local and cloud infrastructure notes.
- `tests/e2e` for future end-to-end coverage.

## Local Setup Placeholder

No application runtime exists yet. For now, clone the repository and review the docs:

```powershell
Get-ChildItem -Recurse
```

Future setup will include frontend install/build commands, backend dependency setup, Docker services, migrations, and seed loading.

## Roadmap Summary

- V1: Production-quality MVP with database schema, FastAPI foundation, structured search, school profiles, frontend foundation, onboarding, deterministic ranking, saved schools, comparison, Redis caching, and deployment polish.
- V2: Recommendation and decision intelligence with ingestion, pgvector semantic search, similar schools, acceptance decision mode, cost/value analysis, sensitivity analysis, decision reports, and analytics.
- V3: Production hardening with auth, observability, load testing, admin data quality tools, security review, end-to-end tests, and portfolio polish.

See [tasks.md](tasks.md) for the working checklist.

## Validation Commands Placeholder

There are no real build or test commands yet. Current foundation validation is manual:

```powershell
Get-ChildItem -Recurse -File
```

Expected future commands:

- Frontend: `cd apps/web && pnpm lint && pnpm build`
- Backend: `cd apps/api && pytest`
- E2E: `pnpm exec playwright test`

## Limitations

- No database schema, migrations, seed data, API endpoints, UI pages, ranking engine, Redis cache, or deployment exists yet.
- No performance metrics are available.
- The repository is not currently initialized as a Git repository in this workspace.
- Documentation is intentionally concise and should be updated as each implementation step lands.
