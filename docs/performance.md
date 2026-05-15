# Performance Notes

This document records only evidence that has been implemented or measured. It intentionally avoids production claims until a hosted environment and load-test workflow exist.

## Verified Engineering Work

| Area | Implemented evidence | Claim level |
| --- | --- | --- |
| Search indexing | Alembic schema defines indexes for common search filters and sorts: state, region, type, setting, enrollment, acceptance rate, graduation rate, tuition, and net price. | Implemented, not benchmarked. |
| Query structure | Search, profile, and ranking reads go through repositories and SQLAlchemy expressions instead of route-level SQL. | Implemented. |
| Cache-aside | Redis cache service wraps search, profile, and ranking reads with versioned keys and TTLs. | Implemented. |
| Cache hit behavior | Tests verify repeated search/profile/ranking calls avoid duplicate repository work. | Unit-tested behavior, not production DB reduction. |
| Cache fallback | Redis connection/read/write failures fall back to database reads. | Implemented and documented. |
| Ranking determinism | Ranking tests cover stable scoring, missing data behavior, hard constraints, and sort order. | Implemented. |

## Current Cache TTLs

| Resource | TTL |
| --- | --- |
| Search | 300 seconds |
| School profile | 3600 seconds |
| Ranking | 300 seconds |

Cache keys include `CACHE_KEY_VERSION`. Ranking keys also include `RANKING_VERSION`.

## Metrics Not Yet Measured

- Production p50/p95/p99 latency.
- Real cache hit rate.
- Database CPU, query latency, or connection pool saturation.
- Before/after index latency improvement.
- Before/after Redis database-load reduction.
- Uptime, error budget, real users, or traffic volume.

## Recommended Measurement Plan

V3 should add:

- A repeatable seed/load-test dataset.
- Endpoint load tests for `/schools/search`, `/schools/{id}`, and `/rankings`.
- `EXPLAIN ANALYZE` snapshots for representative search and ranking candidate queries.
- Cache hit/miss counters by endpoint.
- Documented p50/p95/p99 latency results from local and production-like environments.
