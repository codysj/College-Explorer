from __future__ import annotations

from dataclasses import dataclass

from repositories.schools import SchoolRepository
from schemas.preferences import Preference
from schemas.similar_schools import (
    SimilarSchoolResult,
    SimilarSchoolsRequest,
    SimilarSchoolsResponse,
    SimilarityVariant,
)
from services.cache import CacheService, NullCacheBackend
from services.ranking_service import RANKING_VERSION, RankingService, to_float, to_int
from services.semantic_search import (
    EMBEDDING_TYPE,
    LocalHashEmbeddingProvider,
    build_search_document,
    lexical_fallback_rows,
)


VARIANT_REASON_CODES = {
    "general": "similar_profile_match",
    "cheaper": "variant_lower_net_price",
    "less_selective": "variant_higher_acceptance_rate",
    "smaller": "variant_lower_enrollment",
    "stronger_outcomes": "variant_stronger_outcomes",
    "closer_to_home": "variant_home_state_match",
}


@dataclass(frozen=True)
class SimilarityScore:
    row: dict[str, object]
    score: float
    reasons: list[str]
    tradeoffs: list[str]


class SimilarSchoolsService:
    def __init__(
        self,
        repository: SchoolRepository,
        cache: CacheService | None = None,
        embedding_provider: LocalHashEmbeddingProvider | None = None,
    ) -> None:
        self.repository = repository
        self.cache = cache or CacheService(NullCacheBackend(), "v1", 300, 3600, 300)
        self.embedding_provider = embedding_provider or LocalHashEmbeddingProvider()
        self.ranking_service = RankingService(repository, cache)

    def get_similar_schools(self, school_id: int, request: SimilarSchoolsRequest) -> SimilarSchoolsResponse | None:
        cache_key = self.cache.make_key(
            "similar-schools",
            {
                "school_id": school_id,
                "variant": request.variant,
                "request": request.model_dump(mode="json"),
                "embedding_model": self.embedding_provider.model,
                "embedding_type": EMBEDDING_TYPE,
                "ranking_version": RANKING_VERSION,
            },
        )
        cached = self.cache.get_model(cache_key, SimilarSchoolsResponse)
        if cached is not None:
            return cached

        source = self.repository.get_school_profile_row(school_id)
        if source is None:
            return None
        source_row = profile_row_to_candidate_row(source)
        rows, retrieval_mode = self._retrieve_candidates(school_id, source_row, request)
        candidates = [
            row
            for row in rows
            if int(row["school_id"]) != school_id
            and row_matches_constraints(row, request)
            and row_matches_variant(source_row, row, request)
        ]
        scored = score_candidates(source_row, candidates, request)
        ranked = self._rank_scored_candidates(source_row, scored, request)
        total_results = len(ranked)
        start = (request.page - 1) * request.page_size
        end = start + request.page_size
        results = [
            self._to_result(item, source_row, request)
            for item in ranked[start:end]
        ]
        response = SimilarSchoolsResponse(
            source_school_id=school_id,
            variant=request.variant,
            variant_applied=request.variant,
            ranking_version=RANKING_VERSION,
            embedding_model=self.embedding_provider.model,
            embedding_type=EMBEDDING_TYPE,
            retrieval_mode=retrieval_mode,
            results=results,
            page=request.page,
            page_size=request.page_size,
            total_results=total_results,
            has_next=end < total_results,
        )
        self.cache.set_model(cache_key, response, self.cache.search_ttl_seconds)
        return response

    def _retrieve_candidates(
        self,
        school_id: int,
        source_row: dict[str, object],
        request: SimilarSchoolsRequest,
    ) -> tuple[list[dict[str, object]], str]:
        try:
            rows = self.repository.get_similar_vector_candidate_rows(
                school_id=school_id,
                embedding_type=EMBEDDING_TYPE,
                embedding_model=self.embedding_provider.model,
                limit=request.candidate_limit,
            )
        except Exception:
            rows = []
        if rows:
            return rows, "pgvector"

        documents = self.repository.get_semantic_document_rows()
        source_document = build_search_document(source_row).text
        return lexical_fallback_rows(documents, source_document, request.candidate_limit), "deterministic_fallback"

    def _rank_scored_candidates(
        self,
        source_row: dict[str, object],
        scored: list[SimilarityScore],
        request: SimilarSchoolsRequest,
    ) -> list[SimilarityScore]:
        preferences = source_like_preferences(source_row, request)
        ranked_by_id = {
            int(ranked.row["school_id"]): ranked
            for ranked in self.ranking_service.rank_rows([item.row for item in scored], preferences)
        }
        return sorted(
            scored,
            key=lambda item: (
                -item.score,
                -(ranked_by_id[int(item.row["school_id"])].fit_score if int(item.row["school_id"]) in ranked_by_id else 0),
                int(item.row["school_id"]),
            ),
        )

    def _to_result(
        self,
        item: SimilarityScore,
        source_row: dict[str, object],
        request: SimilarSchoolsRequest,
    ) -> SimilarSchoolResult:
        ranked = self.ranking_service.score_school(item.row, source_like_preferences(source_row, request))
        reasons = unique_codes([*item.reasons, *ranked.top_reasons])
        tradeoffs = unique_codes([*item.tradeoffs, *ranked.top_tradeoffs])
        return SimilarSchoolResult(
            school_id=int(item.row["school_id"]),
            name=str(item.row["name"]),
            city=str(item.row["city"]),
            state=str(item.row["state"]),
            type=str(item.row["type"]),
            setting=str(item.row["setting"]),
            enrollment=to_int(item.row.get("enrollment")),
            acceptance_rate=to_float(item.row.get("acceptance_rate")),
            net_price=to_int(item.row.get("net_price")),
            graduation_rate=to_float(item.row.get("graduation_rate")),
            median_earnings=to_int(item.row.get("median_earnings")),
            similarity_score=round(max(0.0, min(1.0, item.score)), 4),
            fit_score=ranked.fit_score,
            top_reasons=reasons[:4],
            top_tradeoffs=tradeoffs[:3],
            variant_applied=request.variant,
            ranking_version=RANKING_VERSION,
        )


def score_candidates(
    source: dict[str, object],
    candidates: list[dict[str, object]],
    request: SimilarSchoolsRequest,
) -> list[SimilarityScore]:
    scored = [score_candidate(source, candidate, request.variant, request.home_state) for candidate in candidates]
    return dedupe_candidates(scored)


def score_candidate(
    source: dict[str, object],
    candidate: dict[str, object],
    variant: SimilarityVariant,
    home_state: str | None = None,
) -> SimilarityScore:
    semantic_score = to_float(candidate.get("semantic_score"))
    base = semantic_score if semantic_score is not None else lexical_similarity(source, candidate)
    structural_score, structural_reasons = structural_similarity(source, candidate)
    variant_score, variant_reasons, variant_tradeoffs = variant_similarity(source, candidate, variant, home_state)
    score = round((base * 0.45) + (structural_score * 0.30) + (variant_score * 0.25), 4)
    reasons = unique_codes([*structural_reasons, *variant_reasons, VARIANT_REASON_CODES[variant]])
    return SimilarityScore(row=candidate, score=score, reasons=reasons, tradeoffs=variant_tradeoffs)


def row_matches_variant(source: dict[str, object], candidate: dict[str, object], request: SimilarSchoolsRequest) -> bool:
    variant = request.variant
    if variant == "cheaper":
        source_price = to_int(source.get("net_price"))
        candidate_price = to_int(candidate.get("net_price"))
        return source_price is None or candidate_price is None or candidate_price < source_price
    if variant == "less_selective":
        source_rate = to_float(source.get("acceptance_rate"))
        candidate_rate = to_float(candidate.get("acceptance_rate"))
        return source_rate is None or candidate_rate is None or candidate_rate > source_rate
    if variant == "smaller":
        source_enrollment = to_int(source.get("enrollment"))
        candidate_enrollment = to_int(candidate.get("enrollment"))
        return source_enrollment is None or candidate_enrollment is None or candidate_enrollment < source_enrollment
    if variant == "stronger_outcomes":
        source_grad = to_float(source.get("graduation_rate"))
        candidate_grad = to_float(candidate.get("graduation_rate"))
        source_earnings = to_int(source.get("median_earnings"))
        candidate_earnings = to_int(candidate.get("median_earnings"))
        grad_improved = source_grad is not None and candidate_grad is not None and candidate_grad > source_grad
        earnings_improved = source_earnings is not None and candidate_earnings is not None and candidate_earnings > source_earnings
        return grad_improved or earnings_improved or (source_grad is None and source_earnings is None)
    if variant == "closer_to_home" and request.home_state:
        return str(candidate.get("state") or "").upper() == request.home_state.upper()
    return True


def row_matches_constraints(row: dict[str, object], request: SimilarSchoolsRequest) -> bool:
    for key in ("state", "region", "type", "setting"):
        expected = getattr(request, key)
        if expected and str(row.get(key) or "").lower() != str(expected).lower():
            return False
    checks = [
        ("min_net_price", "net_price", lambda actual, expected: actual >= expected),
        ("max_net_price", "net_price", lambda actual, expected: actual <= expected),
        ("min_acceptance_rate", "acceptance_rate", lambda actual, expected: actual >= expected),
        ("max_acceptance_rate", "acceptance_rate", lambda actual, expected: actual <= expected),
        ("min_graduation_rate", "graduation_rate", lambda actual, expected: actual >= expected),
        ("min_enrollment", "enrollment", lambda actual, expected: actual >= expected),
        ("max_enrollment", "enrollment", lambda actual, expected: actual <= expected),
    ]
    for request_key, row_key, predicate in checks:
        expected = getattr(request, request_key)
        actual = to_float(row.get(row_key))
        if expected is not None and (actual is None or not predicate(actual, expected)):
            return False
    return True


def structural_similarity(source: dict[str, object], candidate: dict[str, object]) -> tuple[float, list[str]]:
    components: list[float] = []
    reasons: list[str] = []
    if source.get("type") and source.get("type") == candidate.get("type"):
        components.append(1.0)
        reasons.append("same_school_type")
    if source.get("setting") and source.get("setting") == candidate.get("setting"):
        components.append(1.0)
        reasons.append("same_setting")
    if source.get("region") and source.get("region") == candidate.get("region"):
        components.append(1.0)
        reasons.append("same_region")
    majors_overlap = overlap_ratio(source.get("top_majors"), candidate.get("top_majors"))
    if majors_overlap > 0:
        components.append(majors_overlap)
        reasons.append("overlapping_majors")
    culture_overlap = overlap_ratio(source.get("culture_tags"), candidate.get("culture_tags"))
    if culture_overlap > 0:
        components.append(culture_overlap)
        reasons.append("similar_campus_culture")
    return (sum(components) / len(components), reasons) if components else (0.5, ["structured_profile_available"])


def variant_similarity(
    source: dict[str, object],
    candidate: dict[str, object],
    variant: SimilarityVariant,
    home_state: str | None,
) -> tuple[float, list[str], list[str]]:
    if variant == "cheaper":
        return lower_is_better_score(source, candidate, "net_price", "lower_net_price")
    if variant == "less_selective":
        return higher_is_better_score(source, candidate, "acceptance_rate", "higher_acceptance_rate")
    if variant == "smaller":
        return lower_is_better_score(source, candidate, "enrollment", "lower_enrollment")
    if variant == "stronger_outcomes":
        grad_score, grad_reasons, grad_tradeoffs = higher_is_better_score(source, candidate, "graduation_rate", "higher_graduation_rate")
        earnings_score, earnings_reasons, earnings_tradeoffs = higher_is_better_score(source, candidate, "median_earnings", "higher_earnings")
        return max(grad_score, earnings_score), unique_codes([*grad_reasons, *earnings_reasons]), unique_codes([*grad_tradeoffs, *earnings_tradeoffs])
    if variant == "closer_to_home" and home_state:
        if str(candidate.get("state") or "").upper() == home_state.upper():
            return 1.0, ["home_state_match"], []
        return 0.2, [], ["not_in_home_state"]
    return 0.75, ["similar_structured_profile"], []


def lower_is_better_score(
    source: dict[str, object],
    candidate: dict[str, object],
    key: str,
    reason: str,
) -> tuple[float, list[str], list[str]]:
    source_value = to_float(source.get(key))
    candidate_value = to_float(candidate.get(key))
    if source_value is None or candidate_value is None:
        return 0.5, [], [f"{reason}_unknown"]
    if candidate_value < source_value:
        improvement = min((source_value - candidate_value) / max(source_value, 1), 1)
        return 0.75 + improvement * 0.25, [reason], []
    return 0.1, [], [f"{reason}_not_met"]


def higher_is_better_score(
    source: dict[str, object],
    candidate: dict[str, object],
    key: str,
    reason: str,
) -> tuple[float, list[str], list[str]]:
    source_value = to_float(source.get(key))
    candidate_value = to_float(candidate.get(key))
    if source_value is None or candidate_value is None:
        return 0.5, [], [f"{reason}_unknown"]
    if candidate_value > source_value:
        improvement = min((candidate_value - source_value) / max(abs(source_value), 0.01), 1)
        return 0.75 + improvement * 0.25, [reason], []
    return 0.1, [], [f"{reason}_not_met"]


def source_like_preferences(source: dict[str, object], request: SimilarSchoolsRequest) -> Preference:
    majors = source.get("top_majors") if isinstance(source.get("top_majors"), list) else []
    constraints: dict[str, object] = {
        "preferred_regions": [source.get("region")] if source.get("region") else [],
        "preferred_settings": [source.get("setting")] if source.get("setting") else [],
        "preferred_school_types": [source.get("type")] if source.get("type") else [],
    }
    if request.home_state:
        constraints["preferred_states"] = [request.home_state]
    weights = {"academic": 0.28, "career": 0.22, "campus": 0.18, "cost": 0.16, "location": 0.10, "admissions_realism": 0.06}
    if request.variant == "cheaper":
        weights = {"cost": 0.45, "academic": 0.20, "career": 0.15, "campus": 0.10, "location": 0.05, "admissions_realism": 0.05}
    elif request.variant == "stronger_outcomes":
        weights = {"career": 0.40, "academic": 0.25, "cost": 0.12, "campus": 0.10, "location": 0.08, "admissions_realism": 0.05}
    elif request.variant == "closer_to_home":
        weights = {"location": 0.40, "academic": 0.22, "career": 0.16, "cost": 0.10, "campus": 0.08, "admissions_realism": 0.04}
    return Preference(
        intended_major=str(majors[0]) if majors else None,
        home_state=request.home_state,
        max_annual_cost=to_int(source.get("net_price")),
        weights=weights,
        constraints=constraints,
    )


def profile_row_to_candidate_row(row: dict[str, object]) -> dict[str, object]:
    return {
        **row,
        "source_name": "profile",
        "source_year": "",
        "data_version": "",
    }


def lexical_similarity(source: dict[str, object], candidate: dict[str, object]) -> float:
    source_tokens = set(build_search_document(source).text.lower().split())
    candidate_tokens = set(build_search_document(candidate).text.lower().split())
    if not source_tokens:
        return 0.0
    return len(source_tokens.intersection(candidate_tokens)) / len(source_tokens)


def overlap_ratio(left: object, right: object) -> float:
    if not isinstance(left, list) or not isinstance(right, list) or not left:
        return 0.0
    left_set = {str(item).strip().lower() for item in left if str(item).strip()}
    right_set = {str(item).strip().lower() for item in right if str(item).strip()}
    return len(left_set.intersection(right_set)) / max(len(left_set), 1)


def dedupe_candidates(scored: list[SimilarityScore]) -> list[SimilarityScore]:
    seen: set[tuple[str, str, str]] = set()
    result: list[SimilarityScore] = []
    for item in sorted(scored, key=lambda candidate: (-candidate.score, int(candidate.row["school_id"]))):
        key = (
            str(item.row.get("name") or "").strip().lower(),
            str(item.row.get("city") or "").strip().lower(),
            str(item.row.get("state") or "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def unique_codes(codes: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for code in codes:
        if code and code not in seen:
            seen.add(code)
            result.append(code)
    return result
