# Scoring Methodology

V1.9 implements a deterministic ranking engine in the FastAPI backend. Scores, rank order, reason codes, tradeoffs, confidence, and `ranking_version` come from structured data and rule-based code only. No LLM or model-generated text is used.

## Version

The current ranking version is `v1.2`. Any future change that materially changes score formulas, weights, hard-constraint behavior, confidence, or reason-code selection should update this version and this document in the same change.

Ranking cache keys include this version. A future ranking formula change must bump the version so cached responses from older deterministic scoring logic cannot be reused.

### v1.1 (2026-09-12)

Explanation-only change; scores, weights, and ordering are identical to `v1.0`.

`build_explanations()` surfaces a category as a tradeoff when its confidence is below
0.5 **or** its score is below 68. Because each category's `tradeoff_code` is fixed before
scoring, a thinly-evidenced category asserted a preference mismatch it could not support.
Real College Scorecard data made this routine:

- Campus emitted `campus_preference_not_matched` on 65 of 92 schools even when the student
  stated no campus preference, because Scorecard publishes no housing, athletics, or
  Greek-life figures and the category falls back to derived tags alone.
- Worse, location emitted `location_preference_not_matched` for schools that *matched*. A
  home state with no explicit `preferred_states` carries 0.35 confidence, so a California
  school could score 90, earn the `location_home_state` reason, and be told it missed the
  preference in the same response.

Below the confidence floor the score is not meaningful either, so `tradeoff_code_for()`
now returns `<category>_data_limited` for any category under 0.5 confidence, and the
category's own tradeoff code only when there is enough data to support the claim. Missing
data is never reported as a demerit.

The version bump is required because cache keys embed it: without it, cached rankings
would keep serving the old, misleading codes.

### Data inputs after the IPEDS supplement (2026-09-12)

A data change, not a scoring change: `RANKING_VERSION` stays `v1.1` because no rule moved.
The ranking snapshot was re-reviewed against the new data instead.

- `student_faculty_ratio` now feeds the academic category for every school (weight 0.10)
  and `average_aid` feeds the cost category (0.15, or 0.25 when aid importance is high).
  For the budget-led snapshot profile, distinct cost scores across the 92 schools rose
  from 38 to 57.
- The campus category reads housing and athletics only when a student states campus
  preferences. For those students it now discriminates: with "athletics" and "residential"
  stated, 82 schools score 100 and 10 score 65. Before the supplement, that same profile
  scored every school 0, because neither field existed - missing data acting as a zero.
  Without stated campus preferences, campus is still a constant fallback and reports
  `campus_data_limited`.
- Housing does not discriminate on this corpus: all 92 doctoral universities report
  on-campus housing.
- Known gap: Penn State has no 2021 EADA record, so it scores as not matching an athletics
  preference, the same as a Division III school, although it competes in Division I.
  Treating unknown athletics as neutral rather than a non-match would be a scoring change
  that needs a version bump; it is recorded as a follow-up rather than made silently.

### v1.2 (2026-09-12): semantic search ordering

The deterministic engine is unchanged: category formulas, weights, hard constraints,
confidence, and reason codes are identical, and the ranking snapshot still passes. The
version moves because `POST /semantic-search` orders its page differently, and its cache
keys must not serve v1.1 responses.

Measured offline against 35 labeled queries (`data/evaluation/`) at the production default
candidate limit of 50:

| Pipeline | End-to-end P@10 | Filtered queries returning nothing | Mean fit of page |
| --- | ---: | ---: | ---: |
| v1.1: v2.2 documents, filter after retrieval, fit order | 0.35 | 0 of 6 (5 of 6 at limit 10) | 81.5 |
| v1.2: v3.0 documents, filter first, relevance order | 0.77 | 0 of 6 at every limit | 78.1 |

Both rows use the production hash retriever. Three changes produce the difference:

- Filters apply inside the candidate query, before the nearest-neighbour limit.
- The page is ordered by query relevance, with the fit order breaking ties. Before, fit
  alone ordered the page and the similarity score was display-only.
- Search documents (v3.0) drop the labels and source line that every school shared,
  spell out state names and athletics divisions, and omit raw numbers.

This stays within the rule against replacing deterministic ranking: similarity is
computed rather than generated, and `rank_rows()` still removes constraint violations and
computes every fit score before anything is reordered. Page fit falls 3.4 points on
average, the measured cost of respecting the query. Precision for synonym and
numeric-only queries is inflated by state-name tie groups; see
`data/evaluation/README.md`.

## Categories

All category scores are normalized to a `0` to `100` scale. Missing data is not treated as zero. When a category has no usable data, the category receives a neutral score of `50.0` and `0.0` confidence so the uncertainty is visible separately from fit.

| Category key | Inputs used | Method |
| --- | --- | --- |
| `academic` | Intended major, academic interests, listed majors, graduation rate, retention rate, student-faculty ratio | Rewards major/interests matches, stronger graduation and retention rates, and lower student-faculty ratios. |
| `cost` | Max annual cost, net price, average aid, tuition, median debt, aid importance | Rewards schools within budget, lower net price, stronger aid relative to tuition, and lower median debt. |
| `career` | Median earnings, repayment rate, career priorities, culture tags | Rewards stronger earnings, repayment, and deterministic matches between career priorities and known tags such as `career-focused`, `technical`, `research`, or `urban`. |
| `location` | Home state, preferred states, preferred regions, school state, school region | Rewards exact preferred-state matches, then region or home-state alignment. |
| `campus` | Preferred setting, school type, campus preferences, housing, sports division, Greek-life rate, culture tags | Rewards setting/type matches and deterministic lifestyle matches such as residential housing, athletics, Greek life, commuter-friendly tags, and small-class tags. |
| `admissions_realism` | Acceptance rate, admissions strategy, target acceptance-rate comfort | Scores selectivity against a `likely`, `balanced`, or `reach` strategy and any minimum acceptance-rate comfort value. This is not admissions advice or an admission probability. |

## Weights

The ranking service accepts user preference weights from onboarding. Supported weight keys are:

- `academic`
- `cost`
- `career`
- `location`
- `campus`
- `admissions_realism`

The service also accepts documented aliases such as `academic_fit`, `campus_lifestyle`, and `admissions`. Unknown weight keys are ignored. Positive supported weights are normalized to sum to `1.0`.

If no usable weights are provided, V1.9 uses these defaults:

```json
{
  "academic": 0.20,
  "cost": 0.20,
  "career": 0.18,
  "location": 0.14,
  "campus": 0.14,
  "admissions_realism": 0.14
}
```

The overall `fit_score` is the weighted sum of category scores, rounded to two decimals.

## Hybrid Semantic Search

`POST /semantic-search` combines retrieval with the deterministic engine. Since `RANKING_VERSION` v1.2:

1. Structured filters are applied inside the candidate query, before the candidate limit.
2. Candidates are retrieved by vector similarity when embeddings exist, or by a deterministic lexical fallback over the same search documents when they do not.
3. The ranking engine removes schools that violate hard constraints and computes fit scores, confidence, reasons, and tradeoffs, exactly as for `POST /rankings`.
4. The page is ordered by query relevance, and the fit order breaks ties between equally relevant schools.

Relevance decides order but never overrides a hard constraint or changes a score. Before v1.2 the page was ordered by fit alone and the similarity score was display-only, which discarded more than half of retrieval's precision in offline evaluation.

The lexical fallback is stable for local development and tests and does not require paid API keys.

Semantic match tags are separate from ranking reason codes. They explain retrieval alignment only and may include:

- `major_match`
- `location_match`
- `setting_match`
- `cost_value_match`
- `outcomes_match`
- `campus_culture_match`

These tags do not alter `fit_score`, category scores, or hard-constraint behavior.

## Similar-School Scoring

V2.3 similar-school discovery adds a deterministic `similarity_score` from three bounded components:

- Semantic/document similarity to the source school.
- Structured similarity, including school type, setting, region, overlapping majors, and campus/culture tags.
- Variant alignment for `cheaper`, `less_selective`, `smaller`, `stronger_outcomes`, or `closer_to_home`.

The source school is excluded before ranking. Variant constraints are applied before response assembly, so a result for `cheaper` must be lower cost when both schools have known net price, `smaller` must have lower enrollment when known, and `less_selective` must have a higher acceptance rate when known. Missing data remains unknown; it does not become zero.

Similar-school responses also include a `fit_score` generated by the existing deterministic ranking service against a source-like preference profile. That fit score is supporting context only; it does not permit a candidate to bypass variant constraints.

V2.3 does not change `RANKING_VERSION` because the core ranking formula is unchanged.

## Acceptance Decision Reports

V2.4 decision reports and V2.7 shareable decision reports do not change `RANKING_VERSION`. They reuse the existing ranking service for fit score, category scores, reason codes, tradeoffs, and confidence. The decision report version is separate (`v2.7`) because report assembly can evolve without changing school ranking formulas.

Decision report categories are intentionally distinct:

| Output | Deterministic basis |
| --- | --- |
| Best overall fit | Highest weighted `fit_score` from the ranking engine. |
| Best value | Lowest known `estimated_yearly_cost` from the acceptance offer, falling back to profile `net_price` only when offer cost is missing. |
| Strongest career upside | Highest deterministic `career` category score. |
| Lowest risk | Lowest bounded risk proxy using known cost, ranking confidence, and unresolved concern count. |
| Biggest unresolved factor | School with the most user-entered unresolved concerns/questions. |

V2.7 adds report sections without adding opaque scoring:

| Output | Deterministic basis |
| --- | --- |
| Finalist ranking table | Existing ranking order, fit score, confidence, estimated cost, career score, and top deterministic tradeoff. |
| Category score table | Existing ranking category scores for academic, cost, career, location, campus, and admissions realism. |
| Cost/value comparison | Existing cost/value formulas applied to report finalists and offer assumptions. |
| Sensitivity highlights | Existing ranking engine rerun over the same finalists with cost, career, and academic emphasis scenarios. |
| Unresolved questions | User-entered unresolved concerns, falling back to explicit confidence gaps. |

Missing offer costs, missing profile net price, missing outcomes metrics, incomplete preference weights, limited ranking confidence, and fewer than two finalists create confidence flags. They lower decision confidence but do not become zero scores. Major tradeoff sentences are deterministic templates using selected school names and known metrics only.

Decision reports are decision-support summaries, not admissions advice, financial advice, ROI guarantees, or predictions. Cost/value modeling and sensitivity analysis are handled by separate V2.5/V2.6 services so decision-report categories do not become opaque blended scores.

## Cost/Value Calculator

V2.5 cost/value calculation does not change `RANKING_VERSION`. It has its own `calculator_version` (`v1.0`) because financial estimates are separate from best-fit ranking.

The calculator is deterministic and formula-driven:

| Output | Deterministic basis |
| --- | --- |
| Estimated yearly cost | Entered yearly cost first; otherwise entered net price or tuition minus scholarships and grants/aid; otherwise profile net price or tuition minus entered scholarships and grants/aid. |
| Estimated four-year total cost | Estimated yearly cost multiplied by `4`. V2.5 does not model inflation or year-by-year tuition changes. |
| Yearly and four-year cost differences | Difference from the selected baseline school's estimated yearly and four-year costs. |
| Estimated debt exposure | Entered annual loan amount multiplied by `4`; if missing, observed median debt may be displayed as a data indicator with a warning. |
| Repayment scenarios | Standard amortization for lower debt, base debt, and higher debt using the entered interest rate and term. |
| Affordability indicator | Compares estimated yearly cost with the entered family yearly budget. |
| Directional outcome-adjusted value | Uses known four-year cost, median earnings, graduation rate, and repayment rate. Missing outcomes produce `uncertain`. |

The calculator intentionally avoids an opaque ROI score. Labels such as `stronger_value`, `reasonable_value`, `higher_cost_tradeoff`, and `uncertain` are directional summaries of visible formulas and known data. They do not alter ranking fit scores, admission realism, or decision-report best-fit categories.

Missing aid data, profile net price, loan assumptions, median earnings, graduation rate, or repayment rate creates warnings and lowers calculator confidence. Unknown values remain unknown instead of becoming zero.

## Sensitivity Analysis

V2.6 sensitivity analysis does not change `RANKING_VERSION`. It reruns the existing deterministic ranking engine against the same candidate rows with adjusted normalized weights, then compares baseline and scenario rank positions.

Supported sensitivity dimensions are:

- `academic` / `academic_fit`
- `cost` / `cost_value`
- `career` / `career_outcomes`
- `campus` / `campus_lifestyle`
- `location`
- `prestige_selectivity`
- `admissions_realism`

`prestige_selectivity` is not a separate prestige score. It is modeled as a selectivity-emphasis scenario over the existing admissions-realism scoring path by applying the scenario weight to `admissions_realism` and using a `reach` admissions strategy for that scenario. This keeps the output explainable through existing category scores and reason codes.

Sensitivity outputs are deterministic:

| Output | Deterministic basis |
| --- | --- |
| Ranking movement | Baseline rank minus scenario rank for the same school. Positive movement means the school rises in the scenario. |
| Stable choice | A highly ranked school with little rank movement and small fit-score movement across tested scenarios. |
| Volatile choice | A school with large rank movement or large fit-score movement when one priority changes. |
| Category drivers | Weighted category contribution differences between baseline and scenario results, ordered by largest visible change. |
| Confidence impacts | Changes in `confidence_score` caused by emphasizing categories with different data coverage. |
| Tradeoff explanations | Deterministic templates based on rank deltas and category drivers. |

Sensitivity analysis does not alter stored rankings, does not smooth or randomize results, and does not generate opaque confidence. Missing data continues to lower category confidence while neutral category scores avoid treating unknowns as zero.

## Ranking Evaluation

V2.8 analytics and ranking evaluation do not change `RANKING_VERSION`. Evaluation reads privacy-safe product events and summarizes observed behavior around deterministic ranking outputs.

Evaluation outputs are descriptive:

| Output | Deterministic basis |
| --- | --- |
| Save rate by fit-score bucket | `school_saved` events divided by observed ranked-school exposures in the same fit bucket. |
| Compare rate by ranking position | `school_compared` events divided by observed ranked-school exposures in the same rank-position bucket. |
| Top reason-code frequency | Counts of deterministic `top_reasons` emitted in ranking events. |
| Confidence distribution | Buckets from ranking `confidence_score` values: high, medium, low, or unknown. |
| Ranking-version distribution | Counts of event metadata grouped by `ranking_version`. |
| Category-weight save summaries | The strongest normalized category weight observed on saved-school events. |

These metrics are not causal proof. A high save rate for high-fit schools can suggest alignment between ranking and user behavior, but it can also reflect self-selection, small samples, demo data, or users only saving schools they already liked. V2.8 keeps the caveats visible in the API and frontend dashboard.

Known evaluation limitations:

- Incomplete public data can depress confidence and shift schools into lower or neutral score buckets.
- Prestige/selectivity preferences can appear as engagement bias when users manually choose well-known schools.
- Local browser workflows are not authenticated user histories, so repeated demos can overrepresent a small set of schools.
- Public-data limitations and missing outcomes fields mean value/career conclusions are directional.
- Weighting sensitivity can change rankings without indicating that one weighting scheme is objectively better.

## Confidence

Confidence is separate from fit. Each category tracks how much of its scoring signal was available. Overall `confidence_score` is the weighted sum of category confidences, rounded to four decimals.

Examples:

- A school with missing cost data is not assigned a zero cost score. It receives neutral cost fit and low cost confidence.
- A school with known outcomes but no matching career-priority tags can still score on career outcomes, but confidence reflects only the available components.
- A high fit score with lower confidence should be shown as promising but data-limited, not as more certain than the source data supports.

## Hard Constraints

Hard constraints are optional and configured through the preference profile `constraints` object. V1.9 supports strict checks for:

- `strict_major`, `major_strict`, `require_major`
- `strict_cost`, `cost_strict`, `require_cost`
- `strict_state`, `strict_region`, `strict_setting`, `strict_school_type`
- `strict_constraints`, a list such as `["major", "cost"]`

Preference constraint values may be supplied as a single string, comma- or pipe-separated string, or list of strings. The ranking engine normalizes these values before matching, so documented list fields such as `preferred_states`, `preferred_regions`, `preferred_settings`, `preferred_school_types`, and `campus_preferences` are evaluated as individual preferences.

Strict major filters out schools whose known major list does not contain the intended major or academic interests. Strict cost filters out schools whose known net price is above `max_annual_cost`. Unknown data is not treated as a violation; it remains reflected in confidence.

### Product decision: budget is a soft signal (2026-09-12)

None of the strict flags are set by the app, and that is deliberate. A school priced above
a student's `max_annual_cost` is **ranked lower, not removed**.

The reasoning: a student who says "$30,000" usually means "$30,000 unless something is
worth stretching for." Removing an over-budget school hides the tradeoff instead of
presenting it; ranking it lower shows the school, shows the cost penalty in its category
score, and lets the student decide. It also avoids empty result sets on a ~100-school
corpus, which is what silently discarding candidates would produce.

V3.1 removed the one place this was violated: onboarding used to copy preferred state,
setting, and school type into URL filters, which the search endpoint applies as SQL
`WHERE` clauses. That made soft preferences behave as hard cuts and contradicted this
design. Preferences are now soft everywhere.

If a strict budget is ever wanted, set `strict_cost` in the preference `constraints` -
the engine already supports it, so it is a configuration change, not new code.

## Reason Codes

Explanations are deterministic code strings, not generated prose. The service chooses:

- `top_reasons`: the strongest 2 to 3 positive category signals by weighted contribution.
- `top_tradeoffs`: the largest 1 to 2 penalties or lowest-confidence categories by weighted penalty.

Example reason and tradeoff codes include:

- `academic_major_match`
- `academic_major_not_listed`
- `cost_within_budget`
- `cost_above_budget`
- `career_strong_earnings`
- `career_priorities_less_visible`
- `location_preferred_state`
- `campus_preferred_setting`
- `<category>_data_limited` for each category (`academic`, `cost`, `career`, `location`,
  `campus`, `admissions_realism`) when confidence is below 0.5 - the evidence is too
  thin to make a claim about the school
- `admissions_meets_acceptance_comfort`
- `admissions_below_acceptance_comfort`

Clients may map these codes to user-facing copy, but the codes themselves are the ranking explanation source of truth for V1.9.
