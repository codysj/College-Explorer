# Retrieval evaluation

Offline evaluation of `POST /semantic-search` (V3.6). Everything here runs in-process against
the committed seed, except the full-text arms, which need `DATABASE_URL` and a running database.
Production is full-text since `RANKING_VERSION` v1.3, so without a database its equivalence
check is skipped and says so.

```bash
python apps/api/scripts/evaluate_retrieval.py --per-query
python apps/api/scripts/evaluate_retrieval.py --queries data/evaluation/holdout_queries.json --per-query
```

## Headline, read carefully

Production (Postgres full-text) at the default candidate limit of 50, on data version
`scorecard-2023.4`:

| Query set | Queries | End-to-end RP@10 | 95% bootstrap CI |
| --- | ---: | ---: | ---: |
| Development (`retrieval_queries.json`) | 33 | 0.85 | 0.73-0.95 |
| Held-out (`holdout_queries.json`) | 16 | 0.79 | 0.64-0.93 |
| Held-out, the pipeline before v1.2 (hash) | 16 | 0.46 | 0.31-0.61 |

The development number is **in-sample**: the v1.2 document and ordering changes were chosen
by measuring them on those queries. The held-out queries were written after v1.3 froze and
before any was run, so they are the out-of-sample estimate. The intervals are wide because the
sets are small; differences among the top retrievers (full-text, model2vec, hybrids) sit
inside them. What the held-out set does support is the large gap to the pre-v1.2 pipeline.
Both sets were labeled by the project author, so shared blind spots remain possible.

## Files

| File | What it is |
| --- | --- |
| `retrieval_queries.json` | The development set: 33 labeled queries (35 until two labels emptied under the 2023.4 data fix; see its notes). Committed before any retrieval change, but retrieval was then tuned on it, so its results are in-sample. |
| `holdout_queries.json` | 16 held-out queries written after v1.3 froze. Nothing has been tuned on them. |
| `results-baseline.md` | The pipeline as it first shipped, measured before anything changed. |
| `results-variants.md` | Documents, filtering, and ordering variants that led to `RANKING_VERSION` v1.2. |
| `results-v1.2.md` | The v1.2 pipeline, the pre-v1.2 pipeline for comparison, and candidate retrievers. |
| `results-v1.3.md` | The shipped full-text pipeline, checked against the real service, beside the other retrievers. |
| `results-v1.4.md` | The same comparison on corrected data (`scorecard-2023.4`), 33 queries, with confidence intervals. Not directly comparable to earlier files. |
| `results-holdout.md` | The held-out set. |

## How relevance is defined

Each query carries a `relevant_if` predicate over school attributes - state, region, majors,
division, net price, and so on - rather than a hand-picked list of results. A school is
relevant when it satisfies the predicate and passes the query's filters. That makes every label
reproducible, and a query whose predicate matches no school stops the run.

Queries are grouped by the kind of gap they test:

| Category | Tests |
| --- | --- |
| `exact_vocabulary` | The query's words appear in the documents. |
| `state_name` | A state spelled out, where documents once carried only the abbreviation. |
| `synonym` | The same meaning in different words ("nursing" for Health Professions). |
| `world_knowledge` | Facts absent from the documents (Ivy League, HBCU, Bay Area). |
| `structured_only` | Numeric needs, such as "cheap" or "small class sizes". |
| `filtered` | A short topical query plus a hard filter. |

## Integrity checks built into the harness

- **Production equivalence.** The production configurations (full-text and its lexical fallback)
  are run through the real `SemanticSearchService`, with full-text scored by the real repository
  SQL, for every query and candidate limit. If the harness's pipeline and the
  service disagree on a single result, the script exits instead of reporting.
- **A faithful baseline.** The pre-v1.2 configurations are rebuilt from a frozen copy of the v2.2
  document builder. Their numbers reproduce `results-variants.md` exactly.

## Metrics

- **Pool recall** - share of relevant schools that survive retrieval and filtering.
- **Retriever RP@10** - precision of the pool in similarity order: the retriever on its own.
- **End-to-end RP@10** - precision of the page a student actually sees, with a 95% percentile
  bootstrap interval over queries (2,000 resamples, fixed seed). Earlier result files call this
  "P@10".
- **Mean fit** - average deterministic fit score of that page, which shows what respecting the
  query costs.

Precision is normalised by `min(10, relevant count)`, which makes it R-precision capped at ten
rather than plain precision at ten: a query with three relevant schools scores 1.0 when all
three are in the top ten. Relevance predicates read the same fields the search documents are
built from, so these labels measure whether retrieval finds attribute matches, not whether a
student would find the result useful.

## Reading the numbers honestly

That normalisation rewards pulling a whole *tied group* into the top ten. Checked token by token
against the v3.0 documents:

- "nursing school in Florida", "big state university in Ohio", "tech-focused school in Georgia",
  and "cheap public school in Texas" are won by the state name alone. "Nursing", "big", "cheap",
  and "focused" match no document, and "tech" matches only Texas Tech.
- "coding programs in the Midwest" is won by "midwest", which also matches irrelevant schools.
- "film and theater programs" is won by the stopword "and" in "Visual and Performing Arts".
- "selective", "class sizes", "Bay Area", "CS", and "historically black" share nothing
  discriminative with any document.
- The Division II and III wins are genuine: the v3.0 documents spell the divisions out.

So the `synonym` and `structured_only` columns overstate how well word-matching retrievers
understand those queries. Postgres full-text removes stopwords, which is one reason its synonym
score is lower than plain token overlap.

Latency is pipeline time in this process. For the full-text arm it includes a round trip to the
local database. None of it is API latency. On Windows with Docker, connect with `127.0.0.1`
rather than `localhost`: sending the ~16 KB of documents over `localhost` measured about 44 ms
per call against 4 ms on `127.0.0.1`, and the committed results use `127.0.0.1`.
