# Data Dictionary

V1.2 defines the initial PostgreSQL schema and deterministic seed data. The seed data in `data/seed/schools_seed.csv` is synthetic and simplified; it is useful for local development and tests, but it is not an official dataset.

## General Rules

- Missing values are stored as `NULL`, not `0`, unless zero is the real value.
- Rates are stored as decimals from `0` to `1`.
- Dollar amounts are stored as whole-dollar integers.
- School records include `source_name`, `source_year`, `data_version`, `imported_at`, and `refreshed_at`; legacy V1 seed rows default to `synthetic_v1_seed`, `2026`, and `v1_seed`.
- Tables with user-owned or mutable data include `created_at`; most also include `updated_at`.

## Tables

### `schools`

Canonical institution identity and search fields.

Key fields: `id`, `unitid`, `name`, `city`, `state`, `region`, `type`, `setting`, `undergraduate_enrollment`, `acceptance_rate`, `latitude`, `longitude`, `source_name`, `source_year`, `data_version`, `imported_at`, `refreshed_at`, `created_at`, `updated_at`.

Indexes: `state`, `region`, `type`, `setting`, `undergraduate_enrollment`, `acceptance_rate`.

### `school_academics`

One row per school for academic attributes.

Key fields: `school_id`, `top_majors`, `graduation_rate`, `retention_rate`, `student_faculty_ratio`, `created_at`.

Index: `graduation_rate`.

### `school_costs`

One row per school for tuition and affordability fields.

Key fields: `school_id`, `tuition_in_state`, `tuition_out_state`, `net_price`, `average_aid`, `debt_median`, `created_at`.

Indexes: `tuition_in_state`, `tuition_out_state`, `net_price`.

### `school_outcomes`

One row per school for early outcome metrics.

Key fields: `school_id`, `median_earnings`, `repayment_rate`, `created_at`.

### `school_campus_life`

One row per school for campus-life attributes.

Key fields: `school_id`, `housing_available`, `sports_division`, `greek_life_rate`, `culture_tags`, `created_at`.

### `school_embeddings`

V2.2 pgvector storage for generated school search document embeddings. Rows are metadata-versioned so embedding providers or document construction can change without silently reusing stale vectors.

Key fields: `school_id`, `embedding_type`, `embedding_model`, `vector`, `text_snapshot_hash`, `created_at`, `refreshed_at`.

Primary key: `school_id`, `embedding_type`, `embedding_model`.

Indexes: `embedding_type`/`embedding_model`, cosine `ivfflat` pgvector index on `vector`.

Current embedding type: `school_search_document`.

Current local/test embedding model: `local-hash-embedding-v1`.

The search document text is generated from structured school fields only: name, location, type/setting, majors/program tags, cost/value summaries, outcome summaries, campus/culture tags, and V2.1 source metadata. Generated vectors are not source-of-truth facts and should not be committed as large data files.

### `users`

Basic placeholder user identity table for future saved-school and comparison work.

Key fields: `id`, `email`, `display_name`, `auth_provider`, `created_at`, `updated_at`.

### `user_preferences`

Basic placeholder table for future persisted onboarding preferences. The V1 ranking engine is implemented in the backend service layer and currently consumes request-body preferences or browser-local onboarding state rather than this table.

Key fields: `id`, `user_id`, `intended_major`, `home_state`, `max_annual_cost`, `weights`, `constraints`, `created_at`, `updated_at`.

### `saved_schools`

User-owned saved school list entries.

Key fields: `id`, `user_id`, `school_id`, `status`, `notes`, `created_at`, `updated_at`.

Constraint: one saved-school row per user and school. Status is constrained to `interested`, `applying`, `accepted`, `finalist`, or `removed`.

### `comparisons`

User-owned comparison session metadata.

Key fields: `id`, `user_id`, `name`, `created_at`, `updated_at`.

### `comparison_schools`

Join table that keeps comparison school selections normalized.

Key fields: `comparison_id`, `school_id`, `position`, `created_at`.

Constraint: `position` must be from `1` to `5`.

### `acceptance_offers`

User-owned accepted/finalist decision workspace entries. These capture offer-level inputs and notes without replacing canonical school cost/outcome facts.

Key fields: `id`, `user_id`, `school_id`, `status`, `aid_offer`, `scholarships`, `estimated_yearly_cost`, `visit_notes`, `unresolved_concerns`, `parent_priority_notes`, `student_priority_notes`, `created_at`, `updated_at`.

Constraint: one offer row per user and school. Status is constrained to `accepted` or `finalist`. Financial fields are nonnegative whole-dollar annual amounts when present.

### `decision_summary_snapshots`

Report-ready JSON snapshots produced by `POST /decision/report`. V2.7 snapshots include recommendation cards, finalist ranking rows, category scores, cost/value comparison, sensitivity highlights, unresolved questions, confidence flags, methodology notes, and disclaimer text. Snapshots preserve a deterministic summary at generation time so later export/share workflows can be added without recomputing from changed inputs.

Key fields: `id`, `user_id`, `summary_version`, `school_ids`, `summary`, `created_at`.

### `events`

Privacy-safe analytics/event table for V2.8 product telemetry and ranking evaluation.

Key fields: `id`, `user_id`, `event_name`, `entity_type`, `entity_id`, `metadata`, `created_at`.

Indexes: `user_id`, `event_name`, `created_at`.

Supported V2.8 event names include `search_performed`, `semantic_search_performed`, `school_profile_viewed`, `school_saved`, `school_compared`, `onboarding_completed`, `ranking_generated`, `sensitivity_adjusted`, and `decision_report_generated`.

The `metadata` JSON is sanitized before storage. It may contain structured fields such as enabled filter keys, result counts, rank position, fit score, confidence score, reason codes, normalized category weights, report version, and ranking version. It must not store raw search text, user notes, emails, aid offers, scholarships, estimated yearly costs, loan amounts, or other sensitive free-form student details.

## V2.1 Ingestion Fields

The V2.1 ingestion pipeline writes product-ready school seed CSVs with the same school, academic, cost, outcome, and campus-life columns used by `scripts/seed_database.py`, plus source metadata.

| Field | Meaning |
| --- | --- |
| `source_name` | Human-readable dataset/source label, such as `public_college_snapshot` or a local fixture name. |
| `source_year` | Reporting year for the source snapshot. |
| `data_version` | Deterministic operator-supplied version string for the ingested snapshot. |
| `imported_at` | Timestamp attached when raw data is normalized/imported. |
| `refreshed_at` | Timestamp attached when the refresh command regenerates product-ready output. |

Validation warnings call out unavailable ranking inputs so missing data lowers confidence in downstream scoring instead of silently distorting fit scores.

## V3.0 College Scorecard Snapshot

Real data is fetched by `apps/api/scripts/fetch_scorecard.py`, which writes the raw CSV
that `ingest_college_data.py` already consumes. Normalization, validation, and
missing-value handling stay in the V2.1 pipeline.

### Selection rule

The sample is the union of two slices over the same base population, so it spans both
selective private universities and large public ones — the cost and geography spread the
ranking engine needs to produce meaningful tradeoffs.

Base population (Scorecard filters, reproducible from these alone):

| Filter | Value | Meaning |
| --- | --- | --- |
| `school.carnegie_basic` | `15,16,17` | Doctoral universities (the standard academic definition of "university") |
| `school.ownership` | `1,2` | Public or private nonprofit; for-profit excluded |
| `school.degrees_awarded.predominant` | `3` | Predominantly bachelor's-degree granting |
| `school.operating` | `1` | Currently operating |

Slices, 50 each by default (`--per-slice`):

1. Most selective by latest reported admission rate, bounded to `0.01..0.40` so the slice
   only contains institutions that actually report a rate.
2. Largest by latest reported undergraduate enrollment.

No magazine or commercial ranking is used anywhere in the selection. Slice ordering uses
`latest.*` aliases because the API only permits sorting on those; that choice affects
which schools enter the sample, never the value of any displayed metric.

### Reporting years

Scorecard's `latest.*` fields can describe different years, which the official
documentation warns about. A probe across several institutions confirmed it: cost,
admissions, completion, and enrollment carry data through 2023, while median earnings and
median debt stop at 2020 and return null for later years.

The fetcher therefore pins **one explicit year per metric group for every school**, rather
than reading `latest.*`:

| Metric group | Year | Fields |
| --- | --- | --- |
| Admissions | 2023 | `acceptance_rate` |
| Student body | 2023 | `undergraduate_enrollment`, `retention_rate` |
| Cost | 2023 | `tuition_in_state`, `tuition_out_state`, `net_price` |
| Completion | 2023 | `graduation_rate` |
| Earnings | 2020 | `median_earnings` |
| Debt | 2020 | `debt_median` |
| Repayment | latest | `repayment_rate` (no explicit-year series is published) |

Because the year is uniform per group, a column never mixes vintages across schools, and
the years are dataset-level facts rather than per-row columns. Each fetch writes them to
`<output>.manifest.json` alongside the selection rule. There is deliberately no per-school
fallback to an older year: a school missing 2023 cost stays missing rather than borrowing
2022 and breaking comparability.

### Fields Scorecard does not publish

Left empty, because missing data is never zero:

| Column | Why | Path to filling it |
| --- | --- | --- |
| `student_faculty_ratio` | Not in the Scorecard API | IPEDS |
| `housing_available` | Not in the Scorecard API | IPEDS |
| `sports_division` | Not in the Scorecard API | IPEDS or NCAA |
| `greek_life_rate` | Not published by any official source | Remains unavailable |
| `average_aid` | Scorecard publishes aid *rates*, not an average grant amount. Deriving it from sticker price minus net price would be wrong, not merely approximate: net price already nets living costs and covers aided students only. | IPEDS student financial aid survey |

`top_majors` is derived from `latest.academics.program_percentage.*`, taking the three
largest program shares. `culture_tags` is derived only from reported structural fields
(ownership, locale, enrollment band, research classification) — no invented descriptors.

## Placeholder vs. Real Data

- V1.2 school records were synthetic fixtures with plausible ranges. V3.0 replaces them
  with real College Scorecard data; the synthetic generator is retained only as a test
  fixture so tests never depend on the network.
- V2.1 includes small public-data-style fixtures for pipeline tests, not full official datasets.
- User, preference, saved-school, comparison, and decision tables are structural placeholders until full authenticated account persistence and privacy controls are implemented. Event analytics are implemented for V2.8 local/demo evaluation, but production retention, consent, access control, and deletion workflows belong to V3.
- Full official College Scorecard/IPEDS snapshot operations, similar-school discovery, and data freshness UI belong to later tasks.
