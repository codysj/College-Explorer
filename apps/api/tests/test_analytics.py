from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from api.routes.analytics import get_analytics_service
from apps.api.main import app
from schemas.analytics import AnalyticsEventCreate
from services.analytics import AnalyticsService, sanitize_metadata


class FakeAnalyticsRepository:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.events: list[dict[str, object]] = [
            event(1, "ranking_generated", "school", 1, now, {"ranking_version": "v1.0", "rank_position": 1, "fit_score": 91, "confidence_score": 0.9, "top_reasons": ["academic_major_match"], "category_weights": {"academic": 0.4}}),
            event(2, "ranking_generated", "school", 2, now, {"ranking_version": "v1.0", "rank_position": 2, "fit_score": 76, "confidence_score": 0.6, "top_reasons": ["cost_within_budget"], "category_weights": {"cost": 0.4}}),
            event(3, "school_saved", "school", 1, now, {"school_name": "Berkeley Demo University", "ranking_version": "v1.0", "rank_position": 1, "fit_score": 91, "confidence_score": 0.9, "category_weights": {"academic": 0.4}}),
            event(4, "school_compared", "school", 1, now, {"school_name": "Berkeley Demo University", "rank_position": 1, "fit_score": 91}),
            event(5, "school_profile_viewed", "school", 1, now, {"school_name": "Berkeley Demo University"}),
            event(6, "search_performed", "search", None, now, {"filters": {"state": True, "max_net_price": True}, "result_count": 2}),
            event(7, "decision_report_generated", "decision_report", 10, now, {"ranking_version": "v1.0", "report_version": "v2.7", "school_count": 2}),
            event(8, "onboarding_completed", "preference_profile", None, now, {"completion_percent": 100, "category_weights": {"academic": 0.3}}),
        ]

    def create_event(self, user_id: int | None, event_name: str, entity_type: str | None, entity_id: int | None, metadata: dict[str, object]) -> dict[str, object]:
        row = event(len(self.events) + 1, event_name, entity_type, entity_id, datetime.now(UTC), metadata, user_id)
        self.events.append(row)
        return row

    def list_events(self, lookback_days: int = 90, limit: int = 5000) -> list[dict[str, object]]:
        since = datetime.now(UTC) - timedelta(days=lookback_days)
        return [item for item in self.events if item["created_at"] >= since][:limit]


def event(
    event_id: int,
    event_name: str,
    entity_type: str | None,
    entity_id: int | None,
    created_at: datetime,
    metadata: dict[str, object],
    user_id: int | None = 1,
) -> dict[str, object]:
    return {
        "id": event_id,
        "user_id": user_id,
        "event_name": event_name,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "metadata": metadata,
        "created_at": created_at,
    }


def make_service() -> AnalyticsService:
    return AnalyticsService(FakeAnalyticsRepository())


def test_event_metadata_sanitizer_removes_sensitive_fields() -> None:
    sanitized = sanitize_metadata(
        {
            "query": "affordable colleges near home",
            "visit_notes": "private note",
            "aid_offer": 12000,
            "filters": {"state": "CA", "query": "private", "max_net_price": 30000},
            "ranking_version": "v1.0",
            "fit_score": 88.12345,
        }
    )

    assert "query" not in sanitized
    assert "visit_notes" not in sanitized
    assert "aid_offer" not in sanitized
    assert sanitized["filters"] == {"max_net_price": True, "query": True, "state": True}
    assert sanitized["ranking_version"] == "v1.0"
    assert sanitized["fit_score"] == 88.1235


def test_analytics_summary_aggregates_ranking_evaluation() -> None:
    summary = make_service().summary()

    assert any(row.key == "school_saved" and row.count == 1 for row in summary.event_counts)
    assert summary.most_used_filters[0].key in {"state", "max_net_price"}
    assert summary.most_viewed_schools[0].school_name == "Berkeley Demo University"
    assert summary.most_saved_schools[0].school_id == 1
    assert summary.ranking_evaluation.save_rate_by_fit_bucket[0].bucket == "90-100"
    assert summary.ranking_evaluation.save_rate_by_fit_bucket[0].numerator == 1
    assert summary.ranking_evaluation.compare_rate_by_rank_position[0].bucket == "1"
    assert summary.ranking_evaluation.top_reason_code_frequency[0].count >= 1
    assert summary.ranking_version_usage[0].key == "v1.0"
    assert "decision-support" not in summary.privacy_note.lower()


def test_analytics_event_endpoint_sanitizes_payload(client: TestClient) -> None:
    app.dependency_overrides[get_analytics_service] = make_service
    try:
        response = client.post(
            "/analytics/events",
            json={
                "event_name": "school_saved",
                "entity_type": "school",
                "entity_id": 1,
                "metadata": {
                    "ranking_version": "v1.0",
                    "visit_notes": "do not store this",
                    "fit_score": 92,
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["ranking_version"] == "v1.0"
    assert payload["metadata"]["fit_score"] == 92
    assert "visit_notes" not in payload["metadata"]


def test_analytics_summary_endpoint_returns_schema(client: TestClient) -> None:
    app.dependency_overrides[get_analytics_service] = make_service
    try:
        response = client.get("/analytics/summary?lookback_days=30")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking_evaluation"]["ranking_version_distribution"]
    assert payload["privacy_note"]


def test_invalid_analytics_event_rejected(client: TestClient) -> None:
    response = client.post("/analytics/events", json={"event_name": "raw_private_note", "metadata": {}})

    assert response.status_code == 422
