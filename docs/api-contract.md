# API Contract

No API is implemented yet. This file records the intended contract surface and must be updated as endpoints are added.

## Planned V1 Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health and build metadata. |
| `GET` | `/schools/search` | Structured school search with filters, sorting, and pagination. |
| `GET` | `/schools/{id}` | Full school profile. |
| `POST` | `/preferences` | Create or update onboarding preference profile. |
| `POST` | `/rankings` | Rank candidate schools against deterministic preferences. |
| `POST` | `/saved-schools` | Save or update school list status. |
| `GET` | `/saved-schools` | Fetch saved schools. |
| `POST` | `/comparisons` | Create a comparison session. |
| `GET` | `/comparisons/{id}` | Read comparison output. |

## Contract Rules

- Request and response schemas should be typed with Pydantic on the backend.
- Frontend types should be generated or kept in sync with backend schemas.
- Errors should use stable status codes and user-safe messages.
- Missing data should be represented explicitly instead of disguised as zero.
