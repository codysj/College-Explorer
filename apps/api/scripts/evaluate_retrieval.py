"""Offline retrieval evaluation for semantic search (V3.6).

Measures semantic search against a labeled query set (data/evaluation/retrieval_queries.json)
whose relevance is defined by explicit attribute predicates. The labels were committed before
any retrieval change.

Each configuration is a pipeline of four choices - retriever, document text, where hard
filters apply, and how the final page is ordered. Two groups anchor the comparison:

  before v1.2    the pipeline that shipped until RANKING_VERSION v1.2, rebuilt from a frozen
                 copy of the v2.2 document format. Its numbers should reproduce
                 data/evaluation/results-variants.md, which is the check that the copy is faithful.
  v1.2           filter first and relevance order, with the hash embedding it retrieved by.
  v1.3           the pipeline that ships now: v1.2 with Postgres full-text retrieval, which
                 needs DATABASE_URL and a running database. It and the lexical fallback are
                 compared against the real SemanticSearchService, through the real repository
                 SQL, for every query and candidate limit; the script refuses to report if
                 they diverge.

Other retrievers are measured on the same pipeline so only the retriever varies: model2vec
static embeddings (needs the model under data/models) and reciprocal-rank-fusion hybrids.

Metrics:
  pool recall        share of relevant schools that survive retrieval and filtering
  retriever P@10     precision of the pool in similarity order - the retriever alone
  end-to-end P@10    precision of the page a student sees
  mean fit           average deterministic fit score of that page

Precision is normalised by min(10, relevant count). That rewards pulling a whole tied group
into the top ten, so a state name alone can win a query - read the category table with
data/evaluation/README.md. Latency is pipeline time in this process; for the full-text arm it
includes a round trip to the local database. Neither is API latency.

Usage:
    python apps/api/scripts/evaluate_retrieval.py
    python apps/api/scripts/evaluate_retrieval.py --candidate-limits 10 25 50 --per-query
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(API_ROOT))

from ingestion.college_data import load_seed_rows  # noqa: E402
from repositories.schools import SchoolRepository  # noqa: E402
from schemas.preferences import Preference  # noqa: E402
from schemas.schools import SearchRequest  # noqa: E402
from schemas.semantic_search import SemanticSearchRequest  # noqa: E402
from services.ranking_service import RANKING_VERSION, RankingService  # noqa: E402
from services.semantic_search import (  # noqa: E402
    DOCUMENT_VERSION,
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
DEFAULT_MODEL2VEC_PATH = REPO_ROOT / "data" / "models" / "potion-base-8M"
TOP_K = 10
RRF_K = 60  # The conventional reciprocal-rank-fusion constant; not tuned to this query set.
# Each hybrid fuses the rank order of its component retrievers.
RRF_COMPONENTS = {"rrf": ("lexical", "model2vec"), "rrf_fts": ("fts", "model2vec")}



def legacy_rate_text(value: object) -> str:
    if isinstance(value, Decimal):
        return f"{float(value):.2f}"
    return str(value)


def legacy_document(row: dict[str, object]) -> str:
    """Frozen copy of the v2.2 build_search_document(), kept only for the before/after comparison."""
    costs = [
        f"{label} {row[key]}"
        for label, key in (
            ("in-state tuition", "tuition_in_state"),
            ("out-of-state tuition", "tuition_out_state"),
            ("net price", "net_price"),
            ("average aid", "average_aid"),
            ("median debt", "debt_median"),
        )
        if row.get(key) is not None
    ]
    outcomes = []
    if row.get("graduation_rate") is not None:
        outcomes.append(f"graduation rate {legacy_rate_text(row['graduation_rate'])}")
    if row.get("retention_rate") is not None:
        outcomes.append(f"retention rate {legacy_rate_text(row['retention_rate'])}")
    if row.get("median_earnings") is not None:
        outcomes.append(f"median earnings {row['median_earnings']}")
    if row.get("repayment_rate") is not None:
        outcomes.append(f"repayment rate {legacy_rate_text(row['repayment_rate'])}")
    campus = [
        f"housing {row.get('housing_available')}",
        f"sports {row.get('sports_division')}",
        f"greek life {legacy_rate_text(row.get('greek_life_rate'))}",
        f"culture tags {join_values(row.get('culture_tags'))}",
    ]
    fields = [
        f"name: {row.get('name')}",
        f"location: {row.get('city')}, {row.get('state')} {row.get('region')}",
        f"type setting: {row.get('type')} {row.get('setting')}",
        f"majors programs: {join_values(row.get('top_majors'))}",
        "cost value affordability: " + ", ".join(costs),
        "cost outcomes career value: " + ", ".join(outcomes),
        "campus culture: " + ", ".join(value for value in campus if not value.endswith("None")),
        f"source attributes: {row.get('source_name')} {row.get('source_year')} {row.get('data_version')} v2.2",
    ]
    return "\n".join(field for field in fields if field.strip())


DOCUMENTS = {"legacy": legacy_document, "v3": lambda row: build_search_document(row).text}


@dataclass(frozen=True)
class Config:
    name: str
    retriever: str  # hash, lexical, model2vec, fts, or a key of RRF_COMPONENTS
    document: str  # legacy or v3
    filtering: str  # post: filter the nearest candidates; pre: filter first
    ordering: str  # fit: fit order only; relevance: relevance first, fit breaks ties
    production: bool = False


CONFIGS = [
    Config("before v1.2: hash", "hash", "legacy", "post", "fit"),
    Config("before v1.2: lexical fallback", "lexical", "legacy", "post", "fit"),
    Config("v1.2: hash", "hash", "v3", "pre", "relevance"),
    Config("v1.3 production: full-text", "fts", "v3", "pre", "relevance", production=True),
    Config("v1.3 production: lexical fallback", "lexical", "v3", "pre", "relevance", production=True),
    Config("model2vec potion-base-8M", "model2vec", "v3", "pre", "relevance"),
    Config("hybrid: lexical + model2vec (RRF)", "rrf", "v3", "pre", "relevance"),
    Config("hybrid: full-text + model2vec (RRF)", "rrf_fts", "v3", "pre", "relevance"),
]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class Scorer:
    """Precomputes document text, vectors, and token sets, and scores a query per retriever."""

    def __init__(self, rows: list[dict[str, object]], model2vec_path: Path | None, database_url: str | None) -> None:
        self.provider = LocalHashEmbeddingProvider()
        self.texts = {variant: {int(row["school_id"]): build(row) for row in rows} for variant, build in DOCUMENTS.items()}
        self.vectors = {
            variant: {school_id: self.provider.embed(text) for school_id, text in texts.items()}
            for variant, texts in self.texts.items()
        }
        self.tokens = {
            variant: {school_id: set(tokenize(text)) for school_id, text in texts.items()}
            for variant, texts in self.texts.items()
        }
        self.unavailable: dict[str, str] = {}

        self.model = None
        if model2vec_path is None or not model2vec_path.exists():
            self.unavailable["model2vec"] = f"no model at {model2vec_path}"
        else:
            # Guarantees the model loads from the local files and never reaches the network.
            os.environ["HF_HUB_OFFLINE"] = "1"
            from model2vec import StaticModel

            self.model = StaticModel.from_pretrained(str(model2vec_path))
            ids = sorted(self.texts["v3"])
            self.model_index = {school_id: index for index, school_id in enumerate(ids)}
            self.model_matrix = self.model.encode([self.texts["v3"][school_id] for school_id in ids])

        # The production repository, so the full-text arm runs the SQL that ships.
        self.fulltext: SchoolRepository | None = None
        if not database_url:
            self.unavailable["fts"] = "DATABASE_URL not set"
        else:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import Session

            try:
                session = Session(create_engine(database_url, connect_args={"connect_timeout": 3}))
                session.execute(text("SELECT 1"))
                self.fulltext = SchoolRepository(session)
            except Exception as error:  # noqa: BLE001 - any connection failure just skips the arm
                self.unavailable["fts"] = f"database unavailable ({type(error).__name__})"
        for hybrid, components in RRF_COMPONENTS.items():
            missing = [component for component in components if component in self.unavailable]
            if missing:
                self.unavailable[hybrid] = f"needs {', '.join(missing)}"

    def score(self, retriever: str, document: str, query: str, school_ids: list[int]) -> dict[int, float]:
        if not school_ids:
            return {}
        if retriever == "hash":
            query_vector = self.provider.embed(query)
            return {s: cosine(query_vector, self.vectors[document][s]) for s in school_ids}
        if retriever == "lexical":
            # Same formula and rounding as production's lexical_fallback_rows().
            query_tokens = set(tokenize(query))
            return {
                s: round(len(query_tokens & self.tokens[document][s]) / max(len(query_tokens), 1), 4) for s in school_ids
            }
        if retriever == "model2vec":
            query_vector = self.model.encode([query])[0]
            matrix = self.model_matrix[[self.model_index[s] for s in school_ids]]
            return {s: float(value) for s, value in zip(school_ids, matrix @ query_vector)}
        if retriever == "fts":
            # Same query text as production's _retrieve_candidates().
            return self.fulltext.get_fulltext_scores(
                " or ".join(tokenize(query)), {s: self.texts[document][s] for s in school_ids}
            )
        if retriever in RRF_COMPONENTS:
            fused = {s: 0.0 for s in school_ids}
            for component in RRF_COMPONENTS[retriever]:
                component_scores = self.score(component, document, query, school_ids)
                ordered = sorted(school_ids, key=lambda s: (-component_scores[s], s))
                for rank, s in enumerate(ordered, start=1):
                    fused[s] += 1.0 / (RRF_K + rank)
            return fused
        raise SystemExit(f"unknown retriever {retriever!r}")


class OfflineRepository:
    """Stands in for SchoolRepository so the real service runs without Postgres.

    Filters apply in memory through row_matches_filters, the mirror of _apply_filters. Full-text
    scoring delegates to the real repository when a database is connected; without one it
    raises, which sends the service onto its lexical fallback. Rows are keyed by unitid rather
    than the database serial id, so exact score ties could order differently than in the API.
    """

    def __init__(self, rows: list[dict[str, object]], fulltext: SchoolRepository | None) -> None:
        self.rows = rows
        self.fulltext = fulltext

    def get_semantic_document_rows(self, filters: SearchRequest | None = None) -> list[dict[str, object]]:
        return [row for row in self.rows if filters is None or row_matches_filters(row, filters)]

    def get_fulltext_scores(self, tsquery_text: str, documents: dict[int, str]) -> dict[int, float]:
        if self.fulltext is None:
            raise RuntimeError("no database connected")
        return self.fulltext.get_fulltext_scores(tsquery_text, documents)


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
) -> tuple[list[int], list[int], dict[int, float]]:
    """Returns the pool in similarity order, the final page, and fit scores."""
    filters = request.filters
    all_ids = sorted(rows_by_id)
    eligible = [s for s in all_ids if row_matches_filters(rows_by_id[s], filters)]
    candidates = eligible if config.filtering == "pre" else all_ids
    scores = scorer.score(config.retriever, config.document, request.query, candidates)
    nearest = sorted(candidates, key=lambda s: (-scores[s], s))[: request.candidate_limit]
    pool = nearest if config.filtering == "pre" else [s for s in nearest if row_matches_filters(rows_by_id[s], filters)]

    ranked = ranking.rank_rows([rows_by_id[s] for s in pool], merged_preferences(request))
    fit_order = [int(item.row["school_id"]) for item in ranked]
    fit = {int(item.row["school_id"]): item.fit_score for item in ranked}
    if config.ordering == "fit":
        final = fit_order
    elif config.ordering == "relevance":
        position = {s: index for index, s in enumerate(fit_order)}
        final = sorted(fit_order, key=lambda s: (-scores[s], position[s]))
    else:
        raise SystemExit(f"unknown ordering {config.ordering!r}")
    return pool, final[:TOP_K], fit


def verify_production_equivalence(rows, scorer, ranking, rows_by_id, queries, limits) -> int:
    """Fail loudly unless the production configurations reproduce the real service exactly."""
    services = {
        "fts": SemanticSearchService(OfflineRepository(rows, scorer.fulltext)),
        "lexical": SemanticSearchService(OfflineRepository(rows, None)),
    }
    checked = 0
    for config in (c for c in CONFIGS if c.production):
        if config.retriever in scorer.unavailable:
            print(f"production equivalence NOT checked for {config.name!r}: {scorer.unavailable[config.retriever]}")
            continue
        for limit in limits:
            for spec in queries:
                request = build_request(spec, limit)
                _, final, _ = run_pipeline(config, scorer, ranking, rows_by_id, request)
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


def evaluate(rows, queries, limits, repeats, scorer):
    rows_by_id = {int(row["school_id"]): row for row in rows}
    ranking = RankingService(OfflineRepository(rows, None))

    checked = verify_production_equivalence(rows, scorer, ranking, rows_by_id, queries, limits)
    print(f"production equivalence: {checked} query runs match the real SemanticSearchService exactly")

    results = []
    for config in CONFIGS:
        if config.retriever in scorer.unavailable:
            print(f"skipped {config.name!r}: {scorer.unavailable[config.retriever]}")
            continue
        for limit in limits:
            for spec in queries:
                request = build_request(spec, limit)
                relevant = {
                    s
                    for s, row in rows_by_id.items()
                    if row_matches_filters(row, request.filters) and is_relevant(row, spec["relevant_if"])
                }
                timings = []
                for _ in range(repeats):
                    started = time.perf_counter()
                    pool, final, fit = run_pipeline(config, scorer, ranking, rows_by_id, request)
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
        "| filtered queries empty | mean fit (page) | p50 / p95 ms |"
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
    parser.add_argument("--model2vec-path", type=Path, default=DEFAULT_MODEL2VEC_PATH)
    parser.add_argument("--no-fts", action="store_true", help="skip the Postgres full-text arm")
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env", override=False)
    rows = load_seed_rows(SEED_PATH)
    queries = json.loads(QUERIES_PATH.read_text(encoding="utf-8"))["queries"]

    # Every query must have at least one relevant school, or its precision is undefined and a
    # typo in a predicate would silently score as a retrieval failure.
    for query in queries:
        filters = SearchRequest(**query.get("filters", {}))
        if not any(row_matches_filters(row, filters) and is_relevant(row, query["relevant_if"]) for row in rows):
            raise SystemExit(f"query {query['id']!r} has no relevant schools; check its predicate")

    scorer = Scorer(rows, args.model2vec_path, None if args.no_fts else os.environ.get("DATABASE_URL"))
    counts = defaultdict(int)
    for query in queries:
        counts[query["category"]] += 1
    print(
        f"{len(queries)} queries over {len(rows)} schools; candidate limits {args.candidate_limits}; "
        f"RANKING_VERSION {RANKING_VERSION}, document {DOCUMENT_VERSION}"
    )
    print("queries per category:", dict(sorted(counts.items())))
    report(evaluate(rows, queries, args.candidate_limits, args.repeats, scorer), args.candidate_limits, args.per_query)


if __name__ == "__main__":
    sys.exit(main())
