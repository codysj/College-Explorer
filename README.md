# College Exploration Platform

College Exploration Platform is a full-stack decision-support product for helping prospective and admitted students discover, compare, rank, and justify college choices with transparent data and deterministic scoring.

Status: V1.12 Redis cache-aside complete. pgvector, authenticated persistence, and deployment are intentionally not implemented yet.

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
- Redis for cache-aside reads on search, profile, and ranking responses.
- `data/raw`, `data/processed`, and `data/seed` for source snapshots, cleaned data, and deterministic fixtures.
- `infra` for local and cloud infrastructure notes.
- `tests/e2e` for future end-to-end coverage.

## Local Setup

The local PostgreSQL database and Redis cache can be started with Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
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

### Redis Cache

The backend uses Redis as an optional cache-aside layer for repeated read-heavy responses:

- `GET /schools/search`: 5 minute TTL.
- `GET /schools/{id}`: 60 minute TTL.
- `POST /rankings`: 5 minute TTL.

Cache keys include the endpoint resource type, normalized request parameters, `CACHE_KEY_VERSION`, and `RANKING_VERSION` for ranking responses. Example key shapes:

```text
college-exploration:cache:v1:search:{sha256-digest}
college-exploration:cache:v1:school-profile:{sha256-digest}
college-exploration:cache:v1:ranking:{sha256-digest}
```

Redis configuration:

| Variable | Default | Purpose |
| --- | --- | --- |
| `REDIS_URL` | `redis://localhost:6379/0` | Backend Redis connection URL. |
| `REDIS_ENABLED` | `true` | Set to `false` to use database reads only. |
| `CACHE_KEY_VERSION` | `v1` | Manual namespace bump for cache invalidation. |
| `CACHE_SEARCH_TTL_SECONDS` | `300` | Search response TTL. |
| `CACHE_PROFILE_TTL_SECONDS` | `3600` | School profile response TTL. |
| `CACHE_RANKING_TTL_SECONDS` | `300` | Ranking response TTL. |

If Redis is down or disabled, the API logs the fallback and continues serving from PostgreSQL.

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
- Saved schools dashboard: `http://localhost:3000/dashboard`
- Comparison workspace: `http://localhost:3000/compare`
- School profile: `http://localhost:3000/schools/1`

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
docker compose up -d postgres redis
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
- V1.11 saved-school and comparison state is local to the current browser. V2/V3 should move these records to user-owned backend persistence once authentication and privacy boundaries exist.
- The frontend has a landing page, onboarding, search UI, school profile pages, a saved schools dashboard, a comparison workspace, route shell, UI primitives, and typed API client, but no backend preference persistence or authenticated saved-school/comparison persistence yet.
- Onboarding stores a typed `PreferenceProfile` in browser `localStorage` and forwards supported filters such as state, setting, school type, and max net price to `/search`.
- Search supports structured filters, sort controls, URL state, pagination, local save/compare actions, loading/empty/error states, and API-backed result cards.
- School profiles call `GET /schools/{id}`, render fit summary placeholders, academics, cost, outcomes, campus life, data-quality metadata, save/compare controls, and a V2 similar-schools placeholder.
- Saved schools and compare selections use browser `localStorage` in V1.11 because there is no authenticated user session yet. Saved schools are stored under `college-exploration.saved-schools.v1` with statuses `interested`, `applying`, `accepted`, `finalist`, and `removed`; compare selections are stored under `college-exploration.compare-schools.v1` with a 5-school limit.
- `/dashboard` groups active saved schools by status, supports quick status changes/removal, and links back to profile pages. `/compare` fetches selected school profiles and renders deterministic metric comparisons, category winners, and tradeoff summaries for 2 to 5 schools.
- The "Best fit" sort is a UI placeholder until the frontend calls `POST /rankings`.
- Profile fit score, category scores, top reasons, top tradeoffs, and ranking version remain unavailable on `GET /schools/{id}` unless the backend later adds or composes ranking output. The profile page labels these states explicitly as unavailable and uses `data_confidence_score` only as data-completeness confidence.
- Redis cache-aside is implemented for search, profiles, and rankings with lightweight hit/miss/write-failure logging. No semantic cache, distributed invalidation, pgvector integration, or deployment exists yet.
- Performance validation is limited to reproducible cache hit logs and tests showing repeated calls avoid repository/database reads; no production latency metrics are available.
- Seed data is synthetic and intended for deterministic local development, not factual school reporting.
- Playwright smoke coverage exists for search, onboarding, school profiles, saved schools, compare tray behavior, compare limit enforcement, and comparison rendering.
- README screenshot checklist for V1.13: landing page, onboarding completion, search with filters, school profile fit summary, profile missing-data state, saved schools dashboard, compare tray, and comparison workspace.
- Documentation is intentionally concise and should be updated as each implementation step lands.
