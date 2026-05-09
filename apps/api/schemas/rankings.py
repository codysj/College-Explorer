from pydantic import BaseModel, ConfigDict, Field


class RankingScore(BaseModel):
    school_id: int
    fit_score: float = Field(ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    category_scores: dict[str, float] = Field(default_factory=dict)
    reason_codes: list[str] = Field(default_factory=list)
    tradeoff_codes: list[str] = Field(default_factory=list)


class RankingResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ranking_version": "placeholder",
                "results": [],
            }
        }
    )

    ranking_version: str
    results: list[RankingScore] = Field(default_factory=list)
