from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schemas.preferences import Preference

DecisionStatus = Literal["accepted", "finalist"]


class DecisionOfferBase(BaseModel):
    user_id: int = Field(default=1, ge=1)
    school_id: int = Field(ge=1)
    status: DecisionStatus = "accepted"
    aid_offer: int | None = Field(default=None, ge=0)
    scholarships: int | None = Field(default=None, ge=0)
    estimated_yearly_cost: int | None = Field(default=None, ge=0)
    visit_notes: str | None = Field(default=None, max_length=4000)
    unresolved_concerns: list[str] = Field(default_factory=list, max_length=12)
    parent_priority_notes: str | None = Field(default=None, max_length=4000)
    student_priority_notes: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def validate_offer_totals(self) -> DecisionOfferBase:
        if self.aid_offer is not None and self.estimated_yearly_cost is not None:
            if self.aid_offer > 250_000 or self.estimated_yearly_cost > 250_000:
                raise ValueError("Annual financial inputs must be realistic yearly amounts.")
        if self.scholarships is not None and self.scholarships > 250_000:
            raise ValueError("Annual financial inputs must be realistic yearly amounts.")
        self.unresolved_concerns = [item.strip() for item in self.unresolved_concerns if item.strip()]
        return self


class DecisionOfferCreate(DecisionOfferBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "school_id": 2,
                "status": "finalist",
                "aid_offer": 12000,
                "scholarships": 8000,
                "estimated_yearly_cost": 24000,
                "visit_notes": "Strong department visit; commute felt manageable.",
                "unresolved_concerns": ["Confirm housing cost", "Compare internship access"],
                "parent_priority_notes": "Keep debt below the family budget.",
                "student_priority_notes": "Prefer urban campus and strong CS hiring.",
            }
        }
    )


class DecisionOffer(DecisionOfferBase):
    id: int
    school_name: str
    city: str
    state: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DecisionOffersResponse(BaseModel):
    offers: list[DecisionOffer] = Field(default_factory=list)


class DecisionReportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "school_ids": [1, 2, 3],
                "preferences": {
                    "intended_major": "Computer Science",
                    "home_state": "CA",
                    "max_annual_cost": 32000,
                    "weights": {"academic": 0.25, "cost": 0.25, "career": 0.25, "campus": 0.25},
                },
            }
        }
    )

    user_id: int = Field(default=1, ge=1)
    school_ids: list[int] | None = Field(default=None, min_length=1, max_length=8)
    preferences: Preference = Field(default_factory=Preference)
    max_annual_family_budget: int | None = Field(default=None, ge=0, le=250_000)
    save_snapshot: bool = True


class DecisionSchoolSummary(BaseModel):
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


class DecisionFinalistRankingRow(BaseModel):
    rank: int
    school_id: int
    school_name: str
    fit_score: float
    confidence_score: float
    estimated_yearly_cost: int | None
    four_year_cost: int | None
    career_score: float | None
    major_tradeoff: str


class DecisionCategoryScoreRow(BaseModel):
    school_id: int
    school_name: str
    academic: float | None = None
    cost: float | None = None
    career: float | None = None
    location: float | None = None
    campus: float | None = None
    admissions_realism: float | None = None


class DecisionCostValueRow(BaseModel):
    school_id: int
    school_name: str
    estimated_yearly_cost: int | None
    estimated_four_year_total_cost: int | None
    affordability_status: str
    directional_value: str
    confidence: str
    warnings: list[str]


class DecisionConcernRow(BaseModel):
    school_id: int
    school_name: str
    unresolved_concern_count: int
    questions: list[str]


class DecisionSensitivityHighlight(BaseModel):
    label: str
    school_id: int | None = None
    school_name: str | None = None
    summary: str


class DecisionRecommendation(BaseModel):
    label: str
    school_id: int | None
    school_name: str | None
    rationale: str


class DecisionReportResponse(BaseModel):
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
    snapshot_id: int | None = None
