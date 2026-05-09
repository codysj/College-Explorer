# Deployment

Deployment is not implemented yet. This document records the intended direction so future work can stay consistent.

## Planned Environments

- Local: frontend, backend, PostgreSQL, and Redis running from developer commands and Docker services.
- Production-like: frontend on Vercel or equivalent, API on AWS App Runner or ECS/Fargate, PostgreSQL on RDS, Redis on ElastiCache or managed Redis.

## Rules

- Secrets must come from environment variables or cloud secret management.
- Do not commit `.env` files.
- Do not claim uptime, latency, or production readiness until deployment is real and measured.

## Not Implemented Yet

No Docker Compose file, cloud configuration, deployment workflow, or production environment exists yet.
