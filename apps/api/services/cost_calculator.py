from __future__ import annotations

from datetime import UTC, datetime

from repositories.schools import SchoolRepository
from schemas.cost_calculator import (
    AffordabilityIndicator,
    CalculatorConfidence,
    CostCalculatorRequest,
    CostCalculatorResponse,
    CostCalculatorSchoolResult,
    DirectionalValue,
    ObservedCostData,
    ObservedOutcomeData,
    RepaymentScenario,
)
from services.ranking_service import to_float, to_int

CALCULATOR_VERSION = "v1.0"
DISCLAIMER = (
    "Cost/value calculator outputs are estimates for planning only, not financial advice. "
    "Actual aid, costs, borrowing terms, repayment, and outcomes may vary."
)


class CostCalculatorService:
    def __init__(self, repository: SchoolRepository) -> None:
        self.repository = repository

    def calculate(self, request: CostCalculatorRequest) -> CostCalculatorResponse:
        requested_ids = [item.school_id for item in request.schools]
        rows = {
            int(row["school_id"]): row
            for row in self.repository.get_cost_calculator_rows(requested_ids)
        }
        assumptions_by_school = {item.school_id: item for item in request.schools}
        baseline_id = request.baseline_school_id or request.schools[0].school_id
        baseline_cost = yearly_cost(assumptions_by_school[baseline_id], rows.get(baseline_id, {}))

        results = [
            build_result(
                row=rows.get(school_id, {"school_id": school_id, "name": f"School {school_id}", "city": "", "state": ""}),
                assumption=assumption,
                baseline_cost=baseline_cost,
                max_budget=request.max_annual_family_budget,
            )
            for school_id, assumption in assumptions_by_school.items()
        ]
        results.sort(key=lambda item: (item.estimated_four_year_total_cost is None, item.estimated_four_year_total_cost or 0, item.school_id))

        return CostCalculatorResponse(
            calculator_version=CALCULATOR_VERSION,
            generated_at=datetime.now(UTC),
            disclaimer=DISCLAIMER,
            baseline_school_id=baseline_id,
            results=results,
            comparison_summary=comparison_summary(results, baseline_id),
        )


def build_result(
    row: dict[str, object],
    assumption,
    baseline_cost: int | None,
    max_budget: int | None,
) -> CostCalculatorSchoolResult:
    warnings = warning_flags(row, assumption)
    cost = yearly_cost(assumption, row)
    four_year_total = cost * 4 if cost is not None else None
    yearly_difference = cost - baseline_cost if cost is not None and baseline_cost is not None else None
    debt_exposure = estimated_debt_exposure(assumption, row)
    confidence = confidence_level(warnings, cost)

    return CostCalculatorSchoolResult(
        school_id=int(row["school_id"]),
        name=str(row.get("name") or f"School {assumption.school_id}"),
        city=str(row.get("city") or ""),
        state=str(row.get("state") or ""),
        observed_cost_data=ObservedCostData(
            tuition_in_state=to_int(row.get("tuition_in_state")),
            tuition_out_state=to_int(row.get("tuition_out_state")),
            net_price=to_int(row.get("net_price")),
            average_aid=to_int(row.get("average_aid")),
            debt_median=to_int(row.get("debt_median")),
        ),
        observed_outcome_data=ObservedOutcomeData(
            median_earnings=to_int(row.get("median_earnings")),
            graduation_rate=to_float(row.get("graduation_rate")),
            repayment_rate=to_float(row.get("repayment_rate")),
        ),
        assumptions=assumption,
        estimated_yearly_cost=cost,
        estimated_four_year_total_cost=four_year_total,
        yearly_cost_difference=yearly_difference,
        four_year_cost_difference=yearly_difference * 4 if yearly_difference is not None else None,
        estimated_debt_exposure=debt_exposure,
        repayment_scenarios=repayment_scenarios(debt_exposure, assumption.loan_interest_rate, assumption.loan_term_years),
        directional_outcome_adjusted_value=directional_value(four_year_total, row),
        affordability=affordability(cost, max_budget),
        confidence=confidence,
        warnings=warnings,
        formulas=formulas(assumption, row),
    )


def yearly_cost(assumption, row: dict[str, object]) -> int | None:
    if assumption.estimated_yearly_cost is not None:
        return assumption.estimated_yearly_cost
    if assumption.estimated_net_price is not None:
        return max(0, assumption.estimated_net_price - (assumption.scholarships or 0) - (assumption.grants_aid or 0))
    if assumption.tuition is not None:
        return max(0, assumption.tuition - (assumption.scholarships or 0) - (assumption.grants_aid or 0))
    net_price = to_int(row.get("net_price"))
    if net_price is not None:
        return max(0, net_price - (assumption.scholarships or 0) - (assumption.grants_aid or 0))
    tuition = to_int(row.get("tuition_out_state")) or to_int(row.get("tuition_in_state"))
    if tuition is not None:
        return max(0, tuition - (assumption.scholarships or 0) - (assumption.grants_aid or 0))
    return None


def estimated_debt_exposure(assumption, row: dict[str, object]) -> int | None:
    if assumption.annual_loan_amount is not None:
        return assumption.annual_loan_amount * 4
    return to_int(row.get("debt_median"))


def repayment_scenarios(principal: int | None, interest_rate: float, term_years: int) -> list[RepaymentScenario]:
    if principal is None:
        return []
    scenarios = [
        ("lower_debt", max(0, principal - 10_000), "Total borrowed is $10,000 lower than the current assumption."),
        ("base", principal, "Total borrowed matches the current assumption or observed median debt indicator."),
        ("higher_debt", principal + 10_000, "Total borrowed is $10,000 higher than the current assumption."),
    ]
    return [
        RepaymentScenario(
            scenario=kind,
            principal=amount,
            interest_rate=interest_rate,
            term_years=term_years,
            estimated_monthly_payment=monthly_payment(amount, interest_rate, term_years),
            estimated_total_repaid=monthly_payment(amount, interest_rate, term_years) * term_years * 12,
            assumption=label,
        )
        for kind, amount, label in scenarios
    ]


def monthly_payment(principal: int, annual_rate: float, term_years: int) -> int:
    if principal <= 0:
        return 0
    months = term_years * 12
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return round(principal / months)
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round(payment)


def directional_value(four_year_total: int | None, row: dict[str, object]) -> DirectionalValue:
    earnings = to_int(row.get("median_earnings"))
    graduation_rate = to_float(row.get("graduation_rate"))
    repayment_rate = to_float(row.get("repayment_rate"))
    if four_year_total is None or earnings is None or graduation_rate is None:
        return "uncertain"
    cost_to_earnings = four_year_total / max(earnings, 1)
    if cost_to_earnings <= 1.7 and graduation_rate >= 0.75 and (repayment_rate is None or repayment_rate >= 0.75):
        return "stronger_value"
    if cost_to_earnings <= 2.6 and graduation_rate >= 0.60:
        return "reasonable_value"
    return "higher_cost_tradeoff"


def affordability(cost: int | None, max_budget: int | None) -> AffordabilityIndicator:
    if cost is None or max_budget is None:
        return AffordabilityIndicator(status="unknown", message="Affordability cannot be evaluated without both yearly cost and budget.")
    if cost <= max_budget:
        return AffordabilityIndicator(status="within_budget", message="Estimated yearly cost is within the entered family budget.")
    if cost <= max_budget * 1.15:
        return AffordabilityIndicator(status="near_budget", message="Estimated yearly cost is near the entered budget and may need careful review.")
    return AffordabilityIndicator(status="above_budget", message="Estimated yearly cost is above the entered family budget.")


def warning_flags(row: dict[str, object], assumption) -> list[str]:
    flags: list[str] = []
    if not row.get("name"):
        flags.append("school_profile_not_found")
    if assumption.estimated_yearly_cost is None and assumption.estimated_net_price is None and row.get("net_price") is None:
        flags.append("missing_aid_or_net_price")
    if row.get("median_earnings") is None or row.get("graduation_rate") is None:
        flags.append("missing_outcomes_data")
    if assumption.annual_loan_amount is None and row.get("debt_median") is not None:
        flags.append("using_observed_median_debt_not_personal_loan_plan")
    if assumption.annual_loan_amount is None and row.get("debt_median") is None:
        flags.append("missing_debt_assumption")
    if assumption.estimated_yearly_cost is None:
        flags.append("derived_yearly_cost")
    return sorted(set(flags))


def confidence_level(warnings: list[str], cost: int | None) -> CalculatorConfidence:
    if cost is None or len(warnings) >= 3:
        return "low"
    if warnings:
        return "medium"
    return "high"


def formulas(assumption, row: dict[str, object]) -> list[str]:
    source = "estimated_yearly_cost"
    if assumption.estimated_yearly_cost is None:
        if assumption.estimated_net_price is not None:
            source = "estimated_net_price - scholarships - grants_aid"
        elif assumption.tuition is not None:
            source = "tuition - scholarships - grants_aid"
        elif row.get("net_price") is not None:
            source = "profile_net_price - scholarships - grants_aid"
        else:
            source = "profile_tuition - scholarships - grants_aid"
    return [
        f"estimated_yearly_cost = max(0, {source})",
        "estimated_four_year_total_cost = estimated_yearly_cost * 4",
        "estimated_debt_exposure = annual_loan_amount * 4 when supplied; otherwise observed median debt indicator when available",
        "repayment monthly payment uses the standard amortization formula with entered interest rate and term",
        "directional value compares four-year cost with observed earnings, graduation, and repayment data when available",
    ]


def comparison_summary(results: list[CostCalculatorSchoolResult], baseline_id: int | None) -> list[str]:
    if len(results) < 2:
        return ["Add at least two schools to compare cost differences."]
    baseline = next((item for item in results if item.school_id == baseline_id), None)
    summaries: list[str] = []
    if baseline:
        for item in results:
            if item.school_id == baseline.school_id or item.four_year_cost_difference is None:
                continue
            direction = "more" if item.four_year_cost_difference > 0 else "less"
            summaries.append(
                f"{item.name} may cost about ${abs(item.four_year_cost_difference):,} {direction} over four years than {baseline.name} under current assumptions."
            )
    best_value = next((item for item in results if item.directional_outcome_adjusted_value == "stronger_value"), None)
    if best_value:
        summaries.append(f"{best_value.name} shows stronger directional value under the current cost and outcomes assumptions.")
    if any("using_observed_median_debt_not_personal_loan_plan" in item.warnings for item in results):
        summaries.append("Debt exposure includes observed median debt for at least one school because no personal loan assumption was entered.")
    return summaries or ["Cost differences are currently close or too uncertain to summarize confidently."]
