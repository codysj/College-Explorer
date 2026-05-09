# API Contract

V1.4 implements process health, DB readiness, and structured school search. Profile, preference persistence, saved schools, comparisons, semantic search, and ranking logic are not implemented yet.

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

### `GET /schools/search`

Structured school search for search-result cards. This endpoint does not return full profiles and does not compute rankings.

Query parameters:

| Name | Type | Rules |
| --- | --- | --- |
| `query` | string | Optional school-name search, max 120 chars. |
| `state` | string | Optional 2-letter state code. |
| `region` | string | Optional region, max 32 chars. |
| `type` | string | Optional school type, max 32 chars. |
| `setting` | string | Optional campus setting, max 32 chars. |
| `min_enrollment` | integer | Optional, `>= 0`. |
| `max_enrollment` | integer | Optional, `>= 0`; must be >= `min_enrollment` when both are present. |
| `min_net_price` | integer | Optional, `>= 0`. |
| `max_net_price` | integer | Optional, `>= 0`; must be >= `min_net_price` when both are present. |
| `min_acceptance_rate` | number | Optional, `0` to `1`. |
| `max_acceptance_rate` | number | Optional, `0` to `1`; must be >= `min_acceptance_rate` when both are present. |
| `min_graduation_rate` | number | Optional, `0` to `1`. |
| `max_graduation_rate` | number | Optional, `0` to `1`; must be >= `min_graduation_rate` when both are present. |
| `sort` | enum | `name`, `net_price`, `graduation_rate`, `acceptance_rate`, or `enrollment`. Defaults to `name`. |
| `direction` | enum | `asc` or `desc`. Defaults to `asc`. |
| `page` | integer | Defaults to `1`; must be `>= 1`. |
| `page_size` | integer | Defaults to `20`; must be `1` to `50`. |

Example request:

```text
GET /schools/search?state=CA&min_net_price=15000&max_net_price=40000&sort=net_price&page=1&page_size=10
```

Response `200`:

```json
{
  "results": [
    {
      "school_id": 40,
      "name": "Sun Coast State University",
      "city": "San Diego",
      "state": "CA",
      "type": "Public",
      "setting": "Urban",
      "enrollment": 27100,
      "acceptance_rate": 0.37,
      "net_price": 17600,
      "graduation_rate": 0.76,
      "fit_score": null,
      "confidence_score": null,
      "top_reasons": [],
      "top_tradeoffs": []
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_results": 3,
  "has_next": false
}
```

No-result responses use an empty `results` array with pagination metadata.

## Error Format

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed."
  }
}
```

Validation errors generally return `422`. Unexpected server errors return `500`.

## Query Strategy

Structured search joins `schools` to `school_costs` and `school_academics` with left joins, composes filters through SQLAlchemy expressions, counts the filtered result set, applies deterministic sorting, and then applies offset/limit pagination. Route handlers do not write SQL directly.

## Planned V1 Endpoints

| Method | Path | Purpose | Stage |
| --- | --- | --- | --- |
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
