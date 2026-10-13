import pytest
from fastapi.testclient import TestClient

from api.routes.decision import get_decision_service
from apps.api.main import app
from schemas.decision import DecisionOfferInput, DecisionReportRequest
from schemas.preferences import Preference
from services.decision import DecisionService
from services.ranking_service import RankingService


def make_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "school_id": 1,
        "name": "Berkeley Demo University",
        "city": "Berkeley",
        "state": "CA",
        "region": "West",
        "type": "Public",
        "setting": "Urban",
        "enrollment": 30000,
        "acceptance_rate": 0.16,
        "top_majors": ["Computer Science", "Data Science"],
        "graduation_rate": 0.9,
        "retention_rate": 0.94,
        "student_faculty_ratio": 18,
        "tuition_in_state": 15000,
        "tuition_out_state": 47000,
        "net_price": 26000,
        "average_aid": 18000,
        "debt_median": 16000,
        "median_earnings": 79000,
        "repayment_rate": 0.88,
        "housing_available": True,
        "sports_division": "DI",
        "greek_life_rate": 0.12,
        "culture_tags": ["technical", "urban", "career-focused", "research"],
    }
    row.update(overrides)
    return row


class FakeCandidateRepository:
    def get_ranking_candidate_rows_by_ids(self, school_ids: list[int]) -> list[dict[str, object]]:
        rows = [
            make_row(school_id=1, name="Berkeley Demo University", net_price=26000, median_earnings=79000),
            make_row(school_id=2, name="UCLA Demo College", net_price=24000, median_earnings=70000, graduation_rate=0.86),
        ]
        return [row for row in rows if row["school_id"] in school_ids]


def make_offers(**second_overrides: object) -> list[DecisionOfferInput]:
    return [
        DecisionOfferInput(
            school_id=1, status="finalist", aid_offer=12000, scholarships=8000,
            estimated_yearly_cost=22000, unresolved_concerns=["Housing cost"],
        ),
        DecisionOfferInput(
            **{"school_id": 2, "status": "accepted", "aid_offer": 10000, "scholarships": 6000,
               "estimated_yearly_cost": 18000, **second_overrides}
        ),
    ]


class FakeSchoolRepository:
    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return []


def make_service() -> DecisionService:
    return DecisionService(FakeCandidateRepository(), RankingService(FakeSchoolRepository()))


def test_decision_report_is_deterministic_and_distinguishes_categories() -> None:
    service = make_service()
    request = DecisionReportRequest(
        offers=make_offers(),
        preferences=Preference(
            intended_major="Computer Science",
            max_annual_cost=25000,
            weights={"academic": 0.3, "cost": 0.3, "career": 0.3, "campus": 0.1},
        ),
    )

    first = service.build_report(request)
    second = service.build_report(request)

    assert first.best_overall_fit.school_id == second.best_overall_fit.school_id
    assert first.best_value.school_id == 2
    assert first.strongest_career_upside.school_id == 1
    assert first.lowest_risk.school_id == 2
    assert first.major_tradeoffs
    assert first.disclaimer
    assert first.report_version == "v2.7"
    assert first.finalist_ranking_table[0].rank == 1
    assert first.category_score_table
    assert first.cost_value_comparison
    assert first.sensitivity_highlights
    assert first.unresolved_questions
    assert "deterministic" in first.methodology_note.lower()


def test_missing_data_reduces_decision_confidence() -> None:
    service = make_service()

    report = service.build_report(
        DecisionReportRequest(offers=make_offers(estimated_yearly_cost=None), preferences=Preference())
    )

    assert report.decision_confidence in {"low", "medium"}
    assert "missing_financial_data" in report.confidence_flags


def test_report_rejects_unknown_schools() -> None:
    service = make_service()

    with pytest.raises(ValueError, match="current dataset"):
        service.build_report(DecisionReportRequest(offers=[DecisionOfferInput(school_id=404)]))


def test_report_request_validation(client: TestClient) -> None:
    for offers in (
        [],
        [{"school_id": 1, "estimated_yearly_cost": -1}],
        [{"school_id": 1}, {"school_id": 1}],
        [{"school_id": 1, "unresolved_concerns": ["x" * 301]}],
    ):
        assert client.post("/decision/report", json={"offers": offers}).status_code == 422


def test_offer_store_is_not_exposed(client: TestClient) -> None:
    """Offers travel with each report request; no endpoint returns one visitor's offers to another."""
    assert client.get("/decision/offers").status_code in {404, 405}
    assert client.post("/decision/offers", json={"school_id": 1}).status_code in {404, 405}


def test_decision_endpoints_return_report(client: TestClient) -> None:
    app.dependency_overrides[get_decision_service] = make_service
    try:
        report = client.post(
            "/decision/report",
            json={
                "offers": [offer.model_dump() for offer in make_offers()],
                "preferences": {
                    "intended_major": "Computer Science",
                    "max_annual_cost": 25000,
                    "weights": {"academic": 0.3, "cost": 0.3, "career": 0.3, "campus": 0.1},
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert report.status_code == 200
    assert report.json()["best_value"]["school_id"] == 2
    assert report.json()["printable_report_path"] == "/decision/report"
    assert report.json()["cost_value_comparison"]
