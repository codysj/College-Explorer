from __future__ import annotations

from datetime import UTC, datetime

from repositories.decision import DecisionRepository
from schemas.decision import (
    DecisionCategoryScoreRow,
    DecisionConcernRow,
    DecisionCostValueRow,
    DecisionFinalistRankingRow,
    DecisionOffer,
    DecisionOfferCreate,
    DecisionOffersResponse,
    DecisionRecommendation,
    DecisionReportRequest,
    DecisionReportResponse,
    DecisionSchoolSummary,
    DecisionSensitivityHighlight,
)
from schemas.cost_calculator import CostCalculatorAssumption
from services.cost_calculator import build_result
from services.ranking_service import RANKING_VERSION, RankingService, to_int
from services.sensitivity import scenario_preferences, scenario_weights

DECISION_REPORT_VERSION = "v2.7"
DISCLAIMER = (
    "This report is decision-support only. It is not admissions advice, financial advice, or a guarantee of outcomes. "
    "Estimates are based on available public data, local seed data, and user-entered offer assumptions."
)
METHODOLOGY_NOTE = (
    "Rankings, category scores, cost/value labels, sensitivity highlights, confidence, reasons, and tradeoffs are produced by deterministic code. "
    "Missing data is treated as unknown and lowers confidence instead of being converted to zero."
)


class DecisionService:
    def __init__(self, repository: DecisionRepository, ranking_service: RankingService) -> None:
        self.repository = repository
        self.ranking_service = ranking_service

    def upsert_offer(self, request: DecisionOfferCreate) -> DecisionOffer:
        return DecisionOffer(**self.repository.upsert_offer(request))

    def list_offers(self, user_id: int) -> DecisionOffersResponse:
        return DecisionOffersResponse(
            offers=[DecisionOffer(**row) for row in self.repository.get_offer_rows(user_id)]
        )

    def build_report(self, request: DecisionReportRequest) -> DecisionReportResponse:
        offer_rows = self.repository.get_offer_rows(request.user_id, request.school_ids)
        if len(offer_rows) > 8:
            raise ValueError("Decision reports support up to 8 accepted or finalist schools.")
        school_ids = [int(row["school_id"]) for row in offer_rows]
        school_rows = self.repository.get_decision_candidate_rows(school_ids)
        offers_by_school = {int(row["school_id"]): row for row in offer_rows}
        ranked_by_school = {
            int(row["school_id"]): self.ranking_service.score_school(row, request.preferences)
            for row in school_rows
        }

        summaries = [
            build_school_summary(ranked_by_school[school_id], offers_by_school[school_id])
            for school_id in school_ids
            if school_id in ranked_by_school
        ]
        summaries.sort(key=lambda item: (-item.fit_score, -item.confidence_score, item.school_id))
        if not summaries:
            raise ValueError("At least one accepted or finalist offer is required to generate a decision report.")

        confidence_flags = build_report_confidence_flags(summaries, request)
        cost_rows = build_cost_value_rows(school_rows, offers_by_school, request)
        sensitivity_highlights = build_sensitivity_highlights(school_rows, request, self.ranking_service)
        response = DecisionReportResponse(
            report_version=DECISION_REPORT_VERSION,
            ranking_version=RANKING_VERSION,
            report_title="College Decision Briefing",
            generated_at=datetime.now(UTC),
            disclaimer=DISCLAIMER,
            methodology_note=METHODOLOGY_NOTE,
            printable_report_path="/decision/report",
            share_url_path="/decision/report",
            decision_confidence=decision_confidence(confidence_flags, summaries),
            confidence_flags=confidence_flags,
            schools=summaries,
            finalist_ranking_table=finalist_ranking_table(summaries, cost_rows),
            category_score_table=category_score_table(summaries),
            cost_value_comparison=cost_rows,
            sensitivity_highlights=sensitivity_highlights,
            unresolved_questions=unresolved_questions(summaries, offers_by_school),
            best_overall_fit=recommendation(
                "Best overall fit",
                max_by(summaries, lambda item: item.fit_score),
                "Highest deterministic fit score from the current preference profile.",
            ),
            best_value=recommendation(
                "Best value",
                min_by(summaries, lambda item: item.estimated_yearly_cost if item.estimated_yearly_cost is not None else item.net_price),
                "Lowest known yearly cost using offer cost first, then profile net price when offer cost is missing.",
            ),
            strongest_career_upside=recommendation(
                "Strongest career upside",
                max_by(summaries, lambda item: item.category_scores.get("career")),
                "Highest deterministic career category score from known earnings, repayment, and career signals.",
            ),
            lowest_risk=recommendation(
                "Lowest risk",
                min_by(summaries, risk_score),
                "Strongest combination of known cost, confidence, and few unresolved concerns.",
            ),
            biggest_unresolved_factor=biggest_unresolved_factor(summaries),
            major_tradeoffs=major_tradeoffs(summaries),
        )
        if request.save_snapshot:
            response.snapshot_id = self.repository.save_snapshot(
                request.user_id,
                DECISION_REPORT_VERSION,
                [item.school_id for item in summaries],
                response.model_dump(mode="json", exclude={"snapshot_id"}),
            )
        return response


def build_school_summary(ranked, offer: dict[str, object]) -> DecisionSchoolSummary:
    row = ranked.row
    flags: list[str] = []
    estimated_cost = to_int(offer.get("estimated_yearly_cost"))
    net_price = to_int(row.get("net_price"))
    earnings = to_int(row.get("median_earnings"))
    if estimated_cost is None:
        flags.append("missing_financial_offer")
    if net_price is None:
        flags.append("missing_profile_net_price")
    if earnings is None:
        flags.append("missing_outcomes_metrics")
    if ranked.confidence_score < 0.7:
        flags.append("limited_ranking_data")

    return DecisionSchoolSummary(
        school_id=int(row["school_id"]),
        name=str(row["name"]),
        status=str(offer["status"]),
        fit_score=ranked.fit_score,
        confidence_score=ranked.confidence_score,
        category_scores=ranked.category_scores,
        estimated_yearly_cost=estimated_cost,
        net_price=net_price,
        median_earnings=earnings,
        unresolved_concern_count=len(offer.get("unresolved_concerns") or []),
        top_reasons=ranked.top_reasons,
        top_tradeoffs=ranked.top_tradeoffs,
        confidence_flags=flags,
    )


def build_cost_value_rows(
    school_rows: list[dict[str, object]],
    offers_by_school: dict[int, dict[str, object]],
    request: DecisionReportRequest,
) -> list[DecisionCostValueRow]:
    baseline_school_id = min(
        offers_by_school,
        key=lambda school_id: (
            to_int(offers_by_school[school_id].get("estimated_yearly_cost")) is None,
            to_int(offers_by_school[school_id].get("estimated_yearly_cost")) or 999_999,
            school_id,
        ),
    )
    baseline_row = next((row for row in school_rows if int(row["school_id"]) == baseline_school_id), {})
    baseline_offer = offers_by_school[baseline_school_id]
    baseline_cost = build_result(
        row=baseline_row,
        assumption=cost_assumption(baseline_school_id, baseline_offer),
        baseline_cost=None,
        max_budget=request.max_annual_family_budget or request.preferences.max_annual_cost,
    ).estimated_yearly_cost

    rows: list[DecisionCostValueRow] = []
    for row in school_rows:
        school_id = int(row["school_id"])
        offer = offers_by_school.get(school_id, {})
        result = build_result(
            row=row,
            assumption=cost_assumption(school_id, offer),
            baseline_cost=baseline_cost,
            max_budget=request.max_annual_family_budget or request.preferences.max_annual_cost,
        )
        rows.append(
            DecisionCostValueRow(
                school_id=result.school_id,
                school_name=result.name,
                estimated_yearly_cost=result.estimated_yearly_cost,
                estimated_four_year_total_cost=result.estimated_four_year_total_cost,
                affordability_status=result.affordability.status,
                directional_value=result.directional_outcome_adjusted_value,
                confidence=result.confidence,
                warnings=result.warnings,
            )
        )
    return sorted(rows, key=lambda item: (item.estimated_four_year_total_cost is None, item.estimated_four_year_total_cost or 0, item.school_id))


def cost_assumption(school_id: int, offer: dict[str, object]) -> CostCalculatorAssumption:
    return CostCalculatorAssumption(
        school_id=school_id,
        estimated_yearly_cost=to_int(offer.get("estimated_yearly_cost")),
        scholarships=to_int(offer.get("scholarships")),
        grants_aid=to_int(offer.get("aid_offer")),
    )


def build_sensitivity_highlights(
    school_rows: list[dict[str, object]],
    request: DecisionReportRequest,
    ranking_service: RankingService,
) -> list[DecisionSensitivityHighlight]:
    if len(school_rows) < 2:
        return [
            DecisionSensitivityHighlight(
                label="Sensitivity",
                summary="Add at least two finalists to compare how priority changes affect the recommendation.",
            )
        ]
    baseline = ranking_service.rank_rows(school_rows, request.preferences)
    baseline_positions = {int(item.row["school_id"]): index + 1 for index, item in enumerate(baseline)}
    highlights: list[DecisionSensitivityHighlight] = []
    scenarios = [
        ("Cost stress test", {"cost_value": 0.5}),
        ("Career upside stress test", {"career_outcomes": 0.5}),
        ("Academic fit stress test", {"academic_fit": 0.5}),
    ]
    base_weights = ranking_service_module_weights(request)
    for label, adjustments in scenarios:
        scenario = SimpleScenario(label, adjustments)
        weights, _ = scenario_weights(base_weights, scenario)
        ranked = ranking_service.rank_rows(school_rows, scenario_preferences(request.preferences, weights, scenario))
        if not ranked:
            continue
        leader = ranked[0]
        school_id = int(leader.row["school_id"])
        delta = baseline_positions.get(school_id, 1) - 1
        if delta > 0:
            summary = f"{leader.row['name']} becomes the top choice when {label.lower()} weights are emphasized."
        elif baseline and int(baseline[0].row["school_id"]) == school_id:
            summary = f"{leader.row['name']} remains the top choice under the {label.lower()}."
        else:
            summary = f"{leader.row['name']} is the strongest option in the {label.lower()}."
        highlights.append(
            DecisionSensitivityHighlight(
                label=label,
                school_id=school_id,
                school_name=str(leader.row["name"]),
                summary=summary,
            )
        )
    return highlights


class SimpleScenario:
    def __init__(self, label: str, weight_adjustments: dict[str, float]) -> None:
        self.scenario_id = label.lower().replace(" ", "_")
        self.label = label
        self.weight_adjustments = weight_adjustments


def ranking_service_module_weights(request: DecisionReportRequest) -> dict[str, float]:
    from services.ranking_service import normalize_weights

    return normalize_weights(request.preferences.weights)


def finalist_ranking_table(
    summaries: list[DecisionSchoolSummary],
    cost_rows: list[DecisionCostValueRow],
) -> list[DecisionFinalistRankingRow]:
    cost_by_school = {row.school_id: row for row in cost_rows}
    return [
        DecisionFinalistRankingRow(
            rank=index + 1,
            school_id=school.school_id,
            school_name=school.name,
            fit_score=school.fit_score,
            confidence_score=school.confidence_score,
            estimated_yearly_cost=school.estimated_yearly_cost if school.estimated_yearly_cost is not None else school.net_price,
            four_year_cost=cost_by_school.get(school.school_id).estimated_four_year_total_cost if cost_by_school.get(school.school_id) else None,
            career_score=school.category_scores.get("career"),
            major_tradeoff=(school.top_tradeoffs[0] if school.top_tradeoffs else "No major deterministic tradeoff flagged."),
        )
        for index, school in enumerate(summaries)
    ]


def category_score_table(summaries: list[DecisionSchoolSummary]) -> list[DecisionCategoryScoreRow]:
    return [
        DecisionCategoryScoreRow(
            school_id=school.school_id,
            school_name=school.name,
            academic=school.category_scores.get("academic"),
            cost=school.category_scores.get("cost"),
            career=school.category_scores.get("career"),
            location=school.category_scores.get("location"),
            campus=school.category_scores.get("campus"),
            admissions_realism=school.category_scores.get("admissions_realism"),
        )
        for school in summaries
    ]


def unresolved_questions(
    summaries: list[DecisionSchoolSummary],
    offers_by_school: dict[int, dict[str, object]],
) -> list[DecisionConcernRow]:
    rows: list[DecisionConcernRow] = []
    for summary in summaries:
        offer = offers_by_school.get(summary.school_id, {})
        questions = [str(item) for item in (offer.get("unresolved_concerns") or []) if str(item).strip()]
        if not questions and summary.confidence_flags:
            questions = [flag.replace("_", " ") for flag in summary.confidence_flags[:3]]
        rows.append(
            DecisionConcernRow(
                school_id=summary.school_id,
                school_name=summary.name,
                unresolved_concern_count=len(questions),
                questions=questions,
            )
        )
    return sorted(rows, key=lambda item: (-item.unresolved_concern_count, item.school_id))


def build_report_confidence_flags(summaries: list[DecisionSchoolSummary], request: DecisionReportRequest) -> list[str]:
    flags: list[str] = []
    if len(summaries) < 2:
        flags.append("fewer_than_two_finalists")
    if not request.preferences.weights:
        flags.append("incomplete_user_preferences")
    if any(item.estimated_yearly_cost is None for item in summaries):
        flags.append("missing_financial_data")
    if any(item.median_earnings is None for item in summaries):
        flags.append("missing_outcomes_metrics")
    if any(item.confidence_score < 0.7 for item in summaries):
        flags.append("limited_school_data")
    return sorted(set(flags))


def decision_confidence(flags: list[str], summaries: list[DecisionSchoolSummary]) -> str:
    if len(summaries) < 2 or len(flags) >= 3:
        return "low"
    if flags:
        return "medium"
    return "high"


def recommendation(label: str, school: DecisionSchoolSummary | None, rationale: str) -> DecisionRecommendation:
    return DecisionRecommendation(
        label=label,
        school_id=school.school_id if school else None,
        school_name=school.name if school else None,
        rationale=rationale if school else "Not enough finalist data is available to select this category.",
    )


def biggest_unresolved_factor(summaries: list[DecisionSchoolSummary]) -> DecisionRecommendation:
    school = max_by(summaries, lambda item: item.unresolved_concern_count)
    if school and school.unresolved_concern_count > 0:
        return recommendation(
            "Biggest unresolved factor",
            school,
            "This school has the most unresolved questions or concerns in the current decision workspace.",
        )
    return DecisionRecommendation(
        label="Biggest unresolved factor",
        school_id=None,
        school_name=None,
        rationale="No unresolved concerns have been entered yet.",
    )


def major_tradeoffs(summaries: list[DecisionSchoolSummary]) -> list[str]:
    if len(summaries) < 2:
        return ["Add at least two accepted or finalist schools to generate side-by-side tradeoffs."]

    tradeoffs: list[str] = []
    best_fit = max_by(summaries, lambda item: item.fit_score)
    best_value = min_by(summaries, lambda item: item.estimated_yearly_cost if item.estimated_yearly_cost is not None else item.net_price)
    best_career = max_by(summaries, lambda item: item.category_scores.get("career"))
    lowest_risk_school = min_by(summaries, risk_score)

    if best_fit and best_value and best_fit.school_id != best_value.school_id:
        tradeoffs.append(f"{best_fit.name} is your strongest overall fit, but {best_value.name} has the lower known cost.")
    if best_career and lowest_risk_school and best_career.school_id != lowest_risk_school.school_id:
        tradeoffs.append(f"{best_career.name} has the strongest career upside, while {lowest_risk_school.name} is the safer current-data choice.")
    if any(item.estimated_yearly_cost is None for item in summaries):
        tradeoffs.append("At least one finalist is missing offer-level cost data, so value comparisons should be treated as uncertain.")
    return tradeoffs or ["The finalists are close on the currently available decision signals."]


def risk_score(summary: DecisionSchoolSummary) -> float | None:
    cost = summary.estimated_yearly_cost if summary.estimated_yearly_cost is not None else summary.net_price
    if cost is None:
        return 10_000 + (1 - summary.confidence_score) * 100 + summary.unresolved_concern_count * 20
    return cost / 1000 + (1 - summary.confidence_score) * 100 + summary.unresolved_concern_count * 20


def max_by(items: list[DecisionSchoolSummary], selector) -> DecisionSchoolSummary | None:
    values = [(selector(item), item) for item in items]
    values = [(value, item) for value, item in values if value is not None]
    if not values:
        return None
    return sorted(values, key=lambda pair: (-float(pair[0]), pair[1].school_id))[0][1]


def min_by(items: list[DecisionSchoolSummary], selector) -> DecisionSchoolSummary | None:
    values = [(selector(item), item) for item in items]
    values = [(value, item) for value, item in values if value is not None]
    if not values:
        return None
    return sorted(values, key=lambda pair: (float(pair[0]), pair[1].school_id))[0][1]
