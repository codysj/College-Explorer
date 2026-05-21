from fastapi.testclient import TestClient

from api.routes.sensitivity import get_sensitivity_service
from apps.api.main import app
from schemas.sensitivity import SensitivityRequest
from services.sensitivity import SensitivityService
from tests.test_ranking_service import make_row


class FakeSensitivityRepository:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.calls = 0

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        self.calls += 1
        return self.rows

    def get_ranking_candidate_rows_by_ids(self, school_ids: list[int]) -> list[dict[str, object]]:
        self.calls += 1
        requested = set(school_ids)
        return [row for row in self.rows if int(row["school_id"]) in requested]


def make_service(rows: list[dict[str, object]] | None = None) -> SensitivityService:
    return SensitivityService(FakeSensitivityRepository(rows or sensitivity_rows()))


def sensitivity_rows() -> list[dict[str, object]]:
    return [
        make_row(school_id=1, name="Balanced State", net_price=25000, median_earnings=62000, acceptance_rate=0.58),
        make_row(
            school_id=2,
            name="Premium Tech",
            net_price=52000,
            average_aid=8000,
            debt_median=34000,
            median_earnings=90000,
            repayment_rate=0.9,
            acceptance_rate=0.18,
            graduation_rate=0.9,
        ),
        make_row(
            school_id=3,
            name="Regional Value",
            net_price=16000,
            median_earnings=47000,
            repayment_rate=0.68,
            acceptance_rate=0.76,
            graduation_rate=0.64,
        ),
    ]


def sensitivity_payload() -> dict[str, object]:
    return {
        "preferences": {
            "intended_major": "Computer Science",
            "max_annual_cost": 30000,
            "weights": {
                "academic": 0.25,
                "cost": 0.2,
                "career": 0.2,
                "campus": 0.1,
                "location": 0.1,
                "admissions_realism": 0.15,
            },
        },
        "scenarios": [
            {"scenario_id": "cost_focus", "label": "Cost sensitivity raised", "weight_adjustments": {"cost_value": 0.55}},
            {"scenario_id": "career_focus", "label": "Career outcomes raised", "weight_adjustments": {"career_outcomes": 0.55}},
        ],
        "candidate_school_ids": [1, 2, 3],
        "filters": {"page": 1, "page_size": 10},
    }


def test_sensitivity_reports_ranking_movement_and_drivers() -> None:
    response = make_service().analyze(SensitivityRequest.model_validate(sensitivity_payload()))

    assert response.ranking_version == "v1.0"
    assert response.baseline_results
    assert len(response.scenarios) == 2
    assert any(item.rank_delta != 0 for scenario in response.scenarios for item in scenario.results)
    assert response.category_drivers
    assert response.tradeoff_explanations


def test_sensitivity_classifies_stable_and_volatile_choices() -> None:
    response = make_service().analyze(SensitivityRequest.model_validate(sensitivity_payload()))

    assert response.stable_choice_definition.startswith("A stable choice")
    assert response.volatile_choice_definition.startswith("A volatile choice")
    assert response.stable_schools or response.volatile_schools
    assert any(
        result.stability in {"stable_choice", "volatile_choice", "watch_choice"}
        for scenario in response.scenarios
        for result in scenario.results
    )


def test_sensitivity_outputs_are_deterministic() -> None:
    request = SensitivityRequest.model_validate(sensitivity_payload())
    service = make_service()

    first = service.analyze(request)
    second = service.analyze(request)

    assert first.model_dump() == second.model_dump()


def test_sensitivity_handles_missing_data_without_zero_penalty() -> None:
    rows = sensitivity_rows()
    rows[0].update(net_price=None, average_aid=None, debt_median=None, median_earnings=None, repayment_rate=None)

    response = make_service(rows).analyze(SensitivityRequest.model_validate(sensitivity_payload()))
    school = next(item for item in response.baseline_results if item.school_id == 1)

    assert school.category_scores["cost"] == 50.0
    assert school.confidence_score < 1


def test_sensitivity_rejects_invalid_weight_inputs(client: TestClient) -> None:
    payload = sensitivity_payload()
    payload["scenarios"] = [
        {"scenario_id": "bad", "label": "Bad", "weight_adjustments": {"cost": 1.5}},
    ]

    response = client.post("/sensitivity", json=payload)

    assert response.status_code == 422


def test_sensitivity_endpoint_returns_schema(client: TestClient) -> None:
    def override_service() -> SensitivityService:
        return make_service()

    app.dependency_overrides[get_sensitivity_service] = override_service
    try:
        response = client.post("/sensitivity", json=sensitivity_payload())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking_version"] == "v1.0"
    assert payload["scenarios"][0]["results"][0]["school_id"]
    assert "stable_choice_definition" in payload
