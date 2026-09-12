from __future__ import annotations

from statistics import mean

from repositories.schools import SchoolRepository
from schemas.preferences import Preference
from schemas.sensitivity import (
    SensitivityCategoryDriver,
    SensitivityChoiceSummary,
    SensitivityConfidenceImpact,
    SensitivityRequest,
    SensitivityResponse,
    SensitivityScenario,
    SensitivityScenarioResult,
    SensitivitySchoolMovement,
)
from services.cache import CacheService, NullCacheBackend
from services.ranking_service import CATEGORY_KEYS, RANKING_VERSION, RankedSchool, RankingService, normalize_weights


DIMENSION_ALIASES = {
    "academic_fit": "academic",
    "cost_value": "cost",
    "career_outcomes": "career",
    "campus_lifestyle": "campus",
    "prestige_selectivity": "admissions_realism",
}

STABLE_DEFINITION = "A stable choice remains highly ranked across many weighting scenarios, with little rank movement."
VOLATILE_DEFINITION = "A volatile choice changes rank dramatically when one preference changes."


class SensitivityService:
    def __init__(self, repository: SchoolRepository, cache: CacheService | None = None) -> None:
        self.repository = repository
        self.cache = cache or CacheService(NullCacheBackend(), "v1", 300, 3600, 300)
        self.ranking_service = RankingService(repository, cache)

    def analyze(self, request: SensitivityRequest) -> SensitivityResponse:
        cache_key = self.cache.make_key(
            "sensitivity",
            {
                "request": request.model_dump(mode="json"),
                "profile_snapshot": self._profile_snapshot(request.preferences),
                "ranking_version": RANKING_VERSION,
            },
            version=RANKING_VERSION,
        )
        cached = self.cache.get_model(cache_key, SensitivityResponse)
        if cached is not None:
            return cached

        rows = self._candidate_rows(request)
        baseline_weights = normalize_weights(request.preferences.weights)
        baseline_ranked = self.ranking_service.rank_rows(rows, request.preferences)
        baseline_positions = positions_by_school(baseline_ranked)
        baseline_results = [
            self._movement(
                ranked,
                base=ranked,
                base_rank=index + 1,
                scenario_rank=index + 1,
                all_scenario_deltas=[],
                all_fit_deltas=[],
                base_weights=baseline_weights,
                scenario_weights=baseline_weights,
            )
            for index, ranked in enumerate(baseline_ranked)
        ]

        scenario_rankings: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]] = []
        for scenario in request.scenarios:
            applied_weights, emphasis = scenario_weights(baseline_weights, scenario)
            preferences = scenario_preferences(request.preferences, applied_weights, scenario)
            ranked = self.ranking_service.rank_rows(rows, preferences)
            scenario_rankings.append((scenario, applied_weights, ranked, emphasis))

        deltas_by_school: dict[int, list[int]] = {}
        fit_deltas_by_school: dict[int, list[float]] = {}
        for _, _, ranked, _ in scenario_rankings:
            scenario_positions = positions_by_school(ranked)
            ranked_by_id = {int(item.row["school_id"]): item for item in ranked}
            for school_id, base_rank in baseline_positions.items():
                scenario_rank = scenario_positions.get(school_id)
                if scenario_rank is None:
                    continue
                deltas_by_school.setdefault(school_id, []).append(base_rank - scenario_rank)
                base = baseline_ranked[base_rank - 1]
                fit_deltas_by_school.setdefault(school_id, []).append(ranked_by_id[school_id].fit_score - base.fit_score)

        scenario_results = [
            self._scenario_result(
                scenario,
                applied_weights,
                ranked,
                baseline_ranked,
                baseline_positions,
                deltas_by_school,
                fit_deltas_by_school,
                baseline_weights,
                emphasis,
            )
            for scenario, applied_weights, ranked, emphasis in scenario_rankings
        ]

        stable_schools = build_stable_summaries(baseline_ranked, scenario_rankings, deltas_by_school, fit_deltas_by_school)
        volatile_schools = build_volatile_summaries(baseline_ranked, scenario_rankings, deltas_by_school, fit_deltas_by_school)
        category_drivers = build_category_drivers(baseline_ranked, scenario_rankings, baseline_weights)
        confidence_impacts = build_confidence_impacts(baseline_ranked, scenario_rankings)
        tradeoffs = build_tradeoff_explanations(scenario_results)
        messages = build_summary_messages(stable_schools, volatile_schools, category_drivers)

        response = SensitivityResponse(
            ranking_version=RANKING_VERSION,
            baseline_weights=baseline_weights,
            stable_choice_definition=STABLE_DEFINITION,
            volatile_choice_definition=VOLATILE_DEFINITION,
            baseline_results=baseline_results,
            scenarios=scenario_results,
            stable_schools=stable_schools,
            volatile_schools=volatile_schools,
            category_drivers=category_drivers,
            confidence_impacts=confidence_impacts,
            tradeoff_explanations=tradeoffs,
            summary_messages=messages,
        )
        self.cache.set_model(cache_key, response, self.cache.ranking_ttl_seconds)
        return response

    def _candidate_rows(self, request: SensitivityRequest) -> list[dict[str, object]]:
        if request.candidate_school_ids:
            return self.repository.get_ranking_candidate_rows_by_ids(request.candidate_school_ids)
        return self.repository.get_ranking_candidate_rows(request.filters)

    def _movement(
        self,
        ranked: RankedSchool,
        base: RankedSchool | None,
        base_rank: int | None,
        scenario_rank: int | None,
        all_scenario_deltas: list[int],
        all_fit_deltas: list[float],
        base_weights: dict[str, float] | None = None,
        scenario_weights: dict[str, float] | None = None,
    ) -> SensitivitySchoolMovement:
        school_id = int(ranked.row["school_id"])
        rank_delta = None if base_rank is None or scenario_rank is None else base_rank - scenario_rank
        fit_delta = 0.0 if base is None else round(ranked.fit_score - base.fit_score, 2)
        confidence_delta = 0.0 if base is None else round(ranked.confidence_score - base.confidence_score, 4)
        drivers = category_drivers_for_school(base, ranked, base_weights, scenario_weights)
        stability = classify_choice(all_scenario_deltas, all_fit_deltas, base_rank)
        movement = movement_label(rank_delta, base_rank, scenario_rank)
        return SensitivitySchoolMovement(
            school_id=school_id,
            name=str(ranked.row["name"]),
            city=str(ranked.row["city"]),
            state=str(ranked.row["state"]),
            base_rank=base_rank,
            scenario_rank=scenario_rank,
            rank_delta=rank_delta,
            fit_score=ranked.fit_score,
            fit_delta=fit_delta,
            confidence_score=ranked.confidence_score,
            confidence_delta=confidence_delta,
            category_scores=ranked.category_scores,
            category_drivers=drivers,
            movement=movement,
            stability=stability,
            top_reasons=ranked.top_reasons,
            top_tradeoffs=ranked.top_tradeoffs,
            explanation=movement_explanation(str(ranked.row["name"]), rank_delta, drivers, stability),
        )

    def _scenario_result(
        self,
        scenario: SensitivityScenario,
        applied_weights: dict[str, float],
        ranked: list[RankedSchool],
        baseline_ranked: list[RankedSchool],
        baseline_positions: dict[int, int],
        deltas_by_school: dict[int, list[int]],
        fit_deltas_by_school: dict[int, list[float]],
        baseline_weights: dict[str, float],
        emphasis: str | None,
    ) -> SensitivityScenarioResult:
        base_by_id = {int(item.row["school_id"]): item for item in baseline_ranked}
        scenario_positions = positions_by_school(ranked)
        movements = [
            self._movement(
                item,
                base_by_id.get(int(item.row["school_id"])),
                baseline_positions.get(int(item.row["school_id"])),
                scenario_positions.get(int(item.row["school_id"])),
                deltas_by_school.get(int(item.row["school_id"]), []),
                fit_deltas_by_school.get(int(item.row["school_id"]), []),
                baseline_weights,
                applied_weights,
            )
            for item in ranked
        ]
        return SensitivityScenarioResult(
            scenario_id=scenario.scenario_id,
            label=scenario.label,
            applied_weights=applied_weights,
            emphasis_dimension=emphasis,
            results=movements,
            summary=scenario_summary(scenario.label, movements, emphasis),
        )

    def _profile_snapshot(self, preferences: Preference) -> dict[str, object]:
        return {
            "intended_major": preferences.intended_major,
            "home_state": preferences.home_state,
            "max_annual_cost": preferences.max_annual_cost,
            "constraints": preferences.constraints,
            "weights": normalize_weights(preferences.weights),
        }


def scenario_weights(base_weights: dict[str, float], scenario: SensitivityScenario) -> tuple[dict[str, float], str | None]:
    next_weights = normalize_weights(base_weights)
    emphasis: str | None = None
    for raw_key, value in scenario.weight_adjustments.items():
        key = DIMENSION_ALIASES.get(raw_key, raw_key)
        next_weights[key] = max(float(next_weights.get(key, 0.0)), value)
        emphasis = raw_key
    return normalize_weights(next_weights), emphasis


def scenario_preferences(preferences: Preference, weights: dict[str, float], scenario: SensitivityScenario) -> Preference:
    constraints = dict(preferences.constraints)
    if "prestige_selectivity" in scenario.weight_adjustments:
        constraints["admissions_strategy"] = "reach"
    return preferences.model_copy(update={"weights": weights, "constraints": constraints})


def positions_by_school(ranked: list[RankedSchool]) -> dict[int, int]:
    return {int(item.row["school_id"]): index + 1 for index, item in enumerate(ranked)}


def movement_label(rank_delta: int | None, base_rank: int | None, scenario_rank: int | None) -> str:
    if base_rank is None:
        return "new"
    if scenario_rank is None:
        return "removed"
    if rank_delta is None or rank_delta == 0:
        return "stable"
    return "up" if rank_delta > 0 else "down"


def classify_choice(rank_deltas: list[int], fit_deltas: list[float], base_rank: int | None) -> str:
    max_rank_delta = max([abs(value) for value in rank_deltas], default=0)
    max_fit_delta = max([abs(value) for value in fit_deltas], default=0.0)
    if max_rank_delta >= 3 or max_fit_delta >= 8:
        return "volatile_choice"
    if base_rank is not None and base_rank <= 5 and max_rank_delta <= 1 and max_fit_delta <= 4:
        return "stable_choice"
    return "watch_choice"


def category_drivers_for_school(
    base: RankedSchool | None,
    scenario: RankedSchool,
    base_weights: dict[str, float] | None,
    scenario_weights: dict[str, float] | None,
) -> list[str]:
    if base is None or base_weights is None or scenario_weights is None:
        return []
    changes = sorted(
        (
            (
                abs(
                    scenario.category_scores.get(key, 50.0) * scenario_weights.get(key, 0.0)
                    - base.category_scores.get(key, 50.0) * base_weights.get(key, 0.0)
                ),
                key,
            )
            for key in CATEGORY_KEYS
        ),
        key=lambda item: (-item[0], item[1]),
    )
    return [key for value, key in changes if value >= 1][:3]


def movement_explanation(name: str, rank_delta: int | None, drivers: list[str], stability: str) -> str:
    driver_text = ", ".join(driver.replace("_", " ") for driver in drivers) or "the current weighted category mix"
    if rank_delta is None or rank_delta == 0:
        return f"{name} stays in the same rank because {driver_text} remains similar under this scenario."
    direction = "rises" if rank_delta > 0 else "falls"
    return f"{name} {direction} {abs(rank_delta)} rank position(s), mainly from {driver_text}; classification: {stability.replace('_', ' ')}."


def scenario_summary(label: str, movements: list[SensitivitySchoolMovement], emphasis: str | None) -> str:
    biggest = max(movements, key=lambda item: abs(item.rank_delta or 0), default=None)
    if biggest is None:
        return f"{label} has no ranked schools to compare."
    if biggest.rank_delta == 0:
        return f"{label} keeps the current top choices stable."
    direction = "rises" if (biggest.rank_delta or 0) > 0 else "falls"
    emphasis_text = emphasis.replace("_", " ") if emphasis else "the adjusted weights"
    return f"{biggest.name} {direction} most when {emphasis_text} changes."


def build_stable_summaries(
    baseline: list[RankedSchool],
    scenarios: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]],
    deltas_by_school: dict[int, list[int]],
    fit_deltas_by_school: dict[int, list[float]],
) -> list[SensitivityChoiceSummary]:
    return [
        summary_for_school(item, index + 1, scenarios, deltas_by_school, fit_deltas_by_school, "stable")
        for index, item in enumerate(baseline)
        if classify_choice(
            deltas_by_school.get(int(item.row["school_id"]), []),
            fit_deltas_by_school.get(int(item.row["school_id"]), []),
            index + 1,
        ) == "stable_choice"
    ][:5]


def build_volatile_summaries(
    baseline: list[RankedSchool],
    scenarios: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]],
    deltas_by_school: dict[int, list[int]],
    fit_deltas_by_school: dict[int, list[float]],
) -> list[SensitivityChoiceSummary]:
    summaries = [
        summary_for_school(item, index + 1, scenarios, deltas_by_school, fit_deltas_by_school, "volatile")
        for index, item in enumerate(baseline)
        if classify_choice(
            deltas_by_school.get(int(item.row["school_id"]), []),
            fit_deltas_by_school.get(int(item.row["school_id"]), []),
            index + 1,
        ) == "volatile_choice"
    ]
    return sorted(summaries, key=lambda item: (-item.max_rank_delta, item.base_rank or 999))[:5]


def summary_for_school(
    school: RankedSchool,
    base_rank: int,
    scenarios: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]],
    deltas_by_school: dict[int, list[int]],
    fit_deltas_by_school: dict[int, list[float]],
    kind: str,
) -> SensitivityChoiceSummary:
    school_id = int(school.row["school_id"])
    scenario_ranks = []
    for _, _, ranked, _ in scenarios:
        position = positions_by_school(ranked).get(school_id)
        if position is not None:
            scenario_ranks.append(position)
    average_rank = round(mean([base_rank, *scenario_ranks]), 2)
    max_rank_delta = max([abs(value) for value in deltas_by_school.get(school_id, [])], default=0)
    max_fit_delta = round(max([abs(value) for value in fit_deltas_by_school.get(school_id, [])], default=0.0), 2)
    if kind == "stable":
        explanation = f"{school.row['name']} remains highly ranked across the tested weighting scenarios."
    else:
        explanation = f"{school.row['name']} changes materially when one priority receives more weight."
    return SensitivityChoiceSummary(
        school_id=school_id,
        name=str(school.row["name"]),
        base_rank=base_rank,
        average_rank=average_rank,
        max_rank_delta=max_rank_delta,
        max_fit_delta=max_fit_delta,
        explanation=explanation,
    )


def build_category_drivers(
    baseline: list[RankedSchool],
    scenarios: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]],
    baseline_weights: dict[str, float],
) -> list[SensitivityCategoryDriver]:
    baseline_by_id = {int(item.row["school_id"]): item for item in baseline}
    totals = {key: [] for key in CATEGORY_KEYS}
    for _, applied_weights, ranked, _ in scenarios:
        for item in ranked:
            base = baseline_by_id.get(int(item.row["school_id"]))
            if base is None:
                continue
            for key in CATEGORY_KEYS:
                totals[key].append(
                    abs(
                        item.category_scores.get(key, 50.0) * applied_weights.get(key, 0.0)
                        - base.category_scores.get(key, 50.0) * baseline_weights.get(key, 0.0)
                    )
                )
    drivers = [
        SensitivityCategoryDriver(
            category=key,
            average_absolute_fit_delta=round(mean(values), 2) if values else 0.0,
            affected_school_count=sum(1 for value in values if value >= 1),
            explanation=f"{key.replace('_', ' ').title()} is a visible driver when its weighted contribution changes under scenario weights.",
        )
        for key, values in totals.items()
    ]
    return sorted(drivers, key=lambda item: (-item.average_absolute_fit_delta, item.category))[:4]


def build_confidence_impacts(
    baseline: list[RankedSchool],
    scenarios: list[tuple[SensitivityScenario, dict[str, float], list[RankedSchool], str | None]],
) -> list[SensitivityConfidenceImpact]:
    baseline_by_id = {int(item.row["school_id"]): item for item in baseline}
    impacts: list[SensitivityConfidenceImpact] = []
    for school in baseline:
        school_id = int(school.row["school_id"])
        deltas = []
        for _, _, ranked, _ in scenarios:
            scenario_school = next((item for item in ranked if int(item.row["school_id"]) == school_id), None)
            if scenario_school is not None:
                deltas.append(abs(scenario_school.confidence_score - baseline_by_id[school_id].confidence_score))
        max_delta = round(max(deltas, default=0.0), 4)
        if max_delta >= 0.02:
            impacts.append(
                SensitivityConfidenceImpact(
                    school_id=school_id,
                    name=str(school.row["name"]),
                    max_confidence_delta=max_delta,
                    explanation=f"{school.row['name']} has a confidence change because the scenario weights emphasize categories with different data coverage.",
                )
            )
    return sorted(impacts, key=lambda item: (-item.max_confidence_delta, item.school_id))[:5]


def build_tradeoff_explanations(scenarios: list[SensitivityScenarioResult]) -> list[str]:
    explanations: list[str] = []
    for scenario in scenarios:
        changed = [item for item in scenario.results if item.rank_delta and abs(item.rank_delta) >= 2]
        for item in changed[:2]:
            drivers = ", ".join(driver.replace("_", " ") for driver in item.category_drivers) or "weighted fit"
            explanations.append(f"In {scenario.label}, {item.name} moves {item.rank_delta:+d} ranks because {drivers} carries more weight.")
    return explanations or ["The tested scenarios keep ranking movement modest with the current candidate set."]


def build_summary_messages(
    stable: list[SensitivityChoiceSummary],
    volatile: list[SensitivityChoiceSummary],
    drivers: list[SensitivityCategoryDriver],
) -> list[str]:
    messages: list[str] = []
    if stable:
        messages.append(f"{stable[0].name} remains stable across the tested weighting scenarios.")
    if volatile:
        messages.append(f"{volatile[0].name} is the most volatile choice in the current sensitivity run.")
    if drivers:
        messages.append(f"Your rankings are currently most sensitive to {drivers[0].category.replace('_', ' ')} signals.")
    return messages or ["The current rankings are relatively stable across these weighting scenarios."]
