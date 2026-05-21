from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CalculatorConfidence = Literal["low", "medium", "high"]
AffordabilityStatus = Literal["within_budget", "near_budget", "above_budget", "unknown"]
DirectionalValue = Literal["stronger_value", "reasonable_value", "higher_cost_tradeoff", "uncertain"]
RepaymentScenarioKind = Literal["base", "lower_debt", "higher_debt"]


class CostCalculatorAssumption(BaseModel):
    school_id: int = Field(ge=1)
    tuition: int | None = Field(default=None, ge=0, le=250_000)
    estimated_net_price: int | None = Field(default=None, ge=0, le=250_000)
    scholarships: int | None = Field(default=None, ge=0, le=250_000)
    grants_aid: int | None = Field(default=None, ge=0, le=250_000)
    estimated_yearly_cost: int | None = Field(default=None, ge=0, le=250_000)
    annual_loan_amount: int | None = Field(default=None, ge=0, le=250_000)
    loan_interest_rate: float = Field(default=0.055, ge=0, le=0.25)
    loan_term_years: int = Field(default=10, ge=1, le=30)

    @model_validator(mode="after")
    def validate_aid_against_tuition(self) -> "CostCalculatorAssumption":
        total_aid = (self.scholarships or 0) + (self.grants_aid or 0)
        known_price = self.tuition if self.tuition is not None else self.estimated_net_price
        if known_price is not None and total_aid > known_price:
            raise ValueError("Scholarships plus grants/aid cannot exceed the known yearly price input.")
        return self


class CostCalculatorRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schools": [
                    {
                        "school_id": 1,
                        "estimated_net_price": 28000,
                        "scholarships": 8000,
                        "grants_aid": 6000,
                        "annual_loan_amount": 5500,
                    },
                    {
                        "school_id": 2,
                        "estimated_yearly_cost": 42000,
                        "annual_loan_amount": 12000,
                    },
                ],
                "baseline_school_id": 1,
                "max_annual_family_budget": 30000,
            }
        }
    )

    schools: list[CostCalculatorAssumption] = Field(min_length=1, max_length=8)
    baseline_school_id: int | None = Field(default=None, ge=1)
    max_annual_family_budget: int | None = Field(default=None, ge=0, le=250_000)

    @model_validator(mode="after")
    def validate_unique_schools(self) -> "CostCalculatorRequest":
        school_ids = [item.school_id for item in self.schools]
        if len(school_ids) != len(set(school_ids)):
            raise ValueError("Each school may appear only once in the calculator request.")
        if self.baseline_school_id is not None and self.baseline_school_id not in set(school_ids):
            raise ValueError("baseline_school_id must be included in schools.")
        return self


class ObservedCostData(BaseModel):
    tuition_in_state: int | None
    tuition_out_state: int | None
    net_price: int | None
    average_aid: int | None
    debt_median: int | None


class ObservedOutcomeData(BaseModel):
    median_earnings: int | None
    graduation_rate: float | None
    repayment_rate: float | None


class RepaymentScenario(BaseModel):
    scenario: RepaymentScenarioKind
    principal: int
    interest_rate: float
    term_years: int
    estimated_monthly_payment: int
    estimated_total_repaid: int
    assumption: str


class AffordabilityIndicator(BaseModel):
    status: AffordabilityStatus
    message: str


class CostCalculatorSchoolResult(BaseModel):
    school_id: int
    name: str
    city: str
    state: str
    observed_cost_data: ObservedCostData
    observed_outcome_data: ObservedOutcomeData
    assumptions: CostCalculatorAssumption
    estimated_yearly_cost: int | None
    estimated_four_year_total_cost: int | None
    yearly_cost_difference: int | None
    four_year_cost_difference: int | None
    estimated_debt_exposure: int | None
    repayment_scenarios: list[RepaymentScenario]
    directional_outcome_adjusted_value: DirectionalValue
    affordability: AffordabilityIndicator
    confidence: CalculatorConfidence
    warnings: list[str]
    formulas: list[str]


class CostCalculatorResponse(BaseModel):
    calculator_version: str
    generated_at: datetime
    disclaimer: str
    baseline_school_id: int | None
    results: list[CostCalculatorSchoolResult]
    comparison_summary: list[str]
