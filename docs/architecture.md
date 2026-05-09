# Architecture

This document captures the target architecture for the College Exploration Platform. It is a placeholder until the application layers are implemented.

## Target Shape

- `apps/web`: Next.js frontend for onboarding, search, school profiles, comparison, and decision workflows.
- `apps/api`: FastAPI backend for typed REST endpoints, validation, search, ranking, comparison, and data access.
- PostgreSQL: canonical structured college data and user-owned decision state. The V1.2 schema exists under `apps/api/alembic`.
- pgvector: semantic retrieval for V2 after structured V1 search is stable.
- Redis: cache-aside layer for repeated read-heavy queries after V1 APIs exist.
- `data/raw`: raw source snapshots, usually large and not committed.
- `data/processed`: cleaned local development data.
- `data/seed`: small deterministic fixtures for tests and demos.
- `infra`: local and cloud infrastructure notes and configuration.

## Boundaries

- The frontend must not query PostgreSQL directly.
- The backend owns validation, persistence, scoring, ranking, and API contracts.
- Data ingestion should stay separate from user-facing API routes.
- Deterministic ranking and reason codes must stay separate from any future LLM copy generation.

## Not Implemented Yet

No API service, frontend app, cache, semantic retrieval, or deployment pipeline exists yet. The database schema and synthetic seed data are present for local development.
