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

## Backend Structure

The V1.3 FastAPI foundation lives in `apps/api`:

- `main.py`: app factory, router registration, and exception handler registration.
- `api/`: HTTP routers and request dependencies.
- `core/`: settings, logging, and global error handling.
- `db/`: SQLAlchemy base, engine, and session factory.
- `models/`: SQLAlchemy ORM models matching the Alembic schema.
- `schemas/`: Pydantic API request/response models.
- `repositories/`: data access layer. SQL belongs here, not in route handlers.
- `services/`: business logic layer placeholders between routes and repositories.
- `tests/`: pytest tests for backend behavior.

Request flow should be `routes -> services -> repositories -> database`. Routes own HTTP concerns, services own product logic, repositories own persistence, and models mirror database tables.

## Not Implemented Yet

Only health/readiness endpoints are implemented. Search, profiles, ranking, saved schools, comparisons, frontend app, cache, semantic retrieval, and deployment pipeline are not implemented yet.
