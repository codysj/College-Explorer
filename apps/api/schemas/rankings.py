from pydantic import BaseModel, ConfigDict, Field

from schemas.preferences import Preference
from schemas.schools import SchoolSearchResult, SearchRequest


class RankingScore(BaseModel):
    school_id: int
    fit_score: float = Field(ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    category_scores: dict[str, float] = Field(default_factory=dict)
    reason_codes: list[str] = Field(default_factory=list)
    tradeoff_codes: list[str] = Field(default_factory=list)
    ranking_version: str


class RankingRequest(BaseModel):
    preferences: Preference
    filters: SearchRequest = Field(default_factory=SearchRequest)


class RankingResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ranking_version": "v1.0",
                "results": [
                    {
                        "school_id": 2,
                        "name": "Bayview Technical University",
                        "city": "New Haven",
                        "state": "CT",
                        "type": "Public",
                        "setting": "Urban",
                        "enrollment": 11800,
                        "acceptance_rate": 0.52,
                        "net_price": 24400,
                        "graduation_rate": 0.78,
                        "fit_score": 86.42,
                        "confidence_score": 0.95,
                        "category_scores": {"academic": 92.0, "cost": 82.5},
                        "top_reasons": ["academic_major_match", "cost_within_budget"],
                        "top_tradeoffs": ["admissions_more_selective_than_target"],
                        "ranking_version": "v1.0",
                    }
                ],
                "page": 1,
                "page_size": 20,
                "total_results": 1,
                "has_next": False,
            }
        }
    )

    ranking_version: str
    results: list[SchoolSearchResult] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total_results: int = 0
    has_next: bool = False
