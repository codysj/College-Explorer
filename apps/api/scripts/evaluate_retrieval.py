"""Offline retrieval evaluation for semantic search (V3.6).

Measures the semantic search pipeline as it runs in production today against a labeled
query set (data/evaluation/retrieval_queries.json) whose relevance is defined by explicit
attribute predicates. The labels were written before any retrieval change.

Runs entirely in-process against the committed seed: no Postgres, no network. The pgvector
query is reproduced exactly - cosine similarity, nearest first, school id as tiebreak, then
LIMIT candidate_limit - and the real SemanticSearchService then applies its filters and its
deterministic re-rank, so end-to-end numbers reflect the code that ships.

It separates three things that a single score would blur:
  pool recall        share of relevant schools that survive retrieval and filtering
  retriever P@10     precision of the pool in similarity order - the retriever alone
  end-to-end P@10    precision of what a student actually sees after the fit re-rank

Precision is normalised by min(10, relevant count), so a query with three relevant schools
can still reach 1.0. Latency is in-process only and excludes the database and network, so it
is not API latency.

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
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(API_ROOT))

from ingestion.college_data import load_seed_rows  # noqa: E402
from schemas.preferences import Preference  # noqa: E402
from schemas.schools import SearchRequest  # noqa: E402
from schemas.semantic_search import SemanticSearchRequest  # noqa: E402
from services.semantic_search import (  # noqa: E402
    LocalHashEmbeddingProvider,
    SemanticSearchService,
    build_search_document,
    lexical_fallback_rows,
    row_matches_filters,
)

QUERIES_PATH = REPO_ROOT / "data" / "evaluation" / "retrieval_queries.json"
SEED_PATH = REPO_ROOT / "data" / "seed" / "schools_seed.csv"
TOP_K = 10


class OfflineRepository:
    """Stands in for SchoolRepository so the real service runs without Postgres.

    `vectors` mirrors the school_embeddings table. With no vectors the vector query returns
    nothing, which is exactly the condition that sends production onto the lexical fallback.
    """

    def __init__(self, rows: list[dict[str, object]], vectors: dict[int, list[float]] | None) -> None:
        self.rows = rows
        self.vectors = vectors

    def get_semantic_document_rows(self) -> list[dict[str, object]]:
        return self.rows

    def get_vector_candidate_rows(
        self,
        query_vector: list[float],
        embedding_type: str,
        embedding_model: str,
        limit: int,
    ) -> list[dict[str, object]]:
        if not self.vectors:
            return []
        scored = []
        for row in self.rows:
            candidate = dict(row)
            candidate["semantic_score"] = cosine(query_vector, self.vectors[int(row["school_id"])])
            scored.append(candidate)
        # The SQL orders by cosine distance ascending, then school id: nearest first.
        scored.sort(key=lambda candidate: (-float(candidate["semantic_score"]), int(candidate["school_id"])))
        return scored[:limit]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


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


def precision(ids: list[int], relevant: set[int]) -> float:
    return len(set(ids[:TOP_K]) & relevant) / min(TOP_K, len(relevant))


def build_arms(rows: list[dict[str, object]]) -> dict[str, tuple[SemanticSearchService, dict[int, list[float]] | None]]:
    provider = LocalHashEmbeddingProvider()
    hash_vectors = {int(row["school_id"]): provider.embed(build_search_document(row).text) for row in rows}
    return {
        # Production today: pgvector over 64-bucket hash embeddings.
        "hash": (SemanticSearchService(OfflineRepository(rows, hash_vectors), embedding_provider=provider), hash_vectors),
        # Production's fallback when the vector query returns nothing: token-set overlap.
        "lexical": (SemanticSearchService(OfflineRepository(rows, None), embedding_provider=provider), None),
    }


def prefiltered_pool(
    arm: str,
    rows: list[dict[str, object]],
    filters: SearchRequest,
    query: str,
    limit: int,
    vectors: dict[int, list[float]] | None,
) -> list[int]:
    """The proposed fix: apply hard filters before ranking by similarity, not after."""
    eligible = [row for row in rows if row_matches_filters(row, filters)]
    if arm == "hash" and vectors:
        query_vector = LocalHashEmbeddingProvider().embed(query)
        ordered = sorted(
            eligible,
            key=lambda row: (-cosine(query_vector, vectors[int(row["school_id"])]), int(row["school_id"])),
        )
    else:
        ordered = lexical_fallback_rows(eligible, query, len(eligible))
    return [int(row["school_id"]) for row in ordered[:limit]]


def evaluate(rows, queries, limits, repeats):
    arms = build_arms(rows)
    results = []  # one dict per (arm, limit, query)
    for arm, (service, vectors) in arms.items():
        for limit in limits:
            for spec in queries:
                filters = SearchRequest(**spec.get("filters", {}), page=1, page_size=TOP_K)
                request = SemanticSearchRequest(
                    query=spec["query"], filters=filters, preferences=Preference(), candidate_limit=limit
                )
                relevant = {
                    int(row["school_id"])
                    for row in rows
                    if row_matches_filters(row, filters) and is_relevant(row, spec["relevant_if"])
                }

                timings = []
                for _ in range(repeats):
                    started = time.perf_counter()
                    response = service.search(request)
                    timings.append(time.perf_counter() - started)

                # The same retrieval and filtering search() performs, exposed to separate the
                # retriever's contribution from the re-rank's.
                candidates, mode = service._retrieve_candidates(request)
                pool = [int(row["school_id"]) for row in candidates if row_matches_filters(row, filters)]
                final = [result.school_id for result in response.results]
                prefiltered = prefiltered_pool(arm, rows, filters, spec["query"], limit, vectors)

                results.append(
                    {
                        "arm": arm,
                        "limit": limit,
                        "id": spec["id"],
                        "category": spec["category"],
                        "relevant": len(relevant),
                        "mode": mode,
                        "pool_size": len(pool),
                        "pool_recall": len(set(pool) & relevant) / len(relevant),
                        "prefiltered_recall": len(set(prefiltered) & relevant) / len(relevant),
                        "retriever_p10": precision(pool, relevant),
                        "prefiltered_p10": precision(prefiltered, relevant),
                        "end_to_end_p10": precision(final, relevant),
                        "empty": not final,
                        "prefiltered_empty": not prefiltered,
                        "timings": timings,
                    }
                )
    return results


def mean(values):
    values = list(values)
    return statistics.fmean(values) if values else float("nan")


def percentile(values, share):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(share * len(ordered)) - 1))]


def report(results, per_query):
    print("\n## Overall\n")
    print("| arm | candidate_limit | pool recall | retriever P@10 | end-to-end P@10 | filtered: empty (post) | filtered: empty (pre) | filtered: recall post -> pre | in-process p50 / p95 ms |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    groups = defaultdict(list)
    for result in results:
        groups[(result["arm"], result["limit"])].append(result)
    for (arm, limit), rows in groups.items():
        filtered = [row for row in rows if row["category"] == "filtered"]
        timings = [t * 1000 for row in rows for t in row["timings"]]
        print(
            f"| {arm} | {limit} | {mean(r['pool_recall'] for r in rows):.2f} | {mean(r['retriever_p10'] for r in rows):.2f} "
            f"| {mean(r['end_to_end_p10'] for r in rows):.2f} "
            f"| {sum(r['empty'] for r in filtered)}/{len(filtered)} | {sum(r['prefiltered_empty'] for r in filtered)}/{len(filtered)} "
            f"| {mean(r['pool_recall'] for r in filtered):.2f} -> {mean(r['prefiltered_recall'] for r in filtered):.2f} "
            f"| {percentile(timings, 0.5):.2f} / {percentile(timings, 0.95):.2f} |"
        )

    print("\n## Retriever P@10 by query category\n")
    categories = sorted({result["category"] for result in results})
    print("| arm | candidate_limit | " + " | ".join(categories) + " |")
    print("| --- | ---: | " + " | ".join("---:" for _ in categories) + " |")
    for (arm, limit), rows in groups.items():
        cells = [f"{mean(r['retriever_p10'] for r in rows if r['category'] == c):.2f}" for c in categories]
        print(f"| {arm} | {limit} | " + " | ".join(cells) + " |")

    if per_query:
        print("\n## Per query\n")
        print("| arm | limit | query | category | relevant | pool | pool recall | retriever P@10 | end-to-end P@10 | empty |")
        print("| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
        for r in results:
            print(
                f"| {r['arm']} | {r['limit']} | {r['id']} | {r['category']} | {r['relevant']} | {r['pool_size']} "
                f"| {r['pool_recall']:.2f} | {r['retriever_p10']:.2f} | {r['end_to_end_p10']:.2f} | {'yes' if r['empty'] else ''} |"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate-limits", type=int, nargs="+", default=[10, 25, 50])
    parser.add_argument("--repeats", type=int, default=5, help="timed runs per query")
    parser.add_argument("--per-query", action="store_true")
    args = parser.parse_args()

    rows = load_seed_rows(SEED_PATH)
    spec = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))
    queries = spec["queries"]

    # Every query must have at least one relevant school, or its precision is undefined and a
    # typo in a predicate would silently score as a retrieval failure.
    for query in queries:
        filters = SearchRequest(**query.get("filters", {}))
        count = sum(1 for row in rows if row_matches_filters(row, filters) and is_relevant(row, query["relevant_if"]))
        if count == 0:
            raise SystemExit(f"query {query['id']!r} has no relevant schools; check its predicate")

    print(f"{len(queries)} queries over {len(rows)} schools; candidate limits {args.candidate_limits}")
    counts = defaultdict(int)
    for query in queries:
        counts[query["category"]] += 1
    print("queries per category:", dict(sorted(counts.items())))
    report(evaluate(rows, queries, args.candidate_limits, args.repeats), args.per_query)


if __name__ == "__main__":
    sys.exit(main())
