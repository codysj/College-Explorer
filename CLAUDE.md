# College Exploration Platform

Full project spec: docs/SPEC.md (read on demand, not by default)
Current task tracker: tasks.md (always check before starting work)
V3 roadmap and priority rationale: docs/roadmap.md (read before starting any V3 task)
Architecture: docs/architecture.md
API contract: docs/api-contract.md
Scoring methodology: docs/scoring-methodology.md
Data dictionary: docs/data-dictionary.md

## Stack
- Frontend: Next.js App Router + TypeScript + Tailwind + shadcn/ui (apps/web)
- Backend: FastAPI + Pydantic + SQLAlchemy (apps/api)
- DB: PostgreSQL 16 + pgvector (Docker for dev, RDS for prod)
- Cache: Redis (Docker for dev)
- Tests: pytest (backend), Playwright (frontend, unit + journey)
  - No Vitest/RTL. The frontend logic worth asserting is a handful of pure helpers
    already exercised through Playwright; a second runner would be config and CI time
    for coverage that exists. Add it if component-level tests become the bottleneck.

## Commands
- Web: `cd apps/web && npm run dev | npm run lint | npm run typecheck | npm run build`
- Web tests: `cd apps/web && npm run test:e2e` (Playwright; starts its own dev server)
- API: `cd apps/api && python -m uvicorn main:app --reload`
- API tests: `python -m pytest apps/api/tests` from the repo root
- DB: `docker compose up -d postgres redis`
- Migrations: `cd apps/api && alembic upgrade head`
- Real data: `python apps/api/scripts/fetch_scorecard.py --api-key "$SCORECARD_API_KEY"`
- Retrieval eval: `python apps/api/scripts/evaluate_retrieval.py --per-query` (offline, no Postgres; labels in `data/evaluation/retrieval_queries.json`)

Uses npm (package-lock.json) and a plain venv + requirements.txt. There is no pnpm
lockfile, pyproject.toml, or uv.lock - do not use `pnpm` or `uv run`.

## Hard rules (from spec section 3.3)
- Never build V2 features before V1 is complete and stable
- Never replace deterministic ranking with LLM output
- Never invent performance numbers — mark as placeholder if not measured
- Never use string-concatenated SQL; parameterized only
- Missing data is never zero unless zero is semantically correct
- All API responses are typed (Pydantic on backend, generated types on frontend)

## Conventions
- Repository pattern: SQL stays in repos/, never in route handlers
- Cache keys include ranking_version and schema_version
- Every ranking change requires a bumped ranking_version constant
- New endpoints update docs/api-contract.md in the same commit

## Definition of done (spec 3.4)
Functional + Technical + Tested + UX-coherent + Documented.
Don't claim a milestone is done until all five gates pass.