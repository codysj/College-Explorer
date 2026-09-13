# Consolidated Roadmap — V3

Written 2026-09-12. Reconciles external feedback with the actual repo state.
Supersedes the V3.1–V3.7 stub list in `tasks.md` and `docs/SPEC.md` section 10.

---

## 1. What the audit actually found

Three findings reorder the feedback you received. They are not in that feedback because
they are only visible from inside the code.

| Finding | Evidence | Consequence |
| --- | --- | --- |
| **The ranking engine is not connected to the UI.** | `POST /rankings` exists and is tested (`apps/api/services/ranking_service.py`, 29 functions). No file under `apps/web/` references it. `/search` sends structured filters only; `/onboarding` stores a local profile and forwards a filter subset. | The headline product claim — "preferences → ranked results" — does not exist in the running app. The backend half is already built and paid for. |
| **All 50 schools are synthetic.** | `data/seed/schools_seed.csv`, 51 rows, unitids `900001+`, names like "Adams State College" in "Northbridge, MA". | Every screenshot, GIF, retrieval evaluation, and load test currently measures fiction. |
| **Semantic search is a hash, not a semantic model.** | `LocalHashEmbeddingProvider` SHA-256s each token into one of 64 buckets (`apps/api/services/semantic_search.py:46-60`). | It is exact lexical matching with collisions — strictly worse than Postgres full-text, which is already installed. It is also unreferenced by the frontend. |

Also relevant: `tests/e2e/` is empty, `/analytics` is an unauthenticated dashboard with an
unauthenticated write endpoint, and `docs/performance.md` correctly disclaims every number.

**Read of the feedback:** directionally right on all six points, but it assumes the V1/V2
journey works end to end and only needs measurement. It does not. Two of the six items
(the journey, retrieval) are *cheaper* than the feedback implies because the backend
already exists. Two (cohort study, collaboration workspaces) are considerably more
expensive than they look and belong at the end.

---

## 2. Sequencing principle

Order by **what makes the next task honest**, not by feature interest.

```
Real data ──┬─> Ranked journey ──> E2E guard ──> Public deploy ──> reshot demo
            ├─> Retrieval eval  (meaningless on synthetic text)
            ├─> Load test       (meaningless on 50 fake rows)
            └─> Provenance      (synthetic data has no reporting year)
```

Everything downstream of real data is measurement, and measurement on synthetic data is
theater. Phase 0 is not optional and not parallelizable.

---

## Phase 0 — Credibility. Nothing else counts until this ships.

### V3.0 — Populate with real data for the top ~100 US universities

*Maps to: the data/provenance dependency. Effort: 2–3 days.*

Replace the synthetic seed with real, attributable data.

- Fetch from the **College Scorecard API** (`api.data.gov`, free key) keyed by real
  `unitid`. Supplement from **IPEDS** only for fields Scorecard lacks — student-faculty
  ratio, housing, athletics division, Greek life.
- Scope ~100 institutions. Pick a defensible, documented selection rule: a union of
  high-enrollment publics and nationally-known privates gives the geographic and cost
  spread the ranking engine needs to produce interesting tradeoffs. Do not use a magazine
  ranking as the rule; state whatever rule you used in the data dictionary.
- **Capture a reporting year per metric group, not per row.** Scorecard's `latest.*`
  fields mix vintages — cost, completion, and earnings are each as-of different years.
  The schema has row-level `source_name` / `source_year` / `data_version`; add
  `cost_year`, `outcomes_year`, `admissions_year`, `earnings_year`. Field-level provenance
  on all ~25 metrics is over-built; per-group covers the real risk.
- Surface the year anywhere a number is compared — profile, compare table, decision
  report. "Median earnings $52,000 (2021 entering cohort)" is the honest form.
- Keep the synthetic generator as a test fixture. Tests must not depend on the network.

**Done when:** a real school profile renders numbers you can spot-check against
collegescorecard.ed.gov, every displayed metric carries a year, and `refresh_embeddings`
has been re-run over the real corpus.

**Watch for:** missing data rises sharply with real data — small privates suppress
earnings, publics report in-state cost only. This is the first real test of the "missing
is never zero" rule. Expect the completeness/confidence scoring to need retuning, and
expect some schools to be unrankable in some categories. That is correct behavior; make
sure the UI says so instead of silently scoring them low.

### V3.1 — Connect preferences to ranked results

*Maps to: "finish preferences → ranked results → shortlist → decision report". Effort: 1–2 days.*

The smallest diff with the largest payoff in the project.

- Give `/search` a ranked mode: when a `PreferenceProfile` exists in local state, call
  `POST /rankings` with it instead of the filter-only structured search.
- Render what the engine already returns and the UI currently discards — fit score, reason
  codes, tradeoffs, per-category contributions, confidence.
- Onboarding's final step routes into ranked results, not filtered search.
- Keep the ranked/browse distinction visible and reversible. A visitor with no profile
  must still get useful results.
- Route the shortlist forward: `/dashboard` → `/compare` → `/decision` →
  `/decision/report` should be one continuous path. Audit each handoff for a next action.

**Done when:** a first-time visitor goes onboarding → ranked list with explanations → save
three → compare → decision report without typing a URL or landing on a page that doesn't
tell them what to do next.

### V3.2 — One end-to-end test for the whole journey

*Maps to: old V3.6. Effort: half a day.*

`tests/e2e/` is empty; `apps/web/tests/` holds five per-page smoke specs and nothing that
crosses pages. Add one Playwright test walking the full journey above, running in CI —
that test is what licenses the claim that the journey works. Add a ranking snapshot test
over the real corpus so future data refreshes cannot silently reorder results.

---

## Phase 1 — Make it real and public.

### V3.3 — Public deployment

*Not in the feedback. Effort: 1–2 days.*

The README says no public deployment has been verified. For work meant to demonstrate
polish, a live URL is the highest-multiplier item on this list: it converts every other
claim from "documented" to "verifiable."

- Web → Vercel. API → AWS Lambda: the existing API image with the Lambda Web Adapter, a
  public function URL, and a SAM template in `infra/aws`. Postgres → Neon (free, pgvector).
  Redis → Upstash (free, optional). About $0 a month at demo traffic.
- Why Lambda (decided 2026-09-12): the original product ran on AWS, and Lambda's always-free
  allowance keeps that claim true without paying for an always-on server. Railway and Render
  were more convenient but did not fit $0: Railway has no ongoing free tier, and Render's free
  Postgres expires after 30 days.
- Seed the production database from the real ingestion output.
- Health checks, a cost alert, and a cold-start figure measured after the first deploy.
- Deferred: a build stamp on `/health`. It needs a deploy pipeline to supply the commit, and
  deploys are manual until then.

**Done when:** a stranger with the URL completes the journey on a phone.

### V3.4 — Shareable read-only report links

*Lazy version of "student/parent/counselor collaboration". Effort: 1 day.*

V2.7 already persists report snapshots. Add an unguessable share token and a public
read-only route. A student sends a parent a link; the parent sees the report.

That covers the actual collaboration use case at a fraction of the cost of authenticated
workspaces with granular sharing, revocable invitations, comments, and versioned reports.
Build the full version only if the usefulness study (V3.11) shows people want to co-edit —
a much stronger basis than assuming they do.

### V3.5 — Lock the exposed surfaces before going public

*Maps to: old V3.5, narrowed. Effort: half a day.*

Only what a public URL makes genuinely urgent:

- `/analytics` dashboard and `POST /analytics/events` are unauthenticated. Gate the
  dashboard behind a shared secret or environment flag; rate-limit the write endpoint.
- Rate-limit `/rankings`, `/semantic-search`, and `/sensitivity` — all compute-heavy, all
  accepting unauthenticated POST bodies.
- Dependency audit in CI, security headers, and a check that no secrets ship in the image.

Defer the formal threat model until there are accounts to threaten.

---

## Phase 2 — The engineering substance.

### V3.6 — Beat the hash baseline, honestly

*Maps to: "make semantic retrieval better than the hash baseline". Effort: 2–3 days.*

The feedback is right, and the framing matters: the goal is a defensible comparison, not a
better number.

- Build ~30 labeled queries against the real corpus ("affordable engineering school in the
  Midwest", "small liberal arts college with strong outcomes") and hand-label the relevant
  schools. Thirty separates these methods; a thousand is a research project.
- Compare four arms: the current hash, **Postgres full-text** (already installed — the
  honest lexical baseline), sentence embeddings (`all-MiniLM-L6-v2` locally, or an
  embedding API), and hybrid lexical + vector feeding the existing deterministic re-rank.
- **Apply hard constraints during retrieval, not after.** Today `candidate_limit`
  retrieves by similarity and constraints filter the survivors, so a tight budget filter
  can empty the result set. Push constraints into the pgvector query's `WHERE`, or
  over-retrieve in proportion to filter selectivity. This is the actual retrieval
  engineering in this task.
- Measure precision@10, empty-result rate, constraint adherence, and p95 latency per arm.
  Publish the table including the arms that lost.
- **Keep the simplest arm that wins.** If full-text matches embeddings on your queries,
  ship full-text and write down that you tested embeddings and they did not pay for
  themselves. That write-up is a stronger signal than a vector database.

### V3.7 — Measure performance under load and failure

*Maps to: "measure performance under realistic load and failure". Effort: 1–2 days.*

`docs/performance.md` already enumerates exactly what has not been measured. Fill it in.

- One repeatable workload (k6 or Locust) over `/schools/search`, `/schools/{id}`,
  `/rankings`, and `/semantic-search`, committed with its invocation.
- Three scenarios: cold cache, warm cache, Redis unavailable. The fallback path exists —
  prove it degrades rather than fails.
- `EXPLAIN (ANALYZE, BUFFERS)` on the three heaviest queries, output committed.
- Fix the one bottleneck the measurement finds and document the tradeoff taken. One real
  optimization with before/after numbers beats five speculative ones.
- Then rewrite the README performance section with measured numbers and drop those
  disclaimers. Keep disclaimers for whatever is still unmeasured.

### V3.8 — Trustworthy data refresh

*Maps to: "turn ingestion into a trustworthy data-refresh system". Effort: 2 days.*

V3.0 gets real data in once. This makes re-running it safe.

- A `--from-api` mode so a refresh does not depend on a hand-placed CSV.
- Schema-change detection: fail loudly when Scorecard adds, renames, or drops a field
  instead of silently writing nulls.
- A validation report per run — row counts, per-field null rates, and a **diff against the
  previous snapshot with anomaly thresholds**. A school's net price moving 40% is either
  news or a bug, and you need to know which before publishing.
- Cache invalidation keyed on `data_version`. Keys already carry `CACHE_KEY_VERSION` and
  `RANKING_VERSION`; adding the data version stops a refresh from serving stale
  mixed-vintage comparisons.
- Stale-embedding detection via the existing `text_snapshot_hash`.
- A GitHub Actions cron that runs refresh + validation and **opens a PR** rather than
  writing to production. Review stays human; the drudgery does not.

Skip the admin console UI (old V3.4) — a validation report in CI does the same job with no
frontend to maintain.

---

## Phase 3 — Optional depth. Only after Phase 2 ships.

### V3.9 — Accounts and cross-device persistence

*Effort: 3–4 days.* Auth.js or Clerk, user-scoped shortlists/preferences/reports,
authorization tests on every owned resource, data export and deletion. Worth doing only if
V3.4's share links prove insufficient. It is the largest item here and the least visible
to someone evaluating the project in five minutes.

### V3.10 — Learn preferences from comparisons

*Effort: 2–3 days.* The most interesting item in the feedback and the most easily wasted.
Keep it small: 5–7 forced-choice pairs ("$28k two hours from home, or $19k eight hours?"),
update the existing weight vector from the answers, and choose each next question by which
one most changes the current top 10. Non-negotiable: the student sees what changed and
why, and can override it. An opaque model that silently reweights someone's priorities is
worse than the sliders already shipped.

### V3.11 — Usefulness study, scaled to reality

*Effort: about a week elapsed, roughly a day of work.* The feedback asks for a recruited
cohort with observed sessions. Scale it to what actually gets finished: 5–8 real students
or counselors, a written task script, the V2.8 funnel analytics already built, and a short
honest write-up of where people got stuck and what changed as a result. Report n. Eight
observed sessions with specific quotes and two fixes that came out of them is a genuine
signal; a "cohort study" with n=3 and no findings is worse than saying nothing.

### V3.12 — Portfolio polish

*Effort: 1 day.* Reshoot every GIF in `docs/media/` — they show fake schools, which is the
one flaw a reviewer notices in ten seconds. Add a 90-second demo script, a schema diagram,
and a "known limitations" section naming the missing-data reality and the retrieval arms
that lost. Honest limitations read as senior; their absence reads as inexperience.

---

## 3. Deliberately deprioritized

| Dropped or cut down | Why |
| --- | --- |
| Recruited cohort study as specified | n will realistically be 5–8, not a cohort. Scoped down to V3.11 rather than overclaimed. |
| Comments, versioned reports, revocable invitations | Speculative. V3.4 share links cover the real use case; build the rest when someone asks for it. |
| Field-level provenance on every metric | Per-metric-group reporting years cover the actual Scorecard vintage problem. |
| Admin data-quality console (old V3.4) | A CI validation report does the same work with no UI to maintain. |
| Alerting, error budgets, observability dashboard (old V3.2) | Structured logging plus V3.7's measured numbers is the right depth for a project with no on-call rotation. |
| Formal threat model document | Revisit alongside V3.9, when there is user data to model threats against. |

---

## 4. Critical path

**V3.0 → V3.1 → V3.2 → V3.3** is the spine: real data, a working journey, a test that
guards it, a public URL. One to two focused weeks, and it is the difference between a
project that describes itself and one that demonstrates itself.

V3.6 and V3.7 are the two items that make the work read as senior engineering rather than
feature assembly — they are where the reasoning shows. Do them next, and publish the
negative results.

Everything in Phase 3 is genuinely optional.
