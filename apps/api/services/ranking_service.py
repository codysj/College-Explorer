from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from repositories.schools import SchoolRepository
from schemas.preferences import Preference
from schemas.rankings import RankingRequest, RankingResponse
from schemas.schools import SchoolSearchResult


RANKING_VERSION = "v1.0"
CATEGORY_KEYS = (
    "academic",
    "cost",
    "career",
    "location",
    "campus",
    "admissions_realism",
)
DEFAULT_WEIGHTS = {
    "academic": 0.20,
    "cost": 0.20,
    "career": 0.18,
    "location": 0.14,
    "campus": 0.14,
    "admissions_realism": 0.14,
}
WEIGHT_ALIASES = {
    "academics": "academic",
    "academic_fit": "academic",
    "cost_fit": "cost",
    "career_fit": "career",
    "location_fit": "location",
    "campus_fit": "campus",
    "campus_lifestyle": "campus",
    "campus_lifestyle_fit": "campus",
    "admissions": "admissions_realism",
    "admissions_fit": "admissions_realism",
    "admissions_realism_fit": "admissions_realism",
}


@dataclass(frozen=True)
class CategoryScore:
    score: float
    confidence: float
    reason_code: str
    tradeoff_code: str


@dataclass(frozen=True)
class RankedSchool:
    row: dict[str, object]
    fit_score: float
    confidence_score: float
    category_scores: dict[str, float]
    top_reasons: list[str]
    top_tradeoffs: list[str]


class RankingService:
    def __init__(self, repository: SchoolRepository) -> None:
        self.repository = repository

    def rank_schools(self, request: RankingRequest) -> RankingResponse:
        rows = self.repository.get_ranking_candidate_rows(request.filters)
        ranked_rows = self.rank_rows(rows, request.preferences)
        total_results = len(ranked_rows)
        start = (request.filters.page - 1) * request.filters.page_size
        end = start + request.filters.page_size

        return RankingResponse(
            ranking_version=RANKING_VERSION,
            results=[self._to_search_result(ranked) for ranked in ranked_rows[start:end]],
            page=request.filters.page,
            page_size=request.filters.page_size,
            total_results=total_results,
            has_next=end < total_results,
        )

    def rank_rows(self, rows: Iterable[dict[str, object]], preferences: Preference) -> list[RankedSchool]:
        weights = normalize_weights(preferences.weights)
        ranked: list[RankedSchool] = []
        for row in rows:
            if self.violates_hard_constraints(row, preferences):
                continue
            ranked.append(self.score_school(row, preferences, weights))

        return sorted(
            ranked,
            key=lambda school: (-school.fit_score, -school.confidence_score, int(school.row["school_id"])),
        )

    def score_school(
        self,
        row: dict[str, object],
        preferences: Preference,
        weights: dict[str, float] | None = None,
    ) -> RankedSchool:
        applied_weights = weights or normalize_weights(preferences.weights)
        categories = {
            "academic": self.score_academic_fit(row, preferences),
            "cost": self.score_cost_fit(row, preferences),
            "career": self.score_career_fit(row, preferences),
            "location": self.score_location_fit(row, preferences),
            "campus": self.score_campus_lifestyle_fit(row, preferences),
            "admissions_realism": self.score_admissions_realism(row, preferences),
        }
        category_scores = {
            key: round(value.score, 2)
            for key, value in categories.items()
        }
        fit_score = round(
            sum(categories[key].score * applied_weights[key] for key in CATEGORY_KEYS),
            2,
        )
        confidence_score = round(
            sum(categories[key].confidence * applied_weights[key] for key in CATEGORY_KEYS),
            4,
        )
        top_reasons, top_tradeoffs = build_explanations(categories, applied_weights)
        return RankedSchool(
            row=row,
            fit_score=fit_score,
            confidence_score=confidence_score,
            category_scores=category_scores,
            top_reasons=top_reasons,
            top_tradeoffs=top_tradeoffs,
        )

    def violates_hard_constraints(self, row: dict[str, object], preferences: Preference) -> bool:
        major_terms = preference_terms(preferences)
        school_majors = normalized_list(row.get("top_majors"))
        if constraint_enabled(preferences, "major") and major_terms and school_majors:
            if not intersects(major_terms, school_majors):
                return True

        max_cost = preferences.max_annual_cost
        net_price = to_int(row.get("net_price"))
        if constraint_enabled(preferences, "cost") and max_cost is not None and net_price is not None:
            if net_price > max_cost:
                return True

        if constraint_enabled(preferences, "state"):
            preferred_states = constraint_values(preferences, "preferred_states", "preferred_state", "state")
            if preferred_states and normalize_text(row.get("state")) not in preferred_states:
                return True

        if constraint_enabled(preferences, "region"):
            preferred_regions = constraint_values(preferences, "preferred_regions", "preferred_region", "region")
            if preferred_regions and normalize_text(row.get("region")) not in preferred_regions:
                return True

        if constraint_enabled(preferences, "setting"):
            preferred_settings = constraint_values(preferences, "preferred_settings", "preferred_setting", "setting")
            if preferred_settings and normalize_text(row.get("setting")) not in preferred_settings:
                return True

        if constraint_enabled(preferences, "school_type"):
            preferred_types = constraint_values(
                preferences,
                "preferred_school_types",
                "preferred_school_type",
                "school_type",
                "type",
            )
            if preferred_types and normalize_text(row.get("type")) not in preferred_types:
                return True

        return False

    def score_academic_fit(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        major_terms = preference_terms(preferences)
        school_majors = normalized_list(row.get("top_majors"))
        components: list[tuple[float, float]] = []
        reason_code = "academic_profile_available"
        tradeoff_code = "academic_profile_limited"

        if major_terms and school_majors:
            major_score = 100.0 if intersects(major_terms, school_majors) else 42.0
            components.append((major_score, 0.40))
            if major_score == 100.0:
                reason_code = "academic_major_match"
            else:
                tradeoff_code = "academic_major_not_listed"
        elif school_majors:
            components.append((70.0, 0.20))
            reason_code = "academic_programs_known"

        graduation_rate = to_rate(row.get("graduation_rate"))
        if graduation_rate is not None:
            components.append((graduation_rate * 100, 0.25))
            if graduation_rate >= 0.75 and reason_code == "academic_profile_available":
                reason_code = "academic_strong_graduation_rate"
            if graduation_rate < 0.60:
                tradeoff_code = "academic_lower_graduation_rate"

        retention_rate = to_rate(row.get("retention_rate"))
        if retention_rate is not None:
            components.append((retention_rate * 100, 0.25))
            if retention_rate >= 0.85 and reason_code == "academic_profile_available":
                reason_code = "academic_strong_retention_rate"
            if retention_rate < 0.70:
                tradeoff_code = "academic_lower_retention_rate"

        ratio = to_float(row.get("student_faculty_ratio"))
        if ratio is not None:
            faculty_score = clamp(100 - max(ratio - 10, 0) * 4, 25, 100)
            components.append((faculty_score, 0.10))
            if faculty_score >= 85 and reason_code == "academic_profile_available":
                reason_code = "academic_small_classes"

        return category_result(components, reason_code, tradeoff_code)

    def score_cost_fit(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        components: list[tuple[float, float]] = []
        reason_code = "cost_profile_available"
        tradeoff_code = "cost_profile_limited"
        net_price = to_int(row.get("net_price"))
        max_cost = preferences.max_annual_cost

        if net_price is not None and max_cost is not None and max_cost > 0:
            budget_score = 100.0 if net_price <= max_cost else clamp(100 - ((net_price - max_cost) / max_cost) * 200, 0, 100)
            components.append((budget_score, 0.50))
            if net_price <= max_cost:
                reason_code = "cost_within_budget"
            else:
                tradeoff_code = "cost_above_budget"
        elif net_price is not None:
            affordability = clamp(100 - ((net_price - 15000) / 30000) * 65, 35, 100)
            components.append((affordability, 0.35))
            if affordability >= 80:
                reason_code = "cost_lower_net_price"

        average_aid = to_int(row.get("average_aid"))
        tuition = to_int(row.get("tuition_out_state")) or to_int(row.get("tuition_in_state"))
        aid_importance = normalize_text(preferences.constraints.get("aid_importance"))
        if average_aid is not None and tuition is not None and tuition > 0:
            aid_ratio = average_aid / tuition
            aid_weight = 0.25 if aid_importance == "high" else 0.15
            components.append((clamp(aid_ratio * 220, 0, 100), aid_weight))
            if aid_ratio >= 0.45 and reason_code == "cost_profile_available":
                reason_code = "cost_strong_aid"

        debt = to_int(row.get("debt_median"))
        if debt is not None:
            debt_score = clamp(100 - ((debt - 18000) / 22000) * 70, 30, 100)
            components.append((debt_score, 0.20))
            if debt > 30000:
                tradeoff_code = "cost_higher_median_debt"

        return category_result(components, reason_code, tradeoff_code)

    def score_career_fit(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        components: list[tuple[float, float]] = []
        reason_code = "career_profile_available"
        tradeoff_code = "career_profile_limited"

        earnings = to_int(row.get("median_earnings"))
        if earnings is not None:
            earnings_score = clamp(40 + ((earnings - 40000) / 40000) * 60, 20, 100)
            components.append((earnings_score, 0.55))
            if earnings >= 65000:
                reason_code = "career_strong_earnings"
            if earnings < 48000:
                tradeoff_code = "career_lower_earnings"

        repayment_rate = to_rate(row.get("repayment_rate"))
        if repayment_rate is not None:
            components.append((repayment_rate * 100, 0.25))
            if repayment_rate >= 0.80 and reason_code == "career_profile_available":
                reason_code = "career_strong_repayment_rate"

        priorities = constraint_values(preferences, "career_priorities", "career_priority")
        culture_tags = normalized_list(row.get("culture_tags"))
        if priorities and culture_tags:
            match_score = priority_tag_score(priorities, culture_tags)
            components.append((match_score, 0.20))
            if match_score >= 80 and reason_code == "career_profile_available":
                reason_code = "career_priority_match"
            if match_score < 50:
                tradeoff_code = "career_priorities_less_visible"
        elif culture_tags:
            components.append((70.0, 0.10))

        return category_result(components, reason_code, tradeoff_code)

    def score_location_fit(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        preferred_states = constraint_values(preferences, "preferred_states", "preferred_state", "state")
        preferred_regions = constraint_values(preferences, "preferred_regions", "preferred_region", "region")
        home_state = normalize_text(preferences.home_state)
        school_state = normalize_text(row.get("state"))
        school_region = normalize_text(row.get("region"))
        components: list[tuple[float, float]] = []
        reason_code = "location_profile_available"
        tradeoff_code = "location_preference_not_matched"

        if preferred_states:
            state_score = 100.0 if school_state in preferred_states else 45.0
            components.append((state_score, 0.55))
            if state_score == 100.0:
                reason_code = "location_preferred_state"
        elif home_state:
            state_score = 90.0 if school_state == home_state else 60.0
            components.append((state_score, 0.35))
            if state_score == 90.0:
                reason_code = "location_home_state"

        if preferred_regions:
            region_score = 95.0 if school_region in preferred_regions else 50.0
            components.append((region_score, 0.45))
            if region_score == 95.0 and reason_code == "location_profile_available":
                reason_code = "location_preferred_region"

        if not components and (school_state or school_region):
            components.append((70.0, 0.25))
            tradeoff_code = "location_no_preference"

        return category_result(components, reason_code, tradeoff_code)

    def score_campus_lifestyle_fit(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        components: list[tuple[float, float]] = []
        reason_code = "campus_profile_available"
        tradeoff_code = "campus_preference_not_matched"
        preferred_settings = constraint_values(preferences, "preferred_settings", "preferred_setting", "setting")
        preferred_types = constraint_values(preferences, "preferred_school_types", "preferred_school_type", "school_type", "type")
        campus_preferences = constraint_values(preferences, "campus_preferences", "campus_preference")
        culture_tags = normalized_list(row.get("culture_tags"))
        school_setting = normalize_text(row.get("setting"))
        school_type = normalize_text(row.get("type"))

        if preferred_settings:
            setting_score = 100.0 if school_setting in preferred_settings else 50.0
            components.append((setting_score, 0.30))
            if setting_score == 100.0:
                reason_code = "campus_preferred_setting"

        if preferred_types:
            type_score = 95.0 if school_type in preferred_types else 55.0
            components.append((type_score, 0.20))
            if type_score == 95.0 and reason_code == "campus_profile_available":
                reason_code = "campus_preferred_school_type"

        if campus_preferences:
            preference_score = campus_preference_score(campus_preferences, row, culture_tags)
            components.append((preference_score, 0.35))
            if preference_score >= 80 and reason_code == "campus_profile_available":
                reason_code = "campus_lifestyle_match"
            if preference_score < 55:
                tradeoff_code = "campus_lifestyle_less_visible"
        elif culture_tags:
            components.append((70.0, 0.10))

        greek_life = to_rate(row.get("greek_life_rate"))
        if greek_life is not None:
            components.append((clamp(100 - abs(greek_life - 0.12) * 180, 55, 100), 0.10))

        housing = row.get("housing_available")
        if housing is not None and "residential" in campus_preferences:
            components.append((100.0 if bool(housing) else 30.0, 0.15))

        return category_result(components, reason_code, tradeoff_code)

    def score_admissions_realism(self, row: dict[str, object], preferences: Preference) -> CategoryScore:
        acceptance_rate = to_rate(row.get("acceptance_rate"))
        if acceptance_rate is None:
            return CategoryScore(
                score=50.0,
                confidence=0.0,
                reason_code="admissions_data_missing",
                tradeoff_code="admissions_data_missing",
            )

        strategy = normalize_text(preferences.constraints.get("admissions_strategy")) or "balanced"
        target_min = to_rate(preferences.constraints.get("target_acceptance_rate_min"))
        components: list[tuple[float, float]] = []
        reason_code = "admissions_balanced_selectivity"
        tradeoff_code = "admissions_more_selective_than_target"

        if strategy == "likely":
            strategy_score = clamp((acceptance_rate / 0.75) * 100, 35, 100)
            reason_code = "admissions_likely_option" if acceptance_rate >= 0.60 else reason_code
        elif strategy == "reach":
            strategy_score = clamp(100 - abs(acceptance_rate - 0.35) * 150, 45, 100)
            reason_code = "admissions_reach_aligned" if acceptance_rate <= 0.45 else reason_code
            tradeoff_code = "admissions_less_selective_than_reach_preference"
        else:
            strategy_score = clamp(100 - abs(acceptance_rate - 0.55) * 120, 45, 100)
            reason_code = "admissions_balanced_selectivity" if 0.35 <= acceptance_rate <= 0.75 else reason_code

        components.append((strategy_score, 0.65))

        if target_min is not None:
            target_score = 95.0 if acceptance_rate >= target_min else clamp(95 - ((target_min - acceptance_rate) / max(target_min, 0.01)) * 110, 20, 95)
            components.append((target_score, 0.35))
            if target_score == 95.0:
                reason_code = "admissions_meets_acceptance_comfort"
            else:
                tradeoff_code = "admissions_below_acceptance_comfort"

        return category_result(components, reason_code, tradeoff_code)

    def _to_search_result(self, ranked: RankedSchool) -> SchoolSearchResult:
        row = ranked.row
        return SchoolSearchResult(
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
        )


def normalize_weights(weights: dict[str, float] | None) -> dict[str, float]:
    if not weights:
        return DEFAULT_WEIGHTS.copy()

    normalized = {key: 0.0 for key in CATEGORY_KEYS}
    for raw_key, raw_value in weights.items():
        key = WEIGHT_ALIASES.get(raw_key, raw_key)
        if key not in normalized:
            continue
        value = to_float(raw_value)
        if value is not None and value > 0:
            normalized[key] += value

    total = sum(normalized.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {key: normalized[key] / total for key in CATEGORY_KEYS}


def build_explanations(
    categories: dict[str, CategoryScore],
    weights: dict[str, float],
) -> tuple[list[str], list[str]]:
    reason_candidates = sorted(
        (
            (categories[key].score * weights[key], key, categories[key].reason_code)
            for key in CATEGORY_KEYS
            if weights[key] > 0 and categories[key].confidence > 0 and categories[key].score >= 72
        ),
        key=lambda item: (-item[0], item[1]),
    )
    tradeoff_candidates = sorted(
        (
            ((100 - categories[key].score) * weights[key], key, categories[key].tradeoff_code)
            for key in CATEGORY_KEYS
            if weights[key] > 0 and (categories[key].confidence < 0.5 or categories[key].score < 68)
        ),
        key=lambda item: (-item[0], item[1]),
    )
    if not reason_candidates:
        reason_candidates = sorted(
            (
                (categories[key].score * weights[key], key, categories[key].reason_code)
                for key in CATEGORY_KEYS
                if weights[key] > 0 and categories[key].confidence > 0
            ),
            key=lambda item: (-item[0], item[1]),
        )

    return (
        unique_codes(item[2] for item in reason_candidates[:3]),
        unique_codes(item[2] for item in tradeoff_candidates[:2]),
    )


def category_result(
    components: list[tuple[float, float]],
    reason_code: str,
    tradeoff_code: str,
) -> CategoryScore:
    if not components:
        return CategoryScore(
            score=50.0,
            confidence=0.0,
            reason_code=f"{reason_code}_missing",
            tradeoff_code=tradeoff_code,
        )
    total_weight = sum(weight for _, weight in components)
    score = sum(score * weight for score, weight in components) / total_weight
    return CategoryScore(
        score=round(clamp(score, 0, 100), 2),
        confidence=round(clamp(total_weight, 0, 1), 4),
        reason_code=reason_code,
        tradeoff_code=tradeoff_code,
    )


def preference_terms(preferences: Preference) -> list[str]:
    terms: list[str] = []
    if preferences.intended_major:
        terms.append(preferences.intended_major)
    terms.extend(constraint_values(preferences, "academic_interests", "preferred_majors", "intended_majors"))
    return normalized_list(terms)


def constraint_enabled(preferences: Preference, name: str) -> bool:
    constraints = preferences.constraints
    bool_keys = (
        f"strict_{name}",
        f"{name}_strict",
        f"require_{name}",
    )
    for key in bool_keys:
        value = constraints.get(key)
        if isinstance(value, bool):
            return value
    strict_constraints = constraints.get("strict_constraints")
    return name in normalized_list(strict_constraints)


def constraint_values(preferences: Preference, *keys: str) -> list[str]:
    values: list[object] = []
    for key in keys:
        if key in preferences.constraints:
            values.append(preferences.constraints[key])
    return normalized_list(values)


def normalized_list(value: object) -> list[str]:
    if value is None:
        return []
    raw_values: list[str] = []

    def collect(item: object) -> None:
        if item is None:
            return
        if isinstance(item, str):
            raw_values.extend(part.strip() for part in item.replace("|", ",").split(","))
            return
        if isinstance(item, list | tuple | set):
            for nested_item in item:
                collect(nested_item)
            return
        raw_values.append(str(item))

    collect(value)
    return [normalized for item in raw_values if (normalized := normalize_text(item))]


def normalize_text(value: object) -> str:
    return str(value).strip().lower() if value is not None else ""


def intersects(left: list[str], right: list[str]) -> bool:
    right_values = set(right)
    return any(item in right_values for item in left)


def to_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str) and value.strip():
        return float(value)
    return None


def to_int(value: object) -> int | None:
    number = to_float(value)
    return int(number) if number is not None else None


def to_rate(value: object) -> float | None:
    number = to_float(value)
    if number is None:
        return None
    if number > 1:
        number = number / 100
    return clamp(number, 0, 1)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def priority_tag_score(priorities: list[str], culture_tags: list[str]) -> float:
    mappings = {
        "high earnings": {"career-focused", "technical", "business"},
        "graduate school": {"research", "liberal-arts", "small-classes"},
        "internships": {"career-focused", "urban", "technical"},
        "research": {"research", "technical"},
        "public service": {"public-service", "education", "health"},
        "local jobs": {"career-focused", "commuter-friendly", "urban"},
    }
    score = 0
    for priority in priorities:
        desired = mappings.get(priority, {priority})
        if desired.intersection(culture_tags):
            score += 1
    return 100.0 if not priorities else (score / len(priorities)) * 100


def campus_preference_score(
    preferences: list[str],
    row: dict[str, object],
    culture_tags: list[str],
) -> float:
    matches = 0
    housing = row.get("housing_available")
    sports = normalize_text(row.get("sports_division"))
    greek_life = to_rate(row.get("greek_life_rate"))
    for preference in preferences:
        if preference == "residential" and housing is True:
            matches += 1
        elif preference == "commuter-friendly" and "commuter-friendly" in culture_tags:
            matches += 1
        elif preference == "athletics" and sports in {"di", "dii"}:
            matches += 1
        elif preference == "greek life" and greek_life is not None and greek_life >= 0.12:
            matches += 1
        elif preference == "diverse community" and "diverse" in culture_tags:
            matches += 1
        elif preference == "small classes" and "small-classes" in culture_tags:
            matches += 1
        elif preference in culture_tags:
            matches += 1
    return 100.0 if not preferences else (matches / len(preferences)) * 100


def unique_codes(codes: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for code in codes:
        if code not in seen:
            result.append(code)
            seen.add(code)
    return result
