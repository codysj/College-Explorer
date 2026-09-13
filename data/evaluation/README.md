# Retrieval evaluation

Offline evaluation of `POST /semantic-search` (V3.6). Everything here runs in-process against
the committed seed; only the optional Postgres full-text arm needs a database.

```bash
python apps/api/scripts/evaluate_retrieval.py --per-query
```

## Files

| File | What it is |
| --- | --- |
| `retrieval_queries.json` | 35 labeled queries. Committed before any retrieval change, so the labels cannot have been tuned to a method. |
| `results-baseline.md` | The pipeline as it first shipped, measured before anything changed. |
| `results-variants.md` | Documents, filtering, and ordering variants that led to `RANKING_VERSION` v1.2. |
| `results-v1.2.md` | The v1.2 pipeline, the pre-v1.2 pipeline for comparison, and candidate retrievers. |

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

- **Production equivalence.** The v1.2 configurations are run through the real
  `SemanticSearchService` for every query and candidate limit. If the harness's pipeline and the
  service disagree on a single result, the script exits instead of reporting.
- **A faithful baseline.** The pre-v1.2 configurations are rebuilt from a frozen copy of the v2.2
  document builder. Their numbers reproduce `results-variants.md` exactly.

## Metrics

- **Pool recall** - share of relevant schools that survive retrieval and filtering.
- **Retriever P@10** - precision of the pool in similarity order: the retriever on its own.
- **End-to-end P@10** - precision of the page a student actually sees.
- **Mean fit** - average deterministic fit score of that page, which shows what respecting the
  query costs.

Precision is normalised by `min(10, relevant count)`.

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
local database. None of it is API latency.
