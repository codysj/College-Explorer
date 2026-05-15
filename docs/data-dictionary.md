# Data Dictionary

V1.2 defines the initial PostgreSQL schema and deterministic seed data. The seed data in `data/seed/schools_seed.csv` is synthetic and simplified; it is useful for local development and tests, but it is not an official dataset.

## General Rules

- Missing values are stored as `NULL`, not `0`, unless zero is the real value.
- Rates are stored as decimals from `0` to `1`.
- Dollar amounts are stored as whole-dollar integers.
- School records include `source_name` and `source_year`; V1.2 seed rows use `synthetic_v1_seed` and `2026`.
- Tables with user-owned or mutable data include `created_at`; most also include `updated_at`.

## Tables

### `schools`

Canonical institution identity and search fields.

Key fields: `id`, `unitid`, `name`, `city`, `state`, `region`, `type`, `setting`, `undergraduate_enrollment`, `acceptance_rate`, `latitude`, `longitude`, `source_name`, `source_year`, `created_at`, `updated_at`.

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

### `events`

Basic placeholder analytics/event table.

Key fields: `id`, `user_id`, `event_name`, `entity_type`, `entity_id`, `metadata`, `created_at`.

Indexes: `user_id`, `event_name`, `created_at`.

## Placeholder vs. Real Data

- V1.2 school records are synthetic fixtures with plausible ranges.
- User, preference, saved-school, comparison, and event tables are structural placeholders for future V1 features.
- Public source ingestion, official College Scorecard/IPEDS mapping, and data freshness reporting belong to later tasks.
