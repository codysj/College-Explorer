# API Contract

V1.3 defines the FastAPI foundation, health/readiness endpoints, and typed schema placeholders. Search, profile, preference persistence, saved schools, comparisons, and ranking logic are not implemented yet.

## Implemented Endpoints

### `GET /health`

Process-level health check. It does not require a database connection.

Response `200`:

```json
{
  "status": "ok",
  "service": "College Exploration API",
  "environment": "development",
  "version": "0.3.0",
  "timestamp": "2026-05-09T12:00:00Z"
}
```

### `GET /ready`

Readiness check. Executes `SELECT 1` through the SQLAlchemy database session.

Response `200`:

```json
{
  "status": "ready",
  "database": "ok",
  "timestamp": "2026-05-09T12:00:00Z"
}
```

If the database is unavailable, the global exception handler returns a standardized `500` response.

## Error Format

```json
{
  "error": {
    "code": "http_404",
    "message": "Not found"
  }
}
```

Validation errors use `validation_error`. Unexpected server errors use `internal_server_error`.

## Schema Placeholders

### `SchoolSummary`

Fields: `id`, `unitid`, `name`, `city`, `state`, `region`, `type`, `setting`, `undergraduate_enrollment`, `acceptance_rate`.

### `SchoolProfile`

Placeholder profile wrapper with `school`, `top_majors`, `graduation_rate`, `net_price`, `median_earnings`, and `campus_tags`.

### `SearchRequest`

Fields: `query`, `state`, `region`, `type`, `setting`, `min_enrollment`, `max_enrollment`, `max_net_price`, `max_acceptance_rate`, `min_graduation_rate`, `sort`, `direction`, `page`, and `page_size`.

### `SearchResponse`

Fields: `results`, `page`, `page_size`, `total_results`, and `has_next`. Results are empty until V1.4 implements structured search.

### `Preference`

Fields: `intended_major`, `home_state`, `max_annual_cost`, `weights`, and `constraints`.

### `RankingResponse`

Fields: `ranking_version` and `results`. Ranking scores are structure-only until V1.9.

## Planned V1 Endpoints

| Method | Path | Purpose | Stage |
| --- | --- | --- | --- |
| `GET` | `/schools/search` | Structured school search with filters, sorting, and pagination. | V1.4 |
| `GET` | `/schools/{id}` | Full school profile. | V1.5 |
| `POST` | `/preferences` | Create or update onboarding preference profile. | V1.8 |
| `POST` | `/rankings` | Rank candidate schools against deterministic preferences. | V1.9 |
| `POST` | `/saved-schools` | Save or update school list status. | V1.11 |
| `GET` | `/saved-schools` | Fetch saved schools. | V1.11 |
| `POST` | `/comparisons` | Create a comparison session. | V1.11 |
| `GET` | `/comparisons/{id}` | Read comparison output. | V1.11 |

## Contract Rules

- Request and response schemas are Pydantic models.
- Route handlers should call services or repositories rather than writing SQL directly.
- Missing data should be represented explicitly instead of disguised as zero.
- Ranking and generated prose remain separate: ranking fields must come from deterministic code.
