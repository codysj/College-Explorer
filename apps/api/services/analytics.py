from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Iterable

from repositories.analytics import AnalyticsRepository
from schemas.analytics import (
    AnalyticsCountRow,
    AnalyticsDistributionRow,
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsMetricCard,
    AnalyticsRateRow,
    AnalyticsSchoolMetric,
    AnalyticsSummaryResponse,
    RankingEvaluationSummary,
)
from services.ranking_service import RANKING_VERSION

PRIVACY_NOTE = (
    "Analytics events are product telemetry only. They avoid sensitive notes, free-form search text, aid details, "
    "scholarship amounts, student essays, emails, and raw preference narratives."
)

LIMITATIONS = [
    "Correlation metrics are descriptive and must not be interpreted as causal evidence.",
    "Local demo data can create self-selection bias because users choose which schools to save or compare.",
    "Incomplete public-data fields lower ranking confidence and can affect measured save/compare rates.",
    "Prestige and selectivity preferences may be overrepresented when users manually choose finalists.",
    "Browser-local workflows mean V2.8 analytics are a foundation, not production identity-scoped measurement.",
]

SENSITIVE_KEYS = {
    "aid_offer",
    "scholarships",
    "estimated_yearly_cost",
    "annual_loan_amount",
    "visit_notes",
    "unresolved_concerns",
    "parent_priority_notes",
    "student_priority_notes",
    "email",
    "query",
    "raw_query",
    "intended_major",
    "home_state",
    "max_annual_cost",
}

ALLOWED_METADATA_KEYS = {
    "source",
    "school_name",
    "result_count",
    "page",
    "page_size",
    "filters",
    "filter_keys",
    "query_present",
    "query_length",
    "retrieval_mode",
    "ranking_version",
    "ranking_result_count",
    "rank_position",
    "fit_score",
    "confidence_score",
    "confidence_bucket",
    "top_reasons",
    "top_tradeoffs",
    "category_scores",
    "category_weights",
    "school_count",
    "candidate_count",
    "scenario_count",
    "emphasis_dimension",
    "report_version",
    "decision_confidence",
    "status",
    "saved_status",
    "completed_steps",
    "total_steps",
    "completion_percent",
}


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def log_event(self, request: AnalyticsEventCreate) -> AnalyticsEventResponse:
        metadata = sanitize_metadata(request.metadata)
        row = self.repository.create_event(
            user_id=request.user_id,
            event_name=request.event_name,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            metadata=metadata,
        )
        return AnalyticsEventResponse(
            id=int(row["id"]),
            user_id=row["user_id"],
            event_name=row["event_name"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            metadata=row["metadata"],
            created_at=row.get("created_at"),
        )

    def try_log_event(self, request: AnalyticsEventCreate) -> None:
        try:
            self.log_event(request)
        except Exception:
            return

    def summary(self, lookback_days: int = 90) -> AnalyticsSummaryResponse:
        events = self.repository.list_events(lookback_days=lookback_days)
        event_counts = count_rows(event["event_name"] for event in events)
        viewed = school_metrics(events, "school_profile_viewed")
        saved = school_metrics(events, "school_saved")
        ranking_eval = ranking_evaluation(events)
        onboarding_rate = onboarding_completion_rate(events)
        report_frequency = count_rows(day_key(event) for event in events if event["event_name"] == "decision_report_generated")
        ranking_versions = count_rows(
            metadata(event).get("ranking_version", "unknown")
            for event in events
            if metadata(event).get("ranking_version") or event["event_name"] in {"ranking_generated", "decision_report_generated", "sensitivity_adjusted"}
        )
        if not ranking_versions:
            ranking_versions = [AnalyticsCountRow(key=RANKING_VERSION, count=0)]

        return AnalyticsSummaryResponse(
            generated_at=datetime.now(UTC),
            lookback_days=lookback_days,
            event_counts=event_counts,
            metric_cards=metric_cards(events, onboarding_rate),
            most_used_filters=most_used_filters(events),
            most_viewed_schools=viewed,
            most_saved_schools=saved,
            compare_frequency=count_rows(day_key(event) for event in events if event["event_name"] == "school_compared"),
            onboarding_completion_rate=onboarding_rate,
            save_rate_by_rank_position=rate_by_rank_position(events, "school_saved"),
            report_generation_frequency=report_frequency,
            ranking_version_usage=ranking_versions,
            ranking_evaluation=ranking_eval,
            privacy_note=PRIVACY_NOTE,
            limitations=LIMITATIONS,
        )


def sanitize_metadata(metadata: dict[str, object]) -> dict[str, object]:
    sanitized: dict[str, object] = {}
    for key, value in metadata.items():
        if key in SENSITIVE_KEYS or key not in ALLOWED_METADATA_KEYS:
            continue
        sanitized_value = sanitize_value(key, value)
        if sanitized_value is not None:
            sanitized[key] = sanitized_value
    return sanitized


def sanitize_value(key: str, value: object) -> object | None:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return round(float(value), 4) if isinstance(value, float) else value
    if isinstance(value, str):
        return value[:80]
    if isinstance(value, list):
        return [sanitize_value(key, item) for item in value[:12] if sanitize_value(key, item) is not None]
    if isinstance(value, dict):
        if key == "filters":
            return {str(filter_key): True for filter_key, filter_value in sorted(value.items()) if filter_value not in (None, "", [], {})}
        if key in {"category_scores", "category_weights"}:
            return {
                str(nested_key): round(float(nested_value), 4)
                for nested_key, nested_value in sorted(value.items())
                if isinstance(nested_value, int | float)
            }
    return None


def metadata(event: dict[str, object]) -> dict[str, object]:
    value = event.get("metadata")
    return value if isinstance(value, dict) else {}


def day_key(event: dict[str, object]) -> str:
    created_at = event.get("created_at")
    return created_at.date().isoformat() if isinstance(created_at, datetime) else "unknown"


def count_rows(values: Iterable[object], limit: int = 10) -> list[AnalyticsCountRow]:
    counter = Counter(str(value) for value in values if value not in (None, ""))
    return [AnalyticsCountRow(key=key, count=count) for key, count in counter.most_common(limit)]


def school_metrics(events: list[dict[str, object]], event_name: str) -> list[AnalyticsSchoolMetric]:
    counts: Counter[int] = Counter()
    names: dict[int, str] = {}
    for event in events:
        if event["event_name"] != event_name or event.get("entity_type") != "school" or event.get("entity_id") is None:
            continue
        school_id = int(event["entity_id"])
        counts[school_id] += 1
        names[school_id] = str(metadata(event).get("school_name") or f"School {school_id}")
    return [
        AnalyticsSchoolMetric(school_id=school_id, school_name=names.get(school_id, f"School {school_id}"), count=count)
        for school_id, count in counts.most_common(10)
    ]


def most_used_filters(events: list[dict[str, object]]) -> list[AnalyticsCountRow]:
    values: list[str] = []
    for event in events:
        if event["event_name"] not in {"search_performed", "semantic_search_performed"}:
            continue
        filters = metadata(event).get("filters")
        if isinstance(filters, dict):
            values.extend(str(key) for key, enabled in filters.items() if enabled)
        keys = metadata(event).get("filter_keys")
        if isinstance(keys, list):
            values.extend(str(key) for key in keys)
    return count_rows(values)


def metric_cards(events: list[dict[str, object]], onboarding_rate: AnalyticsRateRow) -> list[AnalyticsMetricCard]:
    counts = Counter(str(event["event_name"]) for event in events)
    return [
        AnalyticsMetricCard(label="Searches", value=counts["search_performed"] + counts["semantic_search_performed"], detail="Structured and semantic search events."),
        AnalyticsMetricCard(label="Saves", value=counts["school_saved"], detail="Privacy-safe school save events."),
        AnalyticsMetricCard(label="Compares", value=counts["school_compared"], detail="Schools added to comparison."),
        AnalyticsMetricCard(label="Reports", value=counts["decision_report_generated"], detail="Decision reports generated."),
        AnalyticsMetricCard(label="Onboarding completion", value=f"{round(onboarding_rate.rate * 100)}%", detail="Completed profiles divided by observed starts/completions."),
    ]


def onboarding_completion_rate(events: list[dict[str, object]]) -> AnalyticsRateRow:
    completed = sum(1 for event in events if event["event_name"] == "onboarding_completed")
    starts = sum(1 for event in events if event["event_name"] == "search_performed" and metadata(event).get("source") == "onboarding")
    denominator = max(completed + starts, completed, 1)
    return AnalyticsRateRow(bucket="onboarding", numerator=completed, denominator=denominator, rate=round(completed / denominator, 4))


def rate_by_rank_position(events: list[dict[str, object]], event_name: str) -> list[AnalyticsRateRow]:
    ranking_exposures: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    for event in events:
        rank = metadata(event).get("rank_position")
        if not isinstance(rank, int | float):
            continue
        bucket = rank_bucket(int(rank))
        if event["event_name"] == "ranking_generated":
            ranking_exposures[bucket] += 1
        if event["event_name"] == event_name:
            actions[bucket] += 1
    return [
        AnalyticsRateRow(
            bucket=bucket,
            numerator=actions[bucket],
            denominator=max(ranking_exposures[bucket], actions[bucket], 1),
            rate=round(actions[bucket] / max(ranking_exposures[bucket], actions[bucket], 1), 4),
        )
        for bucket in ["1", "2-3", "4-5", "6-10", "11+"]
    ]


def ranking_evaluation(events: list[dict[str, object]]) -> RankingEvaluationSummary:
    return RankingEvaluationSummary(
        save_rate_by_fit_bucket=rate_by_fit_bucket(events),
        compare_rate_by_rank_position=rate_by_rank_position(events, "school_compared"),
        top_reason_code_frequency=reason_code_frequency(events),
        confidence_distribution=confidence_distribution(events),
        ranking_version_distribution=count_rows(metadata(event).get("ranking_version", "unknown") for event in events),
        category_weight_save_correlations=category_weight_save_correlations(events),
        interpretation_notes=[
            "Save and compare rates describe observed behavior; they do not prove that ranking caused the action.",
            "High-fit save rates are most useful after authenticated persistence and larger real usage samples exist.",
            "Reason-code and confidence distributions help detect whether ranking explanations are too narrow or data-limited.",
        ],
    )


def rate_by_fit_bucket(events: list[dict[str, object]]) -> list[AnalyticsRateRow]:
    exposures: Counter[str] = Counter()
    saves: Counter[str] = Counter()
    for event in events:
        fit_score = metadata(event).get("fit_score")
        if not isinstance(fit_score, int | float):
            continue
        bucket = fit_bucket(float(fit_score))
        if event["event_name"] == "ranking_generated":
            exposures[bucket] += 1
        if event["event_name"] == "school_saved":
            saves[bucket] += 1
    return [
        AnalyticsRateRow(bucket=bucket, numerator=saves[bucket], denominator=max(exposures[bucket], saves[bucket], 1), rate=round(saves[bucket] / max(exposures[bucket], saves[bucket], 1), 4))
        for bucket in ["90-100", "80-89", "70-79", "60-69", "<60", "unknown"]
    ]


def reason_code_frequency(events: list[dict[str, object]]) -> list[AnalyticsCountRow]:
    reason_codes: list[str] = []
    for event in events:
        reasons = metadata(event).get("top_reasons")
        if isinstance(reasons, list):
            reason_codes.extend(str(reason) for reason in reasons)
    return count_rows(reason_codes)


def confidence_distribution(events: list[dict[str, object]]) -> list[AnalyticsDistributionRow]:
    counts: Counter[str] = Counter()
    for event in events:
        confidence = metadata(event).get("confidence_score")
        if isinstance(confidence, int | float):
            counts[confidence_bucket(float(confidence))] += 1
        elif metadata(event).get("confidence_bucket"):
            counts[str(metadata(event)["confidence_bucket"])] += 1
    return [AnalyticsDistributionRow(bucket=bucket, count=counts[bucket]) for bucket in ["high", "medium", "low", "unknown"]]


def category_weight_save_correlations(events: list[dict[str, object]]) -> list[AnalyticsCountRow]:
    saved_weight_counts: Counter[str] = Counter()
    for event in events:
        if event["event_name"] != "school_saved":
            continue
        weights = metadata(event).get("category_weights")
        if not isinstance(weights, dict):
            continue
        top = sorted(
            ((float(value), str(key)) for key, value in weights.items() if isinstance(value, int | float)),
            key=lambda item: (-item[0], item[1]),
        )
        if top:
            saved_weight_counts[top[0][1]] += 1
    return [AnalyticsCountRow(key=key, count=count) for key, count in saved_weight_counts.most_common(6)]


def rank_bucket(rank: int) -> str:
    if rank <= 1:
        return "1"
    if rank <= 3:
        return "2-3"
    if rank <= 5:
        return "4-5"
    if rank <= 10:
        return "6-10"
    return "11+"


def fit_bucket(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 90:
        return "90-100"
    if score >= 80:
        return "80-89"
    if score >= 70:
        return "70-79"
    if score >= 60:
        return "60-69"
    return "<60"


def confidence_bucket(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 0.8:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"
