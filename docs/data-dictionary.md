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

Report-ready JSON snapshots produced by `POST /decision/report`. Snapshots preserve a deterministic summary at generation time so later export/share workflows can be added without recomputing from changed inputs.

Key fields: `id`, `user_id`, `summary_version`, `school_ids`, `summary`, `created_at`.

### `events`

Basic placeholder analytics/event table.

Key fields: `id`, `user_id`, `event_name`, `entity_type`, `entity_id`, `metadata`, `created_at`.

Indexes: `user_id`, `event_name`, `created_at`.

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

## Placeholder vs. Real Data

- V1.2 school records are synthetic fixtures with plausible ranges.
- V2.1 includes small public-data-style fixtures for pipeline tests, not full official datasets.
- User, preference, saved-school, comparison, decision, and event tables are structural placeholders until full authenticated account persistence and privacy controls are implemented.
- Full official College Scorecard/IPEDS snapshot operations, similar-school discovery, and data freshness UI belong to later tasks.
