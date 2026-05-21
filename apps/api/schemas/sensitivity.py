from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schemas.preferences import Preference
from schemas.schools import SearchRequest


SensitivityDimension = Literal[
    "academic",
    "academic_fit",
    "cost",
    "cost_value",
    "career",
    "career_outcomes",
    "campus",
    "campus_lifestyle",
    "location",
    "prestige_selectivity",
    "admissions_realism",
]


class SensitivityScenario(BaseModel):
    scenario_id: str = Field(min_length=1, max_length=48, pattern=r"^[A-Za-z0-9_-]+$")
    label: str = Field(min_length=1, max_length=80)
    weight_adjustments: dict[SensitivityDimension, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_weight_adjustments(self) -> "SensitivityScenario":
        for key, value in self.weight_adjustments.items():
            if value < 0 or value > 1:
                raise ValueError(f"weight_adjustments.{key} must be between 0 and 1")
        return self


class SensitivityRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "preferences": {
                    "intended_major": "Computer Science",
                    "home_state": "CA",
                    "max_annual_cost": 32000,
                    "weights": {
                        "academic": 0.25,
                        "cost": 0.2,
                        "career": 0.2,
                        "campus": 0.12,
                        "location": 0.1,
                        "admissions_realism": 0.13,
                    },
                },
                "scenarios": [
                    {
                        "scenario_id": "cost_focus",
                        "label": "Cost sensitivity raised",
                        "weight_adjustments": {"cost_value": 0.45},
                    }
                ],
                "candidate_school_ids": [1, 2, 3],
                "filters": {"page": 1, "page_size": 10},
            }
        }
    )

    preferences: Preference
    scenarios: list[SensitivityScenario] = Field(min_length=1, max_length=8)
    candidate_school_ids: list[int] = Field(default_factory=list, max_length=20)
    filters: SearchRequest = Field(default_factory=SearchRequest)

    @model_validator(mode="after")
    def validate_request(self) -> "SensitivityRequest":
        if len(set(self.candidate_school_ids)) != len(self.candidate_school_ids):
            raise ValueError("candidate_school_ids must be unique")
        for school_id in self.candidate_school_ids:
            if school_id < 1:
                raise ValueError("candidate_school_ids must contain positive ids")
        for key, value in self.preferences.weights.items():
            if value < 0 or value > 1:
                raise ValueError(f"preferences.weights.{key} must be between 0 and 1")
        return self


class SensitivitySchoolMovement(BaseModel):
    school_id: int
    name: str
    city: str
    state: str
    base_rank: int | None = None
    scenario_rank: int | None = None
    rank_delta: int | None = None
    fit_score: float
    fit_delta: float
    confidence_score: float
    confidence_delta: float
    category_scores: dict[str, float]
    category_drivers: list[str] = Field(default_factory=list)
    movement: Literal["up", "down", "stable", "new", "removed"]
    stability: Literal["stable_choice", "volatile_choice", "watch_choice"]
    top_reasons: list[str] = Field(default_factory=list)
    top_tradeoffs: list[str] = Field(default_factory=list)
    explanation: str


class SensitivityScenarioResult(BaseModel):
    scenario_id: str
    label: str
    applied_weights: dict[str, float]
    emphasis_dimension: str | None = None
    results: list[SensitivitySchoolMovement] = Field(default_factory=list)
    summary: str


class SensitivityChoiceSummary(BaseModel):
    school_id: int
    name: str
    base_rank: int | None = None
    average_rank: float
    max_rank_delta: int
    max_fit_delta: float
    explanation: str


class SensitivityCategoryDriver(BaseModel):
    category: str
    average_absolute_fit_delta: float
    affected_school_count: int
    explanation: str


class SensitivityConfidenceImpact(BaseModel):
    school_id: int
    name: str
    max_confidence_delta: float
    explanation: str


class SensitivityResponse(BaseModel):
    ranking_version: str
    baseline_weights: dict[str, float]
    stable_choice_definition: str
    volatile_choice_definition: str
    baseline_results: list[SensitivitySchoolMovement] = Field(default_factory=list)
    scenarios: list[SensitivityScenarioResult] = Field(default_factory=list)
    stable_schools: list[SensitivityChoiceSummary] = Field(default_factory=list)
    volatile_schools: list[SensitivityChoiceSummary] = Field(default_factory=list)
    category_drivers: list[SensitivityCategoryDriver] = Field(default_factory=list)
    confidence_impacts: list[SensitivityConfidenceImpact] = Field(default_factory=list)
    tradeoff_explanations: list[str] = Field(default_factory=list)
    summary_messages: list[str] = Field(default_factory=list)
