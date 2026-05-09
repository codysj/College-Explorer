# API Contract

V1.8 implements process health, DB readiness, structured school search, full school profiles, and a frontend-only local preference profile. Backend preference persistence, saved schools, comparisons, semantic search, and ranking logic are not implemented yet.

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

### `GET /schools/{id}`

Full school profile composed from `schools`, `school_academics`, `school_costs`, `school_outcomes`, and `school_campus_life`. The endpoint uses a single repository query with left joins so missing optional profile rows or fields are represented as `null` rather than causing N+1 relationship loads.

Path parameters:

| Name | Type | Rules |
| --- | --- | --- |
| `id` | integer | School primary key. Returns `404` when no school exists. |

Example request:

```text
GET /schools/1
```

Response `200`:

```json
{
  "school_id": 1,
  "name": "Adams State College",
  "city": "Northbridge",
  "state": "MA",
  "region": "Northeast",
  "type": "Public",
  "setting": "Suburban",
  "enrollment": 6200,
  "academics": {
    "majors": ["Biology", "Psychology", "Business"],
    "popular_majors": ["Biology", "Psychology", "Business"],
    "graduation_rate": 0.69,
    "retention_rate": 0.82,
    "student_faculty_ratio": 15.0
  },
  "cost": {
    "tuition_in_state": 14200,
    "tuition_out_state": 31800,
    "net_price": 22100,
    "average_aid": 12600,
    "debt_median": 21000
  },
  "outcomes": {
    "median_earnings": 52000,
    "completion_rate": null,
    "repayment_rate": 0.76,
    "outcome_percentiles": null
  },
  "campus_life": {
    "sports": "DIII",
    "greek_life": 0.08,
    "housing": true,
    "weather_band": null,
    "diversity_metrics": null,
    "culture_tags": ["research", "commuter-friendly", "mid-size"]
  },
  "data_fields_missing": [
    "outcomes.completion_rate",
    "outcomes.outcome_percentiles",
    "campus_life.weather_band",
    "campus_life.diversity_metrics"
  ],
  "data_confidence_score": 0.8571,
  "fit_score": null,
  "category_scores": {},
  "top_reasons": [],
  "top_tradeoffs": [],
  "similar_schools": []
}
```

Response schema:

| Field | Type | Notes |
| --- | --- | --- |
| `school_id`, `name`, `city`, `state`, `region`, `type`, `setting`, `enrollment` | scalar | Core identity and search fields from `schools`. |
| `academics` | object | `majors`, `popular_majors`, `graduation_rate`, `retention_rate`, and `student_faculty_ratio`. Current seed data has one majors array, so both major fields are populated from `top_majors`. |
| `cost` | object | Tuition, net price, aid, and debt fields from `school_costs`. |
| `outcomes` | object | Earnings and repayment from `school_outcomes`; `completion_rate` and `outcome_percentiles` remain `null` until those fields exist. |
| `campus_life` | object | Sports, Greek life, housing, and culture tags from `school_campus_life`; weather and diversity remain `null` until data exists. |
| `data_fields_missing` | string array | Dot-path list of response fields whose values are `null`. |
| `data_confidence_score` | number | Completeness heuristic: non-null data fields divided by total tracked profile data fields, rounded to four decimals. |
| `fit_score`, `category_scores`, `top_reasons`, `top_tradeoffs`, `similar_schools` | placeholders | Present for future ranking and V2 similar-school work. They are not computed in V1.5. |

Missing data behavior:

- Missing numeric values are returned as `null`, never converted to `0`.
- Missing object-like future fields such as `outcome_percentiles` and `diversity_metrics` are returned as `null`.
- `data_fields_missing` makes unknown values explicit for clients.
- `data_confidence_score` measures data completeness only; it is not a ranking score, admissions signal, ROI estimate, or recommendation confidence.

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

School profile reads join `schools` to academics, costs, outcomes, and campus life with left joins in one repository query. The service layer composes the nested profile response, computes missing-field metadata, and leaves ranking and similar-school placeholders empty.

## Planned V1 Endpoints

| Method | Path | Purpose | Stage |
| --- | --- | --- | --- |
| `POST` | `/preferences` | Create or update onboarding preference profile. | V1.8 |
| `POST` | `/rankings` | Rank candidate schools against deterministic preferences. | V1.9 |
| `POST` | `/saved-schools` | Save or update school list status. | V1.11 |
| `GET` | `/saved-schools` | Fetch saved schools. | V1.11 |
| `POST` | `/comparisons` | Create a comparison session. | V1.11 |
| `GET` | `/comparisons/{id}` | Read comparison output. | V1.11 |

## Frontend-Only V1.8 Preference Profile

Until `POST /preferences` exists, the web app stores a local `PreferenceProfile` in browser `localStorage` under `college-exploration.preference-profile.v1`.

The local profile extends the planned backend `Preference` schema:

| Field | Notes |
| --- | --- |
| `intended_major`, `home_state`, `max_annual_cost`, `weights` | Directly map to the existing backend `Preference` schema placeholder. |
| `academic_interests`, `career_priorities`, `preferred_regions`, `preferred_states`, `preferred_settings`, `preferred_school_types`, `campus_preferences`, `admissions_strategy`, `target_acceptance_rate_min`, `aid_importance` | Structured constraints intended for the V1.9 deterministic ranking engine. |
| `completion` | Frontend-only completeness metadata for the onboarding UI. |

Onboarding completion forwards only currently supported search filters to `/search`: state, setting, school type, and max net price. It does not call a ranking endpoint or compute fit scores.

## Contract Rules

- Request and response schemas are Pydantic models.
- Route handlers should call services or repositories rather than writing SQL directly.
- Missing data should be represented explicitly instead of disguised as zero.
- Ranking and generated prose remain separate: ranking fields must come from deterministic code.
