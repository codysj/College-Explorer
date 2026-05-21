from __future__ import annotations

from datetime import UTC, datetime

from repositories.decision import DecisionRepository
from schemas.decision import (
    DecisionOffer,
    DecisionOfferCreate,
    DecisionOffersResponse,
    DecisionRecommendation,
    DecisionReportRequest,
    DecisionReportResponse,
    DecisionSchoolSummary,
)
from services.ranking_service import RANKING_VERSION, RankingService, to_int

DECISION_REPORT_VERSION = "v1.0"
DISCLAIMER = (
    "Decision summaries are deterministic planning support based on available data and your inputs. "
    "They are not admissions, financial, legal, or guaranteed outcome advice."
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

        confidence_flags = build_report_confidence_flags(summaries, request)
        response = DecisionReportResponse(
            report_version=DECISION_REPORT_VERSION,
            ranking_version=RANKING_VERSION,
            generated_at=datetime.now(UTC),
            disclaimer=DISCLAIMER,
            decision_confidence=decision_confidence(confidence_flags, summaries),
            confidence_flags=confidence_flags,
            schools=summaries,
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
