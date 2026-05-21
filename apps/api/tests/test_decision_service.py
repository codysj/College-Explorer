from fastapi.testclient import TestClient

from api.routes.decision import get_decision_service
from apps.api.main import app
from schemas.decision import DecisionOfferCreate, DecisionReportRequest
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


class FakeDecisionRepository:
    def __init__(self) -> None:
        self.offers = [
            {
                "id": 1,
                "user_id": 1,
                "school_id": 1,
                "status": "finalist",
                "aid_offer": 12000,
                "scholarships": 8000,
                "estimated_yearly_cost": 22000,
                "visit_notes": "Strong academic visit.",
                "unresolved_concerns": ["Housing cost"],
                "parent_priority_notes": "Keep debt low.",
                "student_priority_notes": "Career access matters.",
                "created_at": None,
                "updated_at": None,
                "school_name": "Berkeley Demo University",
                "city": "Berkeley",
                "state": "CA",
            },
            {
                "id": 2,
                "user_id": 1,
                "school_id": 2,
                "status": "accepted",
                "aid_offer": 10000,
                "scholarships": 6000,
                "estimated_yearly_cost": 18000,
                "visit_notes": "",
                "unresolved_concerns": [],
                "parent_priority_notes": "",
                "student_priority_notes": "",
                "created_at": None,
                "updated_at": None,
                "school_name": "UCLA Demo College",
                "city": "Los Angeles",
                "state": "CA",
            },
        ]
        self.snapshots: list[dict[str, object]] = []

    def upsert_offer(self, request: DecisionOfferCreate) -> dict[str, object]:
        self.offers[0] = {**self.offers[0], **request.model_dump(), "school_name": "Berkeley Demo University", "city": "Berkeley", "state": "CA"}
        return self.offers[0]

    def get_offer_rows(self, user_id: int, school_ids: list[int] | None = None) -> list[dict[str, object]]:
        rows = [offer for offer in self.offers if offer["user_id"] == user_id]
        if school_ids:
            rows = [offer for offer in rows if offer["school_id"] in school_ids]
        return rows

    def get_decision_candidate_rows(self, school_ids: list[int]) -> list[dict[str, object]]:
        rows = [
            make_row(school_id=1, name="Berkeley Demo University", net_price=26000, median_earnings=79000),
            make_row(school_id=2, name="UCLA Demo College", net_price=24000, median_earnings=70000, graduation_rate=0.86),
        ]
        return [row for row in rows if row["school_id"] in school_ids]

    def save_snapshot(self, user_id: int, summary_version: str, school_ids: list[int], summary: dict[str, object]) -> int:
        self.snapshots.append({"user_id": user_id, "summary_version": summary_version, "school_ids": school_ids, "summary": summary})
        return 99


class FakeSchoolRepository:
    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return []


def make_service() -> DecisionService:
    return DecisionService(FakeDecisionRepository(), RankingService(FakeSchoolRepository()))


def test_offer_upsert_returns_decision_offer() -> None:
    service = make_service()

    offer = service.upsert_offer(
        DecisionOfferCreate(
            school_id=1,
            status="finalist",
            estimated_yearly_cost=21000,
            unresolved_concerns=["Confirm housing"],
        )
    )

    assert offer.school_id == 1
    assert offer.status == "finalist"
    assert offer.estimated_yearly_cost == 21000


def test_decision_report_is_deterministic_and_distinguishes_categories() -> None:
    service = make_service()
    request = DecisionReportRequest(
        user_id=1,
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


def test_missing_data_reduces_decision_confidence() -> None:
    repository = FakeDecisionRepository()
    repository.offers[1]["estimated_yearly_cost"] = None
    service = DecisionService(repository, RankingService(FakeSchoolRepository()))

    report = service.build_report(DecisionReportRequest(user_id=1, preferences=Preference()))

    assert report.decision_confidence in {"low", "medium"}
    assert "missing_financial_data" in report.confidence_flags


def test_invalid_financial_inputs_return_validation_error(client: TestClient) -> None:
    response = client.post(
        "/decision/offers",
        json={"school_id": 1, "estimated_yearly_cost": -1},
    )

    assert response.status_code == 422


def test_decision_endpoints_return_report(client: TestClient) -> None:
    app.dependency_overrides[get_decision_service] = make_service
    try:
        offers = client.get("/decision/offers")
        report = client.post(
            "/decision/report",
            json={
                "user_id": 1,
                "preferences": {
                    "intended_major": "Computer Science",
                    "max_annual_cost": 25000,
                    "weights": {"academic": 0.3, "cost": 0.3, "career": 0.3, "campus": 0.1},
                },
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert offers.status_code == 200
    assert len(offers.json()["offers"]) == 2
    assert report.status_code == 200
    assert report.json()["best_value"]["school_id"] == 2
