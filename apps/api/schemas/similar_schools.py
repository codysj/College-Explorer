from typing import Literal

from pydantic import BaseModel, Field, model_validator


SimilarityVariant = Literal[
    "general",
    "cheaper",
    "less_selective",
    "smaller",
    "stronger_outcomes",
    "closer_to_home",
]


class SimilarSchoolsRequest(BaseModel):
    variant: SimilarityVariant = "general"
    state: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=32)
    type: str | None = Field(default=None, max_length=32)
    setting: str | None = Field(default=None, max_length=32)
    home_state: str | None = Field(default=None, min_length=2, max_length=2)
    min_net_price: int | None = Field(default=None, ge=0)
    max_net_price: int | None = Field(default=None, ge=0)
    min_acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    max_acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    min_graduation_rate: float | None = Field(default=None, ge=0, le=1)
    min_enrollment: int | None = Field(default=None, ge=0)
    max_enrollment: int | None = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=6, ge=1, le=12)
    candidate_limit: int = Field(default=50, ge=1, le=200)

    @model_validator(mode="after")
    def validate_ranges(self) -> "SimilarSchoolsRequest":
        ranges = [
            ("min_net_price", self.min_net_price, "max_net_price", self.max_net_price),
            ("min_acceptance_rate", self.min_acceptance_rate, "max_acceptance_rate", self.max_acceptance_rate),
            ("min_enrollment", self.min_enrollment, "max_enrollment", self.max_enrollment),
        ]
        for min_name, min_value, max_name, max_value in ranges:
            if min_value is not None and max_value is not None and min_value > max_value:
                raise ValueError(f"{min_name} cannot be greater than {max_name}")
        return self


class SimilarSchoolResult(BaseModel):
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
    median_earnings: int | None = None
    similarity_score: float = Field(ge=0, le=1)
    fit_score: float | None = Field(default=None, ge=0, le=100)
    top_reasons: list[str] = Field(default_factory=list)
    top_tradeoffs: list[str] = Field(default_factory=list)
    variant_applied: SimilarityVariant
    ranking_version: str


class SimilarSchoolsResponse(BaseModel):
    source_school_id: int
    variant: SimilarityVariant
    variant_applied: SimilarityVariant
    ranking_version: str
    embedding_model: str
    embedding_type: str
    retrieval_mode: str
    results: list[SimilarSchoolResult] = Field(default_factory=list)
    page: int = 1
    page_size: int = 6
    total_results: int = 0
    has_next: bool = False
