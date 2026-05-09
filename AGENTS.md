# Agent Instructions

These instructions apply to Codex and other LLM coding agents working in this repository.

## Coding Standards

- Read `README.md`, `tasks.md`, `docs/architecture.md`, and the docs relevant to the current task before editing.
- Use Python `>=3.12,<3.13` for backend work. Do not move the project to Python 3.14 until dependency wheel compatibility is verified.
- Keep each implementation step small and aligned with the V1/V2/V3 roadmap.
- Prefer typed contracts and explicit validation over ad hoc objects.
- Keep SQL out of route handlers when backend code is added; use repository or service modules.
- Use parameterized SQL only. Never concatenate user input into SQL.
- Treat missing data as unknown, not as zero, unless zero is semantically correct.
- Keep application logic deterministic where user decisions depend on ranking, sorting, filtering, or scoring.

## Validation Commands

Database commands available after V1.2:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip cache purge
python -m pip install -r apps/api/requirements.txt
docker compose up -d postgres
cd apps/api
alembic upgrade head
python scripts/seed_database.py --reset
pytest
```

Expected future app commands:

```powershell
cd apps/web; pnpm lint; pnpm build
cd apps/api; pytest
pnpm exec playwright test
```

Until those runtimes exist, validate foundation changes with:

```powershell
Get-ChildItem -Recurse -File
```

Do not fix Windows dependency installation failures by adding Visual Studio Build Tools or Rust requirements. If `pydantic-core`, `maturin`, or `link.exe` errors appear, recreate the venv with Python 3.12 and reinstall from wheels.

## Documentation Update Rules

- Update `tasks.md` whenever a roadmap item changes status.
- Update `docs/api-contract.md` in the same change as any endpoint contract.
- Update `docs/data-dictionary.md` in the same change as schema, seed, or data-source changes.
- Update `docs/scoring-methodology.md` in the same change as ranking or explanation logic.
- Update `docs/deployment.md` when infrastructure, environment variables, or deployment steps change.
- Do not claim measured performance, users, uptime, or deployment status unless those facts have been verified.

## LLM Guardrails

- Do not build V2 or V3 features before the required V1 foundation is stable.
- Do not invent college facts, data-source freshness, performance numbers, users, or deployment status.
- Do not present the product as admissions advice, guaranteed ROI, or financial advice.
- Do not store sensitive student details without clear product boundaries and privacy documentation.
- Prefer fixtures, seed data, tests, and typed schemas over mock-only demos.

## Ranking and Generated Text

Keep deterministic ranking separate from LLM-generated text.

- Ranking scores, sort order, category scores, confidence, reason codes, and tradeoffs must come from deterministic code and structured data.
- LLM-generated text may later summarize known deterministic outputs, but it must not create school facts, change scores, decide rankings, or hide missing data.
- Every ranking logic change must update the scoring methodology docs and use a versioned ranking constant once the ranking engine exists.
