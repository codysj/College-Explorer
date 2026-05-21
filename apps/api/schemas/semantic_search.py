from pydantic import BaseModel, ConfigDict, Field

from schemas.preferences import Preference
from schemas.schools import SchoolSearchResult, SearchRequest


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=240)
    filters: SearchRequest = Field(default_factory=SearchRequest)
    preferences: Preference = Field(default_factory=Preference)
    candidate_limit: int = Field(default=50, ge=1, le=200)


class SemanticSearchResult(SchoolSearchResult):
    semantic_score: float | None = Field(default=None, ge=0, le=1)
    match_reasons: list[str] = Field(default_factory=list)


class SemanticSearchResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ranking_version": "v1.0",
                "embedding_model": "local-hash-embedding-v1",
                "embedding_type": "school_search_document",
                "retrieval_mode": "deterministic_fallback",
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
                        "top_tradeoffs": [],
                        "ranking_version": "v1.0",
                        "semantic_score": 0.71,
                        "match_reasons": ["major_match", "setting_match", "cost_value_match"],
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
    embedding_model: str
    embedding_type: str
    retrieval_mode: str
    results: list[SemanticSearchResult] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total_results: int = 0
    has_next: bool = False
