from __future__ import annotations

import json
from datetime import datetime
from typing import Literal, TypeAlias

from pydantic import ConfigDict, Field, model_validator

from schemas.base import ApiModel
AnalyticsEventName = Literal[
    "search_performed",
    "semantic_search_performed",
    "school_profile_viewed",
    "school_saved",
    "school_compared",
    "onboarding_completed",
    "ranking_generated",
    "sensitivity_adjusted",
    "decision_report_generated",
]

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list[JsonScalar] | dict[str, JsonScalar]


class AnalyticsEventCreate(ApiModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_name": "school_saved",
                "entity_type": "school",
                "entity_id": 2,
                "metadata": {
                    "source": "search",
                    "rank_position": 3,
                    "fit_score": 86.4,
                    "ranking_version": "v1.0",
                },
            }
        }
    )

    event_name: AnalyticsEventName
    entity_type: str | None = Field(default=None, max_length=40)
    entity_id: int | None = Field(default=None, ge=1)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_metadata_size(self) -> "AnalyticsEventCreate":
        if len(self.metadata) > 40:
            raise ValueError("metadata may contain at most 40 keys")
        if len(json.dumps(self.metadata, default=str)) > 4096:
            raise ValueError("metadata may be at most 4 KB when serialized")
        return self


class AnalyticsEventResponse(ApiModel):
    id: int
    user_id: int | None
    event_name: AnalyticsEventName
    entity_type: str | None
    entity_id: int | None
    metadata: dict[str, JsonValue]
    created_at: datetime | None = None


class AnalyticsMetricCard(ApiModel):
    label: str
    value: int | float | str
    detail: str


class AnalyticsCountRow(ApiModel):
    key: str
    count: int


class AnalyticsSchoolMetric(ApiModel):
    school_id: int
    school_name: str
    count: int


class AnalyticsRateRow(ApiModel):
    bucket: str
    numerator: int
    denominator: int
    rate: float


class AnalyticsDistributionRow(ApiModel):
    bucket: str
    count: int


class RankingEvaluationSummary(ApiModel):
    save_rate_by_fit_bucket: list[AnalyticsRateRow]
    compare_rate_by_rank_position: list[AnalyticsRateRow]
    top_reason_code_frequency: list[AnalyticsCountRow]
    confidence_distribution: list[AnalyticsDistributionRow]
    ranking_version_distribution: list[AnalyticsCountRow]
    category_weight_save_correlations: list[AnalyticsCountRow]
    interpretation_notes: list[str]


class AnalyticsSummaryResponse(ApiModel):
    generated_at: datetime
    lookback_days: int
    event_counts: list[AnalyticsCountRow]
    metric_cards: list[AnalyticsMetricCard]
    most_used_filters: list[AnalyticsCountRow]
    most_viewed_schools: list[AnalyticsSchoolMetric]
    most_saved_schools: list[AnalyticsSchoolMetric]
    compare_frequency: list[AnalyticsCountRow]
    onboarding_completion_rate: AnalyticsRateRow
    save_rate_by_rank_position: list[AnalyticsRateRow]
    report_generation_frequency: list[AnalyticsCountRow]
    ranking_version_usage: list[AnalyticsCountRow]
    ranking_evaluation: RankingEvaluationSummary
    privacy_note: str
    limitations: list[str]
