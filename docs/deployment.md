# Deployment

Deployment is not implemented yet. This document records the intended direction so future work can stay consistent.

## Planned Environments

- Local: frontend, backend, PostgreSQL, and Redis running from developer commands and Docker services.
- Production-like: frontend on Vercel or equivalent, API on AWS App Runner or ECS/Fargate, PostgreSQL on RDS, Redis on ElastiCache or managed Redis.

## Frontend Configuration

The V1.6 frontend is a local Next.js app in `apps/web`. It currently expects:

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Public base URL for the FastAPI service. Defaults to `http://localhost:8000` in the frontend client when unset. |

Local validation:

```powershell
cd apps/web
npm install
npm run lint
npm run build
```

## Rules

- Secrets must come from environment variables or cloud secret management.
- Do not commit `.env` files.
- Do not claim uptime, latency, or production readiness until deployment is real and measured.

## Not Implemented Yet

No frontend hosting, API hosting, cloud configuration, deployment workflow, or production environment exists yet.
