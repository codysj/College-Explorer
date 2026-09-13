"""Offline retrieval evaluation for semantic search (V3.6).

Measures semantic search against a labeled query set (data/evaluation/retrieval_queries.json)
whose relevance is defined by explicit attribute predicates. The labels were committed before
any retrieval change.

Runs entirely in-process against the committed seed: no Postgres, no network. Each
configuration is a pipeline of four choices - retriever, document text, where hard filters
apply, and how the final page is ordered. The two production configurations are checked
against the real SemanticSearchService for every query and candidate limit, and the script
refuses to report if they diverge, so every other configuration is a like-for-like change to
code that actually ships.

It separates three things that a single score would blur:
  pool recall        share of relevant schools that survive retrieval and filtering
  retriever P@10     precision of the pool in similarity order - the retriever alone
  end-to-end P@10    precision of the page a student sees after final ordering

Precision is normalised by min(10, relevant count), so a query with three relevant schools can
still reach 1.0. "Mean fit" is the average deterministic fit score of that page. Ranking runs
with an empty preference profile plus any filter-derived preferences, so it measures general
desirability rather than personal fit - it is there to show what respecting relevance costs.

Latency is in-process pipeline time only, excluding the database and network. It is not API
latency.

Usage:
    python apps/api/scripts/evaluate_retrieval.py
    python apps/api/scripts/evaluate_retrieval.py --candidate-limits 10 25 50 --per-query
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(API_ROOT))

from ingestion.college_data import load_seed_rows  # noqa: E402
from schemas.preferences import Preference  # noqa: E402
from schemas.schools import SearchRequest  # noqa: E402
from schemas.semantic_search import SemanticSearchRequest  # noqa: E402
from services.ranking_service import RankingService  # noqa: E402
from services.semantic_search import (  # noqa: E402
    LocalHashEmbeddingProvider,
    SemanticSearchService,
    build_search_document,
    join_values,
    merged_preferences,
    row_matches_filters,
    tokenize,
)

QUERIES_PATH = REPO_ROOT / "data" / "evaluation" / "retrieval_queries.json"
SEED_PATH = REPO_ROOT / "data" / "seed" / "schools_seed.csv"
TOP_K = 10

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
DIVISION_WORDS = {"DI": "NCAA Division I", "DII": "NCAA Division II", "DIII": "NCAA Division III", "NAIA": "NAIA"}


def standard_document(row: dict[str, object]) -> str:
    return build_search_document(row).text


def clean_document(row: dict[str, object]) -> str:
    """Candidate document: coded values spelled out, shared boilerplate removed.

    Production documents repeat identical labels in every school's text - "majors programs:",
    "in-state tuition", "cost value affordability:", "campus culture:" - plus a source line,
    so query words such as programs, in, state, cost, value, or campus match all 92 schools
    equally. States appear only as two-letter abbreviations, so "Florida" matches nothing,
    while abbreviations such as IN and OR also collide with common query words. Athletics
    appears as a code such as DIII. Raw numbers are dropped: text retrieval cannot compare
    them, and structured filters already do.
    """
    division = row.get("sports_division")
    lines = [
        row.get("name"),
        f"{row.get('city')}, {STATE_NAMES.get(str(row.get('state')), '')}, {row.get('region')}",
        f"{row.get('type')} {row.get('setting')}",
        join_values(row.get("top_majors")),
        join_values(row.get("culture_tags")),
        DIVISION_WORDS.get(str(division), "") if division else "",
    ]
    return "\n".join(str(line) for line in lines if line)


DOCUMENTS = {"standard": standard_document, "clean": clean_document}


@dataclass(frozen=True)
class Config:
    name: str
    retriever: str  # "hash" or "lexical"
    document: str  # "standard" or "clean"
    filtering: str  # "post" (production: filter the nearest candidates) or "pre" (filter first)
    ordering: str  # "fit" (production), "relevance", or "matched_then_fit"
    production: bool = False


CONFIGS = [
    Config("hash (production)", "hash", "standard", "post", "fit", production=True),
    Config("lexical (production fallback)", "lexical", "standard", "post", "fit", production=True),
    Config("hash + clean docs", "hash", "clean", "post", "fit"),
    Config("lexical + clean docs", "lexical", "clean", "post", "fit"),
    Config("lexical + clean + filter first", "lexical", "clean", "pre", "fit"),
    # Order by how well a school matches the query, with fit breaking ties.
    Config("lexical + clean + filter first + relevance order", "lexical", "clean", "pre", "relevance"),
    # Keep fit as the order, but only among schools that match the query at all.
    Config("lexical + clean + filter first + matched then fit", "lexical", "clean", "pre", "matched_then_fit"),
]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class Scorer:
    """Precomputes document text, hash vectors, and token sets once per document variant."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.provider = LocalHashEmbeddingProvider()
        self.vectors: dict[str, dict[int, list[float]]] = {}
        self.tokens: dict[str, dict[int, set[str]]] = {}
        for variant, build in DOCUMENTS.items():
            texts = {int(row["school_id"]): build(row) for row in rows}
            self.vectors[variant] = {school_id: self.provider.embed(text) for school_id, text in texts.items()}
            self.tokens[variant] = {school_id: set(tokenize(text)) for school_id, text in texts.items()}

    def score(self, retriever: str, document: str, query: str, school_ids: list[int]) -> dict[int, float]:
        if retriever == "hash":
            query_vector = self.provider.embed(query)
            return {school_id: cosine(query_vector, self.vectors[document][school_id]) for school_id in school_ids}
        # Same formula and rounding as production's lexical_fallback_rows().
        query_tokens = set(tokenize(query))
        return {
            school_id: round(len(query_tokens & self.tokens[document][school_id]) / max(len(query_tokens), 1), 4)
            for school_id in school_ids
        }


class OfflineRepository:
    """Stands in for SchoolRepository so the real service runs without Postgres.

    Reproduces the pgvector query: cosine similarity, nearest first, school id as tiebreak,
    LIMIT candidate_limit. With no vectors it returns nothing, which is exactly the condition
    that sends production onto the lexical fallback. Rows are keyed by unitid rather than the
    database serial id, so exact score ties could order differently than in Postgres.
    """

    def __init__(self, rows: list[dict[str, object]], vectors: dict[int, list[float]] | None) -> None:
        self.rows = rows
        self.vectors = vectors

    def get_semantic_document_rows(self) -> list[dict[str, object]]:
        return self.rows

    def get_vector_candidate_rows(
        self, query_vector: list[float], embedding_type: str, embedding_model: str, limit: int
    ) -> list[dict[str, object]]:
        if not self.vectors:
            return []
        scored = []
        for row in self.rows:
            candidate = dict(row)
            candidate["semantic_score"] = cosine(query_vector, self.vectors[int(row["school_id"])])
            scored.append(candidate)
        scored.sort(key=lambda candidate: (-float(candidate["semantic_score"]), int(candidate["school_id"])))
        return scored[:limit]


def size_band(enrollment: object) -> str | None:
    if not isinstance(enrollment, int):
        return None
    return "L" if enrollment >= 20000 else ("M" if enrollment >= 5000 else "S")


def is_relevant(row: dict[str, object], rule: dict[str, object]) -> bool:
    """Evaluate a query's relevant_if predicate. A missing value fails its check."""
    checks = {
        "unitid_in": lambda value: row["school_id"] in value,
        "state_in": lambda value: row.get("state") in value,
        "region_in": lambda value: row.get("region") in value,
        "type": lambda value: row.get("type") == value,
        "setting_in": lambda value: row.get("setting") in value,
        "size_in": lambda value: size_band(row.get("enrollment")) in value,
        "major_any": lambda value: bool(set(value) & set(row.get("top_majors") or [])),
        "division_in": lambda value: row.get("sports_division") in value,
        "max_net_price": lambda value: row.get("net_price") is not None and row["net_price"] <= value,
        "max_acceptance": lambda value: row.get("acceptance_rate") is not None and row["acceptance_rate"] <= value,
        "max_ratio": lambda value: row.get("student_faculty_ratio") is not None
        and row["student_faculty_ratio"] <= value,
    }
    unknown = set(rule) - set(checks)
    if unknown:
        raise SystemExit(f"unknown predicate keys: {sorted(unknown)}")
    return all(checks[key](value) for key, value in rule.items())


def build_request(spec: dict, limit: int) -> SemanticSearchRequest:
    filters = SearchRequest(**spec.get("filters", {}), page=1, page_size=TOP_K)
    return SemanticSearchRequest(query=spec["query"], filters=filters, preferences=Preference(), candidate_limit=limit)


def run_pipeline(
    config: Config,
    scorer: Scorer,
    ranking: RankingService,
    rows_by_id: dict[int, dict[str, object]],
    request: SemanticSearchRequest,
) -> tuple[list[int], list[int], dict[int, float], dict[int, float]]:
    """Returns the pool in similarity order, the final page, fit scores, and similarity scores."""
    filters = request.filters
    all_ids = sorted(rows_by_id)
    candidates = (
        [school_id for school_id in all_ids if row_matches_filters(rows_by_id[school_id], filters)]
        if config.filtering == "pre"
        else all_ids
    )
    scores = scorer.score(config.retriever, config.document, request.query, candidates)
    nearest = sorted(candidates, key=lambda school_id: (-scores[school_id], school_id))[: request.candidate_limit]
    pool = (
        nearest
        if config.filtering == "pre"
        else [school_id for school_id in nearest if row_matches_filters(rows_by_id[school_id], filters)]
    )

    ranked = ranking.rank_rows([rows_by_id[school_id] for school_id in pool], merged_preferences(request))
    fit_order = [int(item.row["school_id"]) for item in ranked]
    fit = {int(item.row["school_id"]): item.fit_score for item in ranked}

    if config.ordering == "fit":
        final = fit_order
    elif config.ordering == "relevance":
        position = {school_id: index for index, school_id in enumerate(fit_order)}
        final = sorted(fit_order, key=lambda school_id: (-scores[school_id], position[school_id]))
    elif config.ordering == "matched_then_fit":
        final = [s for s in fit_order if scores[s] > 0] + [s for s in fit_order if scores[s] <= 0]
    else:
        raise SystemExit(f"unknown ordering {config.ordering!r}")
    return pool, final[:TOP_K], fit, scores


def verify_production_equivalence(rows, scorer, ranking, rows_by_id, queries, limits) -> int:
    """Fail loudly unless the production configurations reproduce the real service exactly."""
    services = {
        "hash": SemanticSearchService(
            OfflineRepository(rows, scorer.vectors["standard"]), embedding_provider=scorer.provider
        ),
        "lexical": SemanticSearchService(OfflineRepository(rows, None), embedding_provider=scorer.provider),
    }
    checked = 0
    for config in (c for c in CONFIGS if c.production):
        for limit in limits:
            for spec in queries:
                request = build_request(spec, limit)
                _, final, _, _ = run_pipeline(config, scorer, ranking, rows_by_id, request)
                actual = [result.school_id for result in services[config.retriever].search(request).results]
                if final != actual:
                    raise SystemExit(
                        f"harness diverges from production for {config.name!r}, limit {limit}, "
                        f"query {spec['id']!r}: harness {final} vs service {actual}"
                    )
                checked += 1
    return checked


def precision(ids: list[int], relevant: set[int]) -> float:
    return len(set(ids[:TOP_K]) & relevant) / min(TOP_K, len(relevant))


def evaluate(rows, queries, limits, repeats):
    rows_by_id = {int(row["school_id"]): row for row in rows}
    scorer = Scorer(rows)
    ranking = RankingService(OfflineRepository(rows, None))

    checked = verify_production_equivalence(rows, scorer, ranking, rows_by_id, queries, limits)
    print(f"production equivalence: {checked} query runs match the real SemanticSearchService exactly")

    results = []
    for config in CONFIGS:
        for limit in limits:
            for spec in queries:
                request = build_request(spec, limit)
                relevant = {
                    school_id
                    for school_id, row in rows_by_id.items()
                    if row_matches_filters(row, request.filters) and is_relevant(row, spec["relevant_if"])
                }
                timings = []
                for _ in range(repeats):
                    started = time.perf_counter()
                    pool, final, fit, _ = run_pipeline(config, scorer, ranking, rows_by_id, request)
                    timings.append(time.perf_counter() - started)
                results.append(
                    {
                        "config": config.name,
                        "limit": limit,
                        "id": spec["id"],
                        "category": spec["category"],
                        "relevant": len(relevant),
                        "pool_size": len(pool),
                        "pool_recall": len(set(pool) & relevant) / len(relevant),
                        "retriever_p10": precision(pool, relevant),
                        "end_to_end_p10": precision(final, relevant),
                        "empty": not final,
                        "mean_fit": statistics.fmean(fit[s] for s in final) if final else float("nan"),
                        "timings": timings,
                    }
                )
    return results


def mean(values):
    values = [value for value in values if not (isinstance(value, float) and math.isnan(value))]
    return statistics.fmean(values) if values else float("nan")


def percentile(values, share):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(share * len(ordered)) - 1))]


def report(results, limits, per_query):
    groups = defaultdict(list)
    for result in results:
        groups[(result["config"], result["limit"])].append(result)

    print("\n## Overall\n")
    print(
        "| configuration | limit | pool recall | retriever P@10 | end-to-end P@10 "
        "| filtered queries empty | mean fit (page) | in-process p50 / p95 ms |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (name, limit), group in groups.items():
        filtered = [row for row in group if row["category"] == "filtered"]
        timings = [t * 1000 for row in group for t in row["timings"]]
        print(
            f"| {name} | {limit} | {mean(r['pool_recall'] for r in group):.2f} "
            f"| {mean(r['retriever_p10'] for r in group):.2f} | {mean(r['end_to_end_p10'] for r in group):.2f} "
            f"| {sum(r['empty'] for r in filtered)}/{len(filtered)} | {mean(r['mean_fit'] for r in group):.1f} "
            f"| {percentile(timings, 0.5):.2f} / {percentile(timings, 0.95):.2f} |"
        )

    focus = max(limits)
    categories = sorted({result["category"] for result in results})
    print(f"\n## End-to-end P@10 by query category, candidate limit {focus}\n")
    print("| configuration | " + " | ".join(categories) + " |")
    print("| --- | " + " | ".join("---:" for _ in categories) + " |")
    for (name, limit), group in groups.items():
        if limit != focus:
            continue
        cells = [f"{mean(r['end_to_end_p10'] for r in group if r['category'] == c):.2f}" for c in categories]
        print(f"| {name} | " + " | ".join(cells) + " |")

    if per_query:
        print("\n## Per query\n")
        print("| configuration | limit | query | category | relevant | pool | pool recall | retriever P@10 | end-to-end P@10 | empty |")
        print("| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
        for r in results:
            print(
                f"| {r['config']} | {r['limit']} | {r['id']} | {r['category']} | {r['relevant']} | {r['pool_size']} "
                f"| {r['pool_recall']:.2f} | {r['retriever_p10']:.2f} | {r['end_to_end_p10']:.2f} "
                f"| {'yes' if r['empty'] else ''} |"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate-limits", type=int, nargs="+", default=[10, 25, 50])
    parser.add_argument("--repeats", type=int, default=5, help="timed runs per query")
    parser.add_argument("--per-query", action="store_true")
    args = parser.parse_args()

    rows = load_seed_rows(SEED_PATH)
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))["queries"]

    # Every query must have at least one relevant school, or its precision is undefined and a
    # typo in a predicate would silently score as a retrieval failure.
    for query in queries:
        filters = SearchRequest(**query.get("filters", {}))
        if not any(row_matches_filters(row, filters) and is_relevant(row, query["relevant_if"]) for row in rows):
            raise SystemExit(f"query {query['id']!r} has no relevant schools; check its predicate")

    counts = defaultdict(int)
    for query in queries:
        counts[query["category"]] += 1
    print(f"{len(queries)} queries over {len(rows)} schools; candidate limits {args.candidate_limits}")
    print("queries per category:", dict(sorted(counts.items())))
    report(evaluate(rows, queries, args.candidate_limits, args.repeats), args.candidate_limits, args.per_query)


if __name__ == "__main__":
    sys.exit(main())
