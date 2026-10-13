from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, model_validator

from schemas.base import ApiModel
from schemas.preferences import Preference

DecisionStatus = Literal["accepted", "finalist"]


class DecisionOfferInput(ApiModel):
    """One accepted or finalist school as the student entered it.

    Offers live in the student's browser and travel with each report request. The server
    keeps no per-visitor offer store, so there is nothing for one visitor to read of another's.
    """

    school_id: int = Field(ge=1)
    status: DecisionStatus = "accepted"
    aid_offer: int | None = Field(default=None, ge=0, le=250_000)
    scholarships: int | None = Field(default=None, ge=0, le=250_000)
    estimated_yearly_cost: int | None = Field(default=None, ge=0, le=250_000)
    unresolved_concerns: list[Annotated[str, Field(max_length=300)]] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def strip_concerns(self) -> DecisionOfferInput:
        self.unresolved_concerns = [item.strip() for item in self.unresolved_concerns if item.strip()]
        return self


class DecisionReportRequest(ApiModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "offers": [
                    {"school_id": 1, "status": "finalist", "aid_offer": 12000, "estimated_yearly_cost": 24000,
                     "unresolved_concerns": ["Confirm housing cost"]},
                    {"school_id": 2, "status": "accepted", "estimated_yearly_cost": 31000},
                ],
                "preferences": {
                    "intended_major": "Computer Science",
                    "home_state": "CA",
                    "max_annual_cost": 32000,
                    "weights": {"academic": 0.25, "cost": 0.25, "career": 0.25, "campus": 0.25},
                },
            }
        }
    )

    offers: list[DecisionOfferInput] = Field(min_length=1, max_length=8)
    preferences: Preference = Field(default_factory=Preference)
    max_annual_family_budget: int | None = Field(default=None, ge=0, le=250_000)

    @model_validator(mode="after")
    def unique_schools(self) -> DecisionReportRequest:
        ids = [offer.school_id for offer in self.offers]
        if len(ids) != len(set(ids)):
            raise ValueError("Each school can appear in a decision report only once.")
        return self


class DecisionSchoolSummary(ApiModel):
    school_id: int
    name: str
    status: DecisionStatus
    fit_score: float
    confidence_score: float
    category_scores: dict[str, float]
    estimated_yearly_cost: int | None
    net_price: int | None
    median_earnings: int | None
    unresolved_concern_count: int
    top_reasons: list[str]
    top_tradeoffs: list[str]
    confidence_flags: list[str]


class DecisionFinalistRankingRow(ApiModel):
    rank: int
    school_id: int
    school_name: str
    fit_score: float
    confidence_score: float
    estimated_yearly_cost: int | None
    four_year_cost: int | None
    career_score: float | None
    major_tradeoff: str


class DecisionCategoryScoreRow(ApiModel):
    school_id: int
    school_name: str
    academic: float | None = None
    cost: float | None = None
    career: float | None = None
    location: float | None = None
    campus: float | None = None
    admissions_realism: float | None = None


class DecisionCostValueRow(ApiModel):
    school_id: int
    school_name: str
    estimated_yearly_cost: int | None
    estimated_four_year_total_cost: int | None
    affordability_status: str
    directional_value: str
    confidence: str
    warnings: list[str]


class DecisionConcernRow(ApiModel):
    school_id: int
    school_name: str
    unresolved_concern_count: int
    questions: list[str]


class DecisionSensitivityHighlight(ApiModel):
    label: str
    school_id: int | None = None
    school_name: str | None = None
    summary: str


class DecisionRecommendation(ApiModel):
    label: str
    school_id: int | None
    school_name: str | None
    rationale: str


class DecisionReportResponse(ApiModel):
    report_version: str
    ranking_version: str
    report_title: str
    generated_at: datetime
    disclaimer: str
    methodology_note: str
    printable_report_path: str
    share_url_path: str
    decision_confidence: Literal["low", "medium", "high"]
    confidence_flags: list[str]
    schools: list[DecisionSchoolSummary]
    finalist_ranking_table: list[DecisionFinalistRankingRow]
    category_score_table: list[DecisionCategoryScoreRow]
    cost_value_comparison: list[DecisionCostValueRow]
    sensitivity_highlights: list[DecisionSensitivityHighlight]
    unresolved_questions: list[DecisionConcernRow]
    best_overall_fit: DecisionRecommendation
    best_value: DecisionRecommendation
    strongest_career_upside: DecisionRecommendation
    lowest_risk: DecisionRecommendation
    biggest_unresolved_factor: DecisionRecommendation
    major_tradeoffs: list[str]
