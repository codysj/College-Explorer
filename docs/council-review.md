# Portfolio Review Council: Findings and Remediation Roadmap

Date: 2026-10-13. Six independent reviewers read the repo at `5052615`, each from one
seat: hiring manager, staff backend engineer, frontend/UX engineer, application security,
data scientist, and DevOps/SRE. This file consolidates what they found, de-duplicated
across seats, and tracks the fix for each item. Items flagged by more than one reviewer
are marked with the seats that raised them.

Legend: `[ ]` open, `[x]` done, `[-]` needs the operator (accounts, credentials, or a
judgment call that is not the code's to make).

## R1 - Trust boundary and correctness bugs

- [x] R1.1 Decision workspace IDOR. `user_id` comes from the client (frontend hardcodes 1),
  so `GET /decision/offers?user_id=` exposes every visitor's aid offers and notes once
  public. Fix: reports are computed from offers sent in the request; the server-side offer
  store is not exposed to anonymous clients. *(backend, security)*
- [x] R1.2 Rate limiter keys on the first `X-Forwarded-For` hop, which the client controls,
  and puts the raw header into the Redis key. Fix: right-most hop, hashed. *(backend, security)*
- [x] R1.3 429 responses lose `Retry-After`: the custom error handler drops `exc.headers`;
  the test passed only because it built a bare app. *(backend)*
- [x] R1.4 Optional queries swallow DB errors on a shared session with no rollback, so the
  fallback runs on an aborted transaction; semantic search caches its degraded response.
  *(backend)*
- [x] R1.5 Ranking and semantic routes commit one analytics row per result. Fix: one batch
  insert, one commit. *(backend)*
- [x] R1.6 Unbounded request strings and dicts (`intended_major`, `weights`, `constraints`,
  concern strings, analytics metadata values). *(security)*
- [x] R1.7 `save_snapshot` defaults to true server-side, so any caller persists blobs.
  *(security)*
- [x] R1.8 Cache keys for search and profile carry no version; no schema version anywhere,
  contrary to the stated convention. *(backend)*
- [x] R1.9 A server-side pydantic `ValidationError` is answered as a 422 logged at INFO.
  *(backend)*
- [x] R1.10 Public analytics schema accepts `user_id` (FK violation -> 500). *(backend)*
- [x] R1.11 `ILIKE` input not escaped (`%` matches everything). *(backend, security)*
- [x] R1.12 OpenAPI docs and `/health` environment exposed in production. *(security)*
- [x] R1.13 Search "Retry" button never refetches. *(frontend)*

## R2 - Scoring integrity (ranking v1.4)

- [x] R2.1 Career and campus preference options map to tags the real corpus does not have
  (for example "Research" looks for `research`, data says `very-high-research`; Greek life
  is null for all 92 schools), so unknown is scored as zero. Fix: map to real tags; drop
  the component when the attribute is unknown; test that every UI option can match.
  *(data)*
- [x] R2.2 "Not in the top 3 majors" is scored as "not offered". Fix: treat as unknown.
  *(data)*
- [x] R2.3 A fully missing category scores a neutral 50, below a corpus mean near 75-80, so
  it acts as a demerit. Fix: drop it and renormalize that school's weights. *(data)*
- [x] R2.4 Similar-schools structural score averages over matches only, so one match beats
  three. *(data)*
- [x] R2.5 Cost calculator subtracts grant aid from net price, which already nets grant aid.
  *(data)*
- [x] R2.6 The browser computes its own fit and category scores when the API fails, with
  invented constants (location 50, urban 72). Fix: show an error and retry instead.
  *(frontend)*
- [x] R2.7 Scoring constants and transforms are absent from the methodology doc; loan rate
  default is uncited. *(data)*

## R3 - Product polish (frontend)

- [x] R3.1 Milestone names and developer text shown to students ("arrives in V1.9", "keep
  the API server running", "not part of the V1 frontend foundation", "Saved to API").
  *(hiring, frontend)*
- [x] R3.2 No site-wide navigation; pages invent inconsistent back links. *(frontend)*
- [x] R3.3 Internal `/analytics` dashboard sits in the public nav space and gets indexed.
  *(frontend)*
- [x] R3.4 Format helpers copied in seven files with different `undefined` handling.
  *(frontend)*
- [x] R3.5 Accessibility: no focus ring on inputs, `EmptyState` renders a second `<h1>`,
  unlabeled tray remove buttons. *(frontend)*
- [x] R3.6 Duplicate site name in two page titles; unguarded localStorage write; "Open
  report" enabled with no report. *(frontend)*
- [x] R3.7 The search feature with a measured evaluation has no UI: the search box is a
  name substring match. Fix: free-text search that calls `/semantic-search`. *(frontend)*
- [x] R3.8 Landing page hero card shows an invented school and score. *(hiring)*
- [x] R3.9 Frontend types are hand-written while the project claims generated types.
  *(frontend)*

## R4 - CI, reproducibility, and operations

- [x] R4.1 CI never runs SQL: no Postgres service, so migrations, full-text SQL, filters,
  and the seed are untested; all 100 backend tests use fakes. Fix: Postgres service in
  CI plus a repository integration test module. *(devops, backend)*
- [x] R4.2 The V1.1 silent-skip placeholder is still in the backend job; no pip cache,
  no `permissions`, no `concurrency`, duplicate push+PR runs. *(devops, security)*
- [x] R4.3 Docker images are never built in CI. *(devops)*
- [x] R4.4 `docker compose up` ends with an empty database; the seed script ignores `.env`
  and can hit a different database than Alembic. *(devops)*
- [x] R4.5 Containers run as root; test tools ship in the production image; dev ports bind
  0.0.0.0. *(devops, security)*
- [x] R4.6 Models drift from migrations (missing unique constraint, no `onupdate`), and the
  offer upsert races. *(backend)*
- [x] R4.7 Lambda uses a pooled engine against Neon. *(devops, backend)*
- [x] R4.8 Vestigial directories (`packages/`, `tests/`, `infra/docker/`), committed
  per-machine `.claude/settings.local.json`, two `pytest.ini` files, no `.nvmrc`.
  *(devops, hiring)*
- [x] R4.9 Frontend sends no security headers. *(security)*

## R5 - Presentation and honesty

- [ ] R5.1 README contradicts the code: ranking `v1.0` (code: v1.3), synthetic data (real
  since V3.0), ranking not wired to UI (wired in V3.1), pgvector retrieval (full-text since
  v1.3), FastAPI badge `0.34`. *(hiring, devops, data)*
- [ ] R5.2 README is 21 KB, PowerShell-only, no CI badge, and buries the measured retrieval
  evaluation. Fix: shorter, results up front, bash commands, CI badge. *(hiring, devops)*
- [x] R5.3 Retrieval metric is in-sample and named P@10 while capped by relevant-set size.
  Fix: rename, add bootstrap intervals, add a held-out query set written after v1.3
  froze and report it separately. *(data)*
- [x] R5.4 Screenshots and GIFs show the synthetic, pre-ranking build ("FIT Unknown").
  Fix: re-capture against the real corpus with a production build. *(hiring)*
- [ ] R5.5 `docs/screenshots.md` says no media exists; methodology doc says V1.9.
  *(hiring, data)*
- [ ] R5.6 Three git author identities. Fix: `.mailmap`. *(hiring)*

## Needs the operator

- [-] Public deployment (V3.3): needs Neon, Upstash, AWS, and Vercel accounts and
  credentials. Everything up to `sam deploy` is committed; the runbook is
  `docs/deployment.md`.
- [-] The "7,600 users" history claim: only the author can link evidence for it. The
  README now states it once, outside the pitch.
- [-] Git history is not rewritten; `.mailmap` unifies authors without force-pushing.
- [-] Agent workflow files (`CLAUDE.md`, `AGENTS.md`, `.claude/agents`) are kept on purpose
  and disclosed in the README as an AI-assisted workflow, rather than hidden.

## Found while fixing

- [x] F1 The fetcher requested `program_percentage.biology`; the Scorecard field is
  `biological`. Biology was missing from every school and 42 of 92 had wrong top-three
  majors. Found by a test that every onboarding option must match some school.
- [x] F2 CI's `npm audit --audit-level=high` gate was already failing on `main`: a critical
  Next.js advisory and a high PostCSS one landed after the lockfile was last updated.
- [x] F3 The pydantic `ValidationError` -> 422 mapping was masking that `GET /schools/search`
  built its query model by hand; it now uses FastAPI's query-parameter model.

- [x] F4 The onboarding quiz never sent career priorities, campus preferences, or academic
  interests to the API, and sent only the first region, setting, and type, so those steps
  changed nothing. Found while recapturing the README media against the real stack; the
  journey test now asserts every answer reaches the ranking request.

## Deliberately not done

- `useSyncExternalStore` rewrite of the saved/compare store, server-rendering the profile
  page, and splitting 500-700 line client components: real improvements, no user-visible
  bug today. Listed in `tasks.md` Planned Next Steps.
- A labeled similar-schools evaluation: R2.4 fixes the inverted score; quality claims stay
  out of the README until it exists.
