from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol

from repositories.schools import SchoolRepository
from schemas.preferences import Preference
from schemas.semantic_search import SemanticSearchRequest, SemanticSearchResponse, SemanticSearchResult
from services.cache import CacheService, NullCacheBackend
from services.ranking_service import RANKING_VERSION, RankingService, RankedSchool, to_float, to_int


EMBEDDING_TYPE = "school_search_document"
LOCAL_EMBEDDING_MODEL = "local-hash-embedding-v1"
EMBEDDING_DIMENSIONS = 64
DOCUMENT_VERSION = "v2.2"
REASON_TAGS = (
    "major_match",
    "location_match",
    "setting_match",
    "cost_value_match",
    "outcomes_match",
    "campus_culture_match",
)


class EmbeddingProvider(Protocol):
    model: str

    def embed(self, text: str) -> list[float]:
        ...


@dataclass(frozen=True)
class SearchDocument:
    school_id: int
    text: str
    text_snapshot_hash: str


class LocalHashEmbeddingProvider:
    model = LOCAL_EMBEDDING_MODEL

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * EMBEDDING_DIMENSIONS
        tokens = tokenize(text)
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 8) for value in vector]


class SemanticSearchService:
    def __init__(
        self,
        repository: SchoolRepository,
        cache: CacheService | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.repository = repository
        self.cache = cache or CacheService(NullCacheBackend(), "v1", 300, 3600, 300)
        self.embedding_provider = embedding_provider or LocalHashEmbeddingProvider()
        self.ranking_service = RankingService(repository, cache)

    def refresh_embeddings(self) -> int:
        rows = self.repository.get_semantic_document_rows()
        refreshed = 0
        for row in rows:
            document = build_search_document(row)
            vector = self.embedding_provider.embed(document.text)
            self.repository.upsert_school_embedding(
                school_id=document.school_id,
                embedding_type=EMBEDDING_TYPE,
                embedding_model=self.embedding_provider.model,
                vector=vector,
                text_snapshot_hash=document.text_snapshot_hash,
            )
            refreshed += 1
        return refreshed

    def search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        cache_key = self.cache.make_key(
            "semantic-search",
            {
                "query": normalize_query(request.query),
                "filters": request.filters.model_dump(mode="json"),
                "preferences": request.preferences.model_dump(mode="json"),
                "embedding_model": self.embedding_provider.model,
                "embedding_type": EMBEDDING_TYPE,
                "candidate_limit": request.candidate_limit,
                "ranking_version": RANKING_VERSION,
            },
        )
        cached = self.cache.get_model(cache_key, SemanticSearchResponse)
        if cached is not None:
            return cached

        rows, retrieval_mode = self._retrieve_candidates(request)
        filtered_rows = [row for row in rows if row_matches_filters(row, request.filters)]
        ranked_rows = self.ranking_service.rank_rows(filtered_rows, merged_preferences(request))
        total_results = len(ranked_rows)
        start = (request.filters.page - 1) * request.filters.page_size
        end = start + request.filters.page_size
        response = SemanticSearchResponse(
            ranking_version=RANKING_VERSION,
            embedding_model=self.embedding_provider.model,
            embedding_type=EMBEDDING_TYPE,
            retrieval_mode=retrieval_mode,
            results=[
                to_semantic_result(ranked, float(ranked.row.get("semantic_score") or 0), request.query)
                for ranked in ranked_rows[start:end]
            ],
            page=request.filters.page,
            page_size=request.filters.page_size,
            total_results=total_results,
            has_next=end < total_results,
        )
        self.cache.set_model(cache_key, response, self.cache.search_ttl_seconds)
        return response

    def _retrieve_candidates(self, request: SemanticSearchRequest) -> tuple[list[dict[str, object]], str]:
        query_vector = self.embedding_provider.embed(request.query)
        try:
            rows = self.repository.get_vector_candidate_rows(
                query_vector=query_vector,
                embedding_type=EMBEDDING_TYPE,
                embedding_model=self.embedding_provider.model,
                limit=request.candidate_limit,
            )
        except Exception:
            rows = []
        if rows:
            return rows, "pgvector"
        fallback_rows = lexical_fallback_rows(
            self.repository.get_semantic_document_rows(),
            request.query,
            request.candidate_limit,
        )
        return fallback_rows, "deterministic_fallback"


def build_search_document(row: dict[str, object]) -> SearchDocument:
    school_id = int(row["school_id"])
    fields = [
        f"name: {row.get('name')}",
        f"location: {row.get('city')}, {row.get('state')} {row.get('region')}",
        f"type setting: {row.get('type')} {row.get('setting')}",
        f"majors programs: {join_values(row.get('top_majors'))}",
        cost_summary(row),
        outcome_summary(row),
        campus_summary(row),
        f"source attributes: {row.get('source_name')} {row.get('source_year')} {row.get('data_version')} {DOCUMENT_VERSION}",
    ]
    text = "\n".join(field for field in fields if field.strip())
    return SearchDocument(
        school_id=school_id,
        text=text,
        text_snapshot_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def lexical_fallback_rows(
    rows: Iterable[dict[str, object]],
    query: str,
    limit: int,
) -> list[dict[str, object]]:
    query_tokens = set(tokenize(query))
    scored: list[dict[str, object]] = []
    for row in rows:
        document = build_search_document(row)
        document_tokens = set(tokenize(document.text))
        score = len(query_tokens.intersection(document_tokens)) / max(len(query_tokens), 1)
        candidate = dict(row)
        candidate["semantic_score"] = round(score, 4)
        scored.append(candidate)
    return sorted(scored, key=lambda row: (-float(row["semantic_score"]), int(row["school_id"])))[:limit]


def to_semantic_result(ranked: RankedSchool, semantic_score: float, query: str) -> SemanticSearchResult:
    row = ranked.row
    return SemanticSearchResult(
        school_id=int(row["school_id"]),
        name=str(row["name"]),
        city=str(row["city"]),
        state=str(row["state"]),
        type=str(row["type"]),
        setting=str(row["setting"]),
        enrollment=to_int(row.get("enrollment")),
        acceptance_rate=to_float(row.get("acceptance_rate")),
        net_price=to_int(row.get("net_price")),
        graduation_rate=to_float(row.get("graduation_rate")),
        fit_score=ranked.fit_score,
        confidence_score=ranked.confidence_score,
        category_scores=ranked.category_scores,
        top_reasons=ranked.top_reasons,
        top_tradeoffs=ranked.top_tradeoffs,
        ranking_version=RANKING_VERSION,
        semantic_score=round(max(0.0, min(1.0, semantic_score)), 4),
        match_reasons=build_match_reasons(row, query),
    )


def build_match_reasons(row: dict[str, object], query: str) -> list[str]:
    tokens = set(tokenize(query))
    reasons: list[str] = []
    majors = set(tokenize(join_values(row.get("top_majors"))))
    culture_tags = set(tokenize(join_values(row.get("culture_tags"))))
    location_terms = set(tokenize(" ".join(str(row.get(key) or "") for key in ("city", "state", "region"))))
    setting_terms = set(tokenize(" ".join(str(row.get(key) or "") for key in ("type", "setting"))))
    if tokens.intersection(majors):
        reasons.append("major_match")
    if tokens.intersection(location_terms):
        reasons.append("location_match")
    if tokens.intersection(setting_terms) or tokens.intersection({"urban", "suburban", "rural", "town", "public", "private"}):
        reasons.append("setting_match")
    if tokens.intersection({"affordable", "cost", "cheap", "aid", "value", "tuition"}) and row.get("net_price") is not None:
        reasons.append("cost_value_match")
    if tokens.intersection({"outcome", "outcomes", "earnings", "graduation", "repayment", "career"}) and (
        row.get("median_earnings") is not None or row.get("graduation_rate") is not None
    ):
        reasons.append("outcomes_match")
    if tokens.intersection(culture_tags) or tokens.intersection({"campus", "culture", "residential", "athletics"}):
        reasons.append("campus_culture_match")
    if not reasons:
        if row.get("top_majors"):
            reasons.append("major_match")
        if row.get("state") or row.get("region"):
            reasons.append("location_match")
        if row.get("setting") or row.get("type"):
            reasons.append("setting_match")
        if row.get("net_price") is not None:
            reasons.append("cost_value_match")
        if row.get("median_earnings") is not None or row.get("graduation_rate") is not None:
            reasons.append("outcomes_match")
        if row.get("culture_tags"):
            reasons.append("campus_culture_match")
    return reasons[:6]


def row_matches_filters(row: dict[str, object], filters: object) -> bool:
    for key in ("state", "region", "type", "setting"):
        expected = getattr(filters, key)
        if expected and str(row.get(key) or "").lower() != str(expected).lower():
            return False
    if getattr(filters, "query") and str(filters.query).lower() not in str(row.get("name") or "").lower():
        return False
    range_checks = [
        ("min_enrollment", "enrollment", lambda actual, expected: actual >= expected),
        ("max_enrollment", "enrollment", lambda actual, expected: actual <= expected),
        ("min_net_price", "net_price", lambda actual, expected: actual >= expected),
        ("max_net_price", "net_price", lambda actual, expected: actual <= expected),
        ("min_acceptance_rate", "acceptance_rate", lambda actual, expected: actual >= expected),
        ("max_acceptance_rate", "acceptance_rate", lambda actual, expected: actual <= expected),
        ("min_graduation_rate", "graduation_rate", lambda actual, expected: actual >= expected),
        ("max_graduation_rate", "graduation_rate", lambda actual, expected: actual <= expected),
    ]
    for filter_name, row_name, predicate in range_checks:
        expected = getattr(filters, filter_name)
        actual = to_float(row.get(row_name))
        if expected is not None and (actual is None or not predicate(actual, expected)):
            return False
    return True


def merged_preferences(request: SemanticSearchRequest) -> Preference:
    constraints = dict(request.preferences.constraints)
    for key in ("state", "region", "setting", "type"):
        value = getattr(request.filters, key)
        if value:
            constraints.setdefault(
                {
                    "state": "preferred_states",
                    "region": "preferred_regions",
                    "setting": "preferred_settings",
                    "type": "preferred_school_types",
                }[key],
                [value],
            )
    if request.filters.max_net_price is not None and request.preferences.max_annual_cost is None:
        return request.preferences.model_copy(
            update={"max_annual_cost": request.filters.max_net_price, "constraints": constraints}
        )
    return request.preferences.model_copy(update={"constraints": constraints})


def cost_summary(row: dict[str, object]) -> str:
    values = []
    for label, key in (
        ("in-state tuition", "tuition_in_state"),
        ("out-of-state tuition", "tuition_out_state"),
        ("net price", "net_price"),
        ("average aid", "average_aid"),
        ("median debt", "debt_median"),
    ):
        if row.get(key) is not None:
            values.append(f"{label} {row[key]}")
    return "cost value affordability: " + ", ".join(values)


def outcome_summary(row: dict[str, object]) -> str:
    values = []
    if row.get("graduation_rate") is not None:
        values.append(f"graduation rate {rate_text(row['graduation_rate'])}")
    if row.get("retention_rate") is not None:
        values.append(f"retention rate {rate_text(row['retention_rate'])}")
    if row.get("median_earnings") is not None:
        values.append(f"median earnings {row['median_earnings']}")
    if row.get("repayment_rate") is not None:
        values.append(f"repayment rate {rate_text(row['repayment_rate'])}")
    return "cost outcomes career value: " + ", ".join(values)


def campus_summary(row: dict[str, object]) -> str:
    values = [
        f"housing {row.get('housing_available')}",
        f"sports {row.get('sports_division')}",
        f"greek life {rate_text(row.get('greek_life_rate'))}",
        f"culture tags {join_values(row.get('culture_tags'))}",
    ]
    return "campus culture: " + ", ".join(value for value in values if not value.endswith("None"))


def join_values(value: object) -> str:
    if isinstance(value, list | tuple | set):
        return ", ".join(str(item) for item in value)
    return str(value or "")


def rate_text(value: object) -> str:
    if isinstance(value, Decimal):
        return f"{float(value):.2f}"
    return str(value)


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1]


def normalize_query(query: str) -> str:
    return " ".join(tokenize(query))
