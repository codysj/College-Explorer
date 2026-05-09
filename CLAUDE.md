# College Exploration Platform

Full project spec: docs/SPEC.md (read on demand, not by default)
Current task tracker: tasks.md (always check before starting work)
Architecture: docs/architecture.md
API contract: docs/api-contract.md
Scoring methodology: docs/scoring-methodology.md
Data dictionary: docs/data-dictionary.md

## Stack
- Frontend: Next.js App Router + TypeScript + Tailwind + shadcn/ui (apps/web)
- Backend: FastAPI + Pydantic + SQLAlchemy (apps/api)
- DB: PostgreSQL 16 + pgvector (Docker for dev, RDS for prod)
- Cache: Redis (Docker for dev)
- Tests: pytest, Vitest + RTL, Playwright

## Commands
- Web: `cd apps/web && pnpm dev | pnpm test | pnpm lint | pnpm build`
- API: `cd apps/api && uv run uvicorn app.main:app --reload`
- API tests: `cd apps/api && uv run pytest`
- DB: `docker compose up -d postgres redis`
- Migrations: `cd apps/api && uv run alembic upgrade head`
- E2E: `pnpm exec playwright test`

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