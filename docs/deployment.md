# Deployment

V1.13 makes the repository deployment-ready with Dockerfiles, Docker Compose service wiring, documented environment variables, CORS configuration, and CI validation. No public production environment has been verified yet.

## Local Environments

### Service-only local development

Use this path when actively editing the backend or frontend from the host machine:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres redis
```

Then start the API and frontend from separate terminals:

```powershell
.\.venv\Scripts\activate
cd apps/api
alembic upgrade head
python scripts/seed_database.py --reset
uvicorn main:app --reload
```

```powershell
cd apps/web
npm run dev
```

Startup order: PostgreSQL and Redis first, migrations second, seed data third, API fourth, frontend last.

### Full Docker local startup

Use this path to validate container packaging:

```powershell
docker compose up --build
```

Compose starts:

- `web`: Next.js standalone production server on `http://localhost:3000`.
- `api`: FastAPI container on `http://localhost:8000`.
- `postgres`: PostgreSQL 16 with pgvector support on port `5432`.
- `redis`: Redis 7 on port `6379`.

The API container runs Alembic migrations on startup. It does not reset or seed data automatically, because automatic destructive seed resets are unsafe for shared environments. Seed manually when needed:

```powershell
docker compose exec api python scripts/seed_database.py --reset
```

## Environment Variables

| Variable | Environment | Required in production | Notes |
| --- | --- | --- | --- |
| `APP_ENV` | API | Yes | Use values such as `production`, `staging`, or `development`. |
| `DATABASE_URL` | API, migrations, seed script | Yes | SQLAlchemy URL for PostgreSQL. Use secret storage. |
| `NEXT_PUBLIC_API_BASE_URL` | Web | Yes | Public browser-facing URL for the FastAPI service. |
| `CORS_ORIGINS` | API | Yes | Comma-separated frontend origins. Keep narrow in production. |
| `REDIS_URL` | API | Recommended | Managed Redis URL for cache-aside reads. |
| `REDIS_ENABLED` | API | No | Set `false` if Redis is not available. |
| `CACHE_KEY_VERSION` | API | No | Bump to invalidate cache namespace. |
| `CACHE_SEARCH_TTL_SECONDS` | API | No | Defaults to `300`. |
| `CACHE_PROFILE_TTL_SECONDS` | API | No | Defaults to `3600`. |
| `CACHE_RANKING_TTL_SECONDS` | API | No | Defaults to `300`. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | Docker local | No | Local container defaults only. Do not reuse local password in production. |

Secrets must come from provider environment settings, AWS Secrets Manager, Vercel environment variables, or equivalent secret storage. Do not commit `.env`.

## Frontend Deployment

Recommended target: Vercel or an equivalent Next.js host.

Configuration:

- Root directory: `apps/web`.
- Install command: `npm ci`.
- Build command: `npm run build`.
- Output: Next.js managed output on Vercel, or standalone output from `apps/web/Dockerfile`.
- Required environment variable: `NEXT_PUBLIC_API_BASE_URL=https://<api-host>`.

The frontend does not need direct database or Redis credentials.

## Backend Deployment

Recommended target: AWS App Runner or ECS/Fargate using `apps/api/Dockerfile`.

Container behavior:

- Exposes port `8000`.
- Runs `uvicorn main:app --host 0.0.0.0 --port 8000` by default.
- Uses `DATABASE_URL`, Redis variables, and CORS variables from the environment.

Deployment startup should run migrations before the API receives traffic. Options:

- App Runner/ECS pre-deploy step that executes `alembic upgrade head`.
- One-off ECS task using the same API image.
- CI/CD migration job after database backup and before service rollout.

Do not run `python scripts/seed_database.py --reset` against production data.

## PostgreSQL

Local: Docker Compose `postgres` service.

Production-like target: AWS RDS PostgreSQL or equivalent managed PostgreSQL with the `vector` extension available before running V2.2 migrations.

Required setup:

- Create a database and application user.
- Store credentials in secret management.
- Set `DATABASE_URL` for the API and migration job.
- Run Alembic migrations.
- Load only approved seed/demo data in non-production environments.

pgvector is planned for V2 semantic retrieval and is not required for V1.13.

## Redis

Local: Docker Compose `redis` service.

Production-like target: AWS ElastiCache Redis or equivalent managed Redis.

Redis is optional for correctness. If Redis is unavailable or `REDIS_ENABLED=false`, the API logs fallback behavior and serves reads from PostgreSQL.

## CI

GitHub Actions currently validates:

- Frontend dependency install with `npm ci`.
- Frontend lint with `npm run lint`.
- Frontend typecheck with `npm run typecheck`.
- Frontend production build with `npm run build`.
- Playwright smoke tests with Chromium.
- Backend dependency install and `pytest`.
- Docker Compose syntax with `docker compose config`.

Future deployment automation can add image build/push and provider-specific deploy steps after a real hosting target is selected.

## Production Safety Rules

- Keep `CORS_ORIGINS` narrow; do not use wildcard CORS for production.
- Do not commit secrets or real student data.
- Do not reset or reseed production databases.
- Treat missing school data as unknown, not zero.
- Do not claim uptime, p95 latency, cache hit rate, user counts, or database reduction until measured in the deployed environment.

## Current Limitations

- No public hosted frontend/backend URL has been verified.
- No TLS, DNS, custom domain, or cloud IAM configuration is committed.
- No production observability stack exists yet.
- No load testing or production latency baseline exists yet.
