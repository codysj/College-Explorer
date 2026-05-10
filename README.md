# College Exploration Platform

College Exploration Platform is a full-stack decision-support product for helping prospective and admitted students discover, compare, rank, and justify college choices with transparent data and deterministic scoring.

Status: V1.9 deterministic ranking engine complete. Redis, pgvector, saved schools, comparisons, and deployment are intentionally not implemented yet.

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

The local PostgreSQL database can be started with Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
```

### Python Setup

Use Python `>=3.12,<3.13`. Python 3.12 is the supported local development version for this project. Do not use Python 3.14 yet; several native-extension dependencies may not have Windows wheels for it.

Verify your Python launcher can find Python 3.12:

```powershell
py -3.12 --version
```

### Virtual Environment Setup

Create and activate a local Python virtual environment from the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
```

Confirm the venv is active and using Python 3.12:

```powershell
python --version
python -c "import sys; print(sys.prefix)"
```

`sys.prefix` should point at this repository's `.venv` directory.

### Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip cache purge
python -m pip install -r apps/api/requirements.txt
```

Successful installs should download wheels and should not show build steps for `pydantic-core`, `psycopg`, `maturin`, Rust, or MSVC.

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

Run the FastAPI app locally:

```powershell
cd apps/api
uvicorn main:app --reload
```

Useful local URLs:

- API health: `http://127.0.0.1:8000/health`
- DB readiness: `http://127.0.0.1:8000/ready`
- Structured search: `http://127.0.0.1:8000/schools/search`
- Deterministic rankings: `http://127.0.0.1:8000/rankings`
- School profile: `http://127.0.0.1:8000/schools/1`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

Example search request:

```powershell
curl "http://127.0.0.1:8000/schools/search?state=CA&min_net_price=15000&max_net_price=40000&sort=net_price&page=1&page_size=10"
```

Example profile request:

```powershell
curl "http://127.0.0.1:8000/schools/1"
```

`GET /schools/{id}` composes a full profile from the core `schools` row plus academic, cost, outcome, and campus-life tables. Profile ranking placeholders such as `fit_score`, `category_scores`, reasons, tradeoffs, and `similar_schools` remain empty until the frontend profile workflow consumes ranking output.

Missing data is treated as unknown. The API returns `null` for missing values, lists those fields in `data_fields_missing`, and includes a simple `data_confidence_score` based on profile completeness. It does not convert missing numbers to zero or infer school facts that are not in the database.

`POST /rankings` ranks search-card results against a supplied preference profile using deterministic V1.0 category scoring, normalized weights, confidence scores, hard constraints, and reason-code explanations. Ranking does not use semantic search, ML models, or LLM-generated scoring.

### Frontend Setup

The V1.6 frontend lives in `apps/web` and uses the Next.js App Router with TypeScript, Tailwind CSS, and small shadcn/ui-compatible component primitives.

Install and validate from the frontend directory:

```powershell
cd apps/web
npm install
npm run lint
npm run build
```

Run the frontend locally:

```powershell
cd apps/web
npm run dev
```

Useful local URL:

- Web app: `http://localhost:3000`
- Onboarding: `http://localhost:3000/onboarding`
- Search UI: `http://localhost:3000/search`

Frontend environment:

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Base URL used by the typed frontend API client. |

### Windows Install Troubleshooting

If installation fails with `Failed building wheel for pydantic-core`, `maturin failed`, or `link.exe not found`, pip is trying to compile native code locally. That usually means the venv is using an unsupported or too-new Python version, or pip has cached an incompatible artifact.

Fix:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip cache purge
python -m pip install -r apps/api/requirements.txt
```

Do not install Visual Studio Build Tools or Rust for this project just to satisfy dependency installation. The supported path is Python 3.12 plus prebuilt wheels.

## Roadmap Summary

- V1: Production-quality MVP with database schema, FastAPI foundation, structured search, school profiles, frontend foundation, onboarding, deterministic ranking, saved schools, comparison, Redis caching, and deployment polish.
- V2: Recommendation and decision intelligence with ingestion, pgvector semantic search, similar schools, acceptance decision mode, cost/value analysis, sensitivity analysis, decision reports, and analytics.
- V3: Production hardening with auth, observability, load testing, admin data quality tools, security review, end-to-end tests, and portfolio polish.

See [tasks.md](tasks.md) for the working checklist.

## Validation Commands

Current validation commands are:

```powershell
py -3.12 --version
.\.venv\Scripts\activate
python --version
docker compose up -d postgres
cd apps/api
alembic upgrade head
python scripts/seed_database.py --reset
pytest
```

Frontend:

```powershell
cd apps/web
npm run lint
npm run build
npm run test:e2e
```

Expected future commands:

- Backend: `cd apps/api && pytest`
- E2E: `pnpm exec playwright test`

## Limitations

- `/health`, `/ready`, `/schools/search`, `/schools/{id}`, and `/rankings` exist. Preference persistence, saved-school, and comparison endpoints are not implemented yet.
- The frontend has a landing page, onboarding, search UI, route shell, UI primitives, and typed API client, but no backend preference persistence, persisted saved-school flows, comparison workflow, or profile pages yet.
- Onboarding stores a typed `PreferenceProfile` in browser `localStorage` and forwards supported filters such as state, setting, school type, and max net price to `/search`.
- Search supports structured filters, sort controls, URL state, pagination, local save/compare state, loading/empty/error states, and API-backed result cards.
- The "Best fit" sort is a UI placeholder until the frontend calls `POST /rankings`.
- No Redis cache, pgvector integration, or deployment exists yet.
- No performance metrics are available.
- Seed data is synthetic and intended for deterministic local development, not factual school reporting.
- End-to-end validation will be added after the product workflows exist.
- Documentation is intentionally concise and should be updated as each implementation step lands.
