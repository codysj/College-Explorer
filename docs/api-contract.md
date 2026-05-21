# API Contract

V2.3 implements process health, DB readiness, structured school search, full school profiles, deterministic rankings, pgvector-backed semantic search with deterministic fallback, similar-school discovery, Redis cache-aside for read-heavy API responses, CORS configuration for the browser frontend, a frontend-only local preference profile, and browser-local saved-school/comparison workflows. Backend preference persistence, saved schools, comparisons, and acceptance decision mode are not implemented yet.

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

Structured school search for search-result cards. This endpoint does not return full profiles. Ranking fields are present in the response shape but are only populated by `POST /rankings`.

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
      "category_scores": {},
      "top_reasons": [],
      "top_tradeoffs": [],
      "ranking_version": null
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_results": 3,
  "has_next": false
}
```

No-result responses use an empty `results` array with pagination metadata.

### `POST /rankings`

Ranks candidate schools against a deterministic preference profile. The endpoint fetches all data needed for V1 ranking in one joined repository query, applies optional hard constraints, computes scores in memory, sorts by `fit_score` descending, then `confidence_score` descending, then `school_id` ascending, and paginates the ranked result.

Request body:

```json
{
  "preferences": {
    "intended_major": "Computer Science",
    "home_state": "CA",
    "max_annual_cost": 30000,
    "weights": {
      "academic": 0.2,
      "cost": 0.2,
      "career": 0.18,
      "location": 0.14,
      "campus": 0.14,
      "admissions_realism": 0.14
    },
    "constraints": {
      "preferred_regions": ["West"],
      "preferred_settings": ["Urban"],
      "career_priorities": ["High earnings", "Internships"],
      "campus_preferences": ["Residential"],
      "admissions_strategy": "balanced",
      "target_acceptance_rate_min": 30,
      "strict_cost": true
    }
  },
  "filters": {
    "state": "CA",
    "page": 1,
    "page_size": 10
  }
}
```

`filters` uses the same fields and validation rules as `GET /schools/search`.

Response `200`:

```json
{
  "ranking_version": "v1.0",
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
      "fit_score": 87.45,
      "confidence_score": 0.94,
      "category_scores": {
        "academic": 83.5,
        "cost": 92.4,
        "career": 86.2,
        "location": 100.0,
        "campus": 91.0,
        "admissions_realism": 72.5
      },
      "top_reasons": [
        "location_preferred_state",
        "cost_within_budget",
        "campus_preferred_setting"
      ],
      "top_tradeoffs": [
        "admissions_below_acceptance_comfort"
      ],
      "ranking_version": "v1.0"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_results": 1,
  "has_next": false
}
```

Ranking response fields:

| Field | Type | Notes |
| --- | --- | --- |
| `fit_score` | number | Weighted `0` to `100` deterministic fit score. |
| `confidence_score` | number | Weighted `0` to `1` score-coverage confidence. This is separate from fit. |
| `category_scores` | object | Category scores keyed by `academic`, `cost`, `career`, `location`, `campus`, and `admissions_realism`. |
| `top_reasons` | string array | Deterministic reason codes for the strongest positive weighted signals. |
| `top_tradeoffs` | string array | Deterministic reason codes for the largest penalties or lowest-confidence signals. |
| `ranking_version` | string | Current ranking formula version, initially `v1.0`. |

Hard constraints:

- `strict_major`, `major_strict`, or `require_major` filters out schools whose known majors do not include the intended major or academic interests.
- `strict_cost`, `cost_strict`, or `require_cost` filters out schools whose known net price is above `max_annual_cost`.
- `strict_state`, `strict_region`, `strict_setting`, and `strict_school_type` make the matching preference fields required.
- `strict_constraints` may also list strict dimensions, such as `["major", "cost"]`.
- Unknown data is not treated as zero and does not count as a violation by itself.

### `POST /semantic-search`

Natural-language school search using hybrid retrieval. The endpoint retrieves vector candidates when embeddings exist, falls back to deterministic lexical matching when they do not, applies structured filters and hard constraints, then re-ranks candidates with the deterministic ranking engine. Vector similarity never overrides hard constraints or final structured ranking.

Request body:

```json
{
  "query": "affordable data science schools near cities",
  "filters": {
    "setting": "Urban",
    "max_net_price": 30000,
    "page": 1,
    "page_size": 10
  },
  "preferences": {
    "intended_major": "Data Science",
    "max_annual_cost": 30000,
    "weights": {
      "academic": 0.35,
      "cost": 0.25,
      "career": 0.25,
      "campus": 0.15
    },
    "constraints": {
      "strict_cost": true
    }
  },
  "candidate_limit": 50
}
```

Request fields:

| Field | Type | Rules |
| --- | --- | --- |
| `query` | string | Required natural-language query, 3 to 240 chars. |
| `filters` | object | Optional `SearchRequest` fields from `GET /schools/search`; page/page_size control the final ranked response page. |
| `preferences` | object | Optional deterministic ranking preferences; hard constraints are honored after retrieval. |
| `candidate_limit` | integer | Optional vector/fallback candidate count, `1` to `200`, defaults to `50`. |

Response `200`:

```json
{
  "ranking_version": "v1.0",
  "embedding_model": "local-hash-embedding-v1",
  "embedding_type": "school_search_document",
  "retrieval_mode": "deterministic_fallback",
  "results": [
    {
      "school_id": 2,
      "name": "Bayview Technical University",
      "city": "New Haven",
      "state": "CT",
      "type": "Public",
      "setting": "Urban",
      "enrollment": 11800,
      "acceptance_rate": 0.52,
      "net_price": 24400,
      "graduation_rate": 0.78,
      "fit_score": 86.42,
      "confidence_score": 0.95,
      "category_scores": {
        "academic": 92.0,
        "cost": 82.5
      },
      "top_reasons": ["academic_major_match", "cost_within_budget"],
      "top_tradeoffs": [],
      "ranking_version": "v1.0",
      "semantic_score": 0.71,
      "match_reasons": ["major_match", "setting_match", "cost_value_match"]
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_results": 1,
  "has_next": false
}
```

`retrieval_mode` is `pgvector` when stored vectors are used and `deterministic_fallback` when embeddings are missing or unavailable. `match_reasons` may include `major_match`, `location_match`, `setting_match`, `cost_value_match`, `outcomes_match`, and `campus_culture_match`.

### `GET /schools/{id}/similar`

Returns explainable similar-school alternatives for a source school. The endpoint retrieves semantic candidates when embeddings exist, falls back to deterministic lexical similarity when they do not, excludes the source school, applies structured constraints, and returns variant-aware scores and reasons.

Query parameters:

| Name | Type | Rules |
| --- | --- | --- |
| `variant` | enum | `general`, `cheaper`, `less_selective`, `smaller`, `stronger_outcomes`, or `closer_to_home`. Defaults to `general`. |
| `state`, `region`, `type`, `setting` | string | Optional structured constraints. |
| `home_state` | string | Optional 2-letter state used by `closer_to_home`. |
| `min_net_price`, `max_net_price`, `min_enrollment`, `max_enrollment` | integer | Optional nonnegative constraints. |
| `min_acceptance_rate`, `max_acceptance_rate`, `min_graduation_rate` | number | Optional `0` to `1` constraints. |
| `page` | integer | Defaults to `1`; must be `>= 1`. |
| `page_size` | integer | Defaults to `6`; must be `1` to `12`. |
| `candidate_limit` | integer | Defaults to `50`; must be `1` to `200`. |

Variant behavior:

- `cheaper`: requires lower net price when both source and candidate net price are known.
- `less_selective`: requires higher acceptance rate when both rates are known.
- `smaller`: requires lower enrollment when both values are known.
- `stronger_outcomes`: requires higher graduation rate or higher median earnings when comparable data is known.
- `closer_to_home`: requires `state == home_state` when `home_state` is supplied.

Response `200`:

```json
{
  "source_school_id": 1,
  "variant": "cheaper",
  "variant_applied": "cheaper",
  "ranking_version": "v1.0",
  "embedding_model": "local-hash-embedding-v1",
  "embedding_type": "school_search_document",
  "retrieval_mode": "deterministic_fallback",
  "results": [
    {
      "school_id": 2,
      "name": "Bayview Technical University",
      "city": "New Haven",
      "state": "CT",
      "type": "Public",
      "setting": "Urban",
      "enrollment": 11800,
      "acceptance_rate": 0.52,
      "net_price": 24400,
      "graduation_rate": 0.78,
      "median_earnings": 68000,
      "similarity_score": 0.82,
      "fit_score": 86.4,
      "top_reasons": ["overlapping_majors", "variant_lower_net_price", "academic_major_match"],
      "top_tradeoffs": [],
      "variant_applied": "cheaper",
      "ranking_version": "v1.0"
    }
  ],
  "page": 1,
  "page_size": 6,
  "total_results": 1,
  "has_next": false
}
```

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
  "acceptance_rate": 0.64,
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
  "data_confidence_score": 0.8621,
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
| `school_id`, `name`, `city`, `state`, `region`, `type`, `setting`, `enrollment`, `acceptance_rate` | scalar | Core identity and search fields from `schools`. |
| `academics` | object | `majors`, `popular_majors`, `graduation_rate`, `retention_rate`, and `student_faculty_ratio`. Current seed data has one majors array, so both major fields are populated from `top_majors`. |
| `cost` | object | Tuition, net price, aid, and debt fields from `school_costs`. |
| `outcomes` | object | Earnings and repayment from `school_outcomes`; `completion_rate` and `outcome_percentiles` remain `null` until those fields exist. |
| `campus_life` | object | Sports, Greek life, housing, and culture tags from `school_campus_life`; weather and diversity remain `null` until data exists. |
| `data_fields_missing` | string array | Dot-path list of response fields whose values are `null`. |
| `data_confidence_score` | number | Completeness heuristic: non-null data fields divided by total tracked profile data fields, rounded to four decimals. |
| `fit_score`, `category_scores`, `top_reasons`, `top_tradeoffs`, `similar_schools` | placeholders | Profile ranking and V2 similar-school work are not computed by this endpoint. Use `POST /rankings` for ranked search-card output. |

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

## Browser Access

The API enables CORS for origins listed in `CORS_ORIGINS`. Local defaults allow `http://localhost:3000` and `http://127.0.0.1:3000` so the Next.js frontend can call FastAPI during development. Production deployments should set this to the exact hosted frontend origin.

## Query Strategy

Structured search joins `schools` to `school_costs` and `school_academics` with left joins, composes filters through SQLAlchemy expressions, counts the filtered result set, applies deterministic sorting, and then applies offset/limit pagination. Route handlers do not write SQL directly.

School profile reads join `schools` to academics, costs, outcomes, and campus life with left joins in one repository query. The service layer composes the nested profile response, computes missing-field metadata, and leaves ranking and similar-school placeholders empty.

Ranking reads join `schools`, `school_academics`, `school_costs`, `school_outcomes`, and `school_campus_life` with left joins in one repository query. The ranking service applies hard constraints, computes category scores, confidence, reason codes, and tradeoffs in memory for V1 scale.

Semantic search uses `school_embeddings` for pgvector retrieval when embeddings are present. The semantic service applies filters and hard constraints after candidate retrieval and delegates final ordering to the ranking service.

Similar-school discovery uses the same generated embedding documents. It compares candidates to a source school, excludes the source school, applies variant constraints, deduplicates name/city/state matches, and returns a deterministic similarity score plus ranking reasons.

## Cache Behavior

Caching is transparent to clients and does not change request or response contracts. The backend checks Redis before repository/database work, stores successful responses on misses, and falls back to normal execution if Redis is unavailable.

| Resource | Key inputs | TTL |
| --- | --- | --- |
| Search | Resource name, all filters, sort, direction, page, page size, `CACHE_KEY_VERSION` | 300 seconds |
| School profile | Resource name, `school_id`, `CACHE_KEY_VERSION` | 3600 seconds |
| Ranking | Resource name, full request body, `RANKING_VERSION`, `CACHE_KEY_VERSION` | 300 seconds |
| Semantic search | Resource name, normalized query, filters, preferences, embedding type/model, `RANKING_VERSION`, `CACHE_KEY_VERSION` | 300 seconds |
| Similar schools | Resource name, school id, variant request, embedding type/model, `RANKING_VERSION`, `CACHE_KEY_VERSION` | 300 seconds |

Example key shapes:

```text
college-exploration:cache:v1:search:{sha256-digest}
college-exploration:cache:v1:school-profile:{sha256-digest}
college-exploration:cache:v1:ranking:{sha256-digest}
```

Ranking keys include `RANKING_VERSION` so cached rankings cannot cross deterministic formula versions.

## Planned V1 Endpoints

| Method | Path | Purpose | Stage |
| --- | --- | --- | --- |
| `POST` | `/preferences` | Create or update onboarding preference profile. | V1.8 |
| `POST` | `/rankings` | Rank candidate schools against deterministic preferences. | Implemented in V1.9 |
| `POST` | `/saved-schools` | Save or update school list status. | Planned after auth |
| `GET` | `/saved-schools` | Fetch saved schools. | Planned after auth |
| `POST` | `/comparisons` | Create a comparison session. | Planned after auth |
| `GET` | `/comparisons/{id}` | Read comparison output. | Planned after auth |

The V1.11 frontend does not call these planned saved-school or comparison endpoints because there is no authenticated user/session boundary. It persists state locally in browser `localStorage` instead:

| Key | Purpose |
| --- | --- |
| `college-exploration.saved-schools.v1` | Saved school snapshots with status `interested`, `applying`, `accepted`, `finalist`, or `removed`. |
| `college-exploration.compare-schools.v1` | Deduplicated compare school snapshots capped at 5 schools. |

Future V2/V3 persistence should map these local records to user-owned backend records after authentication and privacy documentation are in place.

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
