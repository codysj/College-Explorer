# Data Dictionary

No schema or seed data exists yet. This file will become the source of truth for fields, sources, and missing-data behavior during V1.2.

## Planned Data Areas

- `schools`: canonical institution identity and location.
- `school_academics`: programs, graduation, retention, and academic metrics.
- `school_costs`: tuition, net price, aid, and debt fields.
- `school_outcomes`: completion, earnings, and repayment metrics.
- `school_campus_life`: housing, setting, size, culture tags, and derived lifestyle fields.
- `user_preferences`: onboarding answers and ranking weights.
- `saved_schools`: user school lists and statuses.
- `comparisons`: selected schools and comparison snapshots.

## Source Rules

- Public institutional datasets should be the source of truth.
- Every imported field should track source name and source year where practical.
- Derived fields must be labeled as derived.
- Missing values should remain unknown unless zero is semantically correct.
