from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SchoolSort = Literal[
    "name",
    "acceptance_rate",
    "graduation_rate",
    "net_price",
    "enrollment",
]
SortDirection = Literal["asc", "desc"]


class SchoolSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unitid: int
    name: str
    city: str
    state: str
    region: str
    type: str
    setting: str
    undergraduate_enrollment: int | None = None
    acceptance_rate: float | None = None


class SchoolProfile(BaseModel):
    school: SchoolSummary
    top_majors: list[str] = Field(default_factory=list)
    graduation_rate: float | None = None
    net_price: int | None = None
    median_earnings: int | None = None
    campus_tags: list[str] = Field(default_factory=list)


class SchoolProfileAcademics(BaseModel):
    majors: list[str] | None = None
    popular_majors: list[str] | None = None
    graduation_rate: float | None = None
    retention_rate: float | None = None
    student_faculty_ratio: float | None = None


class SchoolProfileCost(BaseModel):
    tuition_in_state: int | None = None
    tuition_out_state: int | None = None
    net_price: int | None = None
    average_aid: int | None = None
    debt_median: int | None = None


class SchoolProfileOutcomes(BaseModel):
    median_earnings: int | None = None
    completion_rate: float | None = None
    repayment_rate: float | None = None
    outcome_percentiles: dict[str, float] | None = None


class SchoolProfileCampusLife(BaseModel):
    sports: str | None = None
    greek_life: float | None = None
    housing: bool | None = None
    weather_band: str | None = None
    diversity_metrics: dict[str, float] | None = None
    culture_tags: list[str] | None = None


class SchoolProfileResponse(BaseModel):
    school_id: int
    name: str
    city: str
    state: str
    region: str
    type: str
    setting: str
    enrollment: int | None = None
    acceptance_rate: float | None = None
    academics: SchoolProfileAcademics
    cost: SchoolProfileCost
    outcomes: SchoolProfileOutcomes
    campus_life: SchoolProfileCampusLife
    data_fields_missing: list[str] = Field(default_factory=list)
    data_confidence_score: float
    fit_score: float | None = None
    category_scores: dict[str, float] = Field(default_factory=dict)
    top_reasons: list[str] = Field(default_factory=list)
    top_tradeoffs: list[str] = Field(default_factory=list)
    similar_schools: list[dict[str, object]] = Field(default_factory=list)


class SchoolSearchResult(BaseModel):
    school_id: int
    name: str
    city: str
    state: str
    type: str
    setting: str
    enrollment: int | None = None
    acceptance_rate: float | None = None
    net_price: int | None = None
    graduation_rate: float | None = None
    fit_score: float | None = None
    confidence_score: float | None = None
    category_scores: dict[str, float] = Field(default_factory=dict)
    top_reasons: list[str] = Field(default_factory=list)
    top_tradeoffs: list[str] = Field(default_factory=list)
    ranking_version: str | None = None


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=32)
    type: str | None = Field(default=None, max_length=32)
    setting: str | None = Field(default=None, max_length=32)
    min_enrollment: int | None = Field(default=None, ge=0)
    max_enrollment: int | None = Field(default=None, ge=0)
    min_net_price: int | None = Field(default=None, ge=0)
    max_net_price: int | None = Field(default=None, ge=0)
    min_acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    max_acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    min_graduation_rate: float | None = Field(default=None, ge=0, le=1)
    max_graduation_rate: float | None = Field(default=None, ge=0, le=1)
    sort: SchoolSort = "name"
    direction: SortDirection = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

    @model_validator(mode="after")
    def validate_ranges(self) -> "SearchRequest":
        ranges = [
            ("min_enrollment", self.min_enrollment, "max_enrollment", self.max_enrollment),
            ("min_net_price", self.min_net_price, "max_net_price", self.max_net_price),
            ("min_acceptance_rate", self.min_acceptance_rate, "max_acceptance_rate", self.max_acceptance_rate),
            ("min_graduation_rate", self.min_graduation_rate, "max_graduation_rate", self.max_graduation_rate),
        ]
        for min_name, min_value, max_name, max_value in ranges:
            if min_value is not None and max_value is not None and min_value > max_value:
                raise ValueError(f"{min_name} cannot be greater than {max_name}")
        return self


class SearchResponse(BaseModel):
    results: list[SchoolSearchResult] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total_results: int = 0
    has_next: bool = False
