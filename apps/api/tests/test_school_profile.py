from fastapi.testclient import TestClient

from api.routes.schools import get_school_service
from apps.api.main import app
from schemas.schools import (
    SchoolProfileAcademics,
    SchoolProfileCampusLife,
    SchoolProfileCost,
    SchoolProfileOutcomes,
    SchoolProfileResponse,
)
from services.schools import SchoolService
from tests.test_cache_service import make_cache


class FakeProfileService:
    def get_school_profile(self, school_id: int) -> SchoolProfileResponse | None:
        if school_id == 404:
            return None
        if school_id == 2:
            return SchoolProfileResponse(
                school_id=2,
                name="Bayview Technical University",
                city="New Haven",
                state="CT",
                region="Northeast",
                type="Public",
                setting="Urban",
                enrollment=11800,
                acceptance_rate=0.44,
                academics=SchoolProfileAcademics(
                    majors=["Computer Science", "Engineering"],
                    popular_majors=["Computer Science", "Engineering"],
                    graduation_rate=0.78,
                    retention_rate=None,
                    student_faculty_ratio=14.0,
                ),
                cost=SchoolProfileCost(
                    tuition_in_state=15900,
                    tuition_out_state=34900,
                    net_price=None,
                    average_aid=14200,
                    debt_median=23000,
                ),
                outcomes=SchoolProfileOutcomes(
                    median_earnings=68000,
                    completion_rate=None,
                    repayment_rate=0.81,
                    outcome_percentiles=None,
                ),
                campus_life=SchoolProfileCampusLife(
                    sports="DII",
                    greek_life=0.12,
                    housing=True,
                    weather_band=None,
                    diversity_metrics=None,
                    culture_tags=["technical", "urban"],
                ),
                data_fields_missing=[
                    "academics.retention_rate",
                    "cost.net_price",
                    "outcomes.completion_rate",
                    "outcomes.outcome_percentiles",
                    "campus_life.weather_band",
                    "campus_life.diversity_metrics",
                ],
                data_confidence_score=0.7857,
            )
        return SchoolProfileResponse(
            school_id=1,
            name="Adams State College",
            city="Northbridge",
            state="MA",
            region="Northeast",
            type="Public",
            setting="Suburban",
            enrollment=6200,
            acceptance_rate=0.64,
            academics=SchoolProfileAcademics(
                majors=["Biology", "Psychology", "Business"],
                popular_majors=["Biology", "Psychology", "Business"],
                graduation_rate=0.69,
                retention_rate=0.82,
                student_faculty_ratio=15.0,
            ),
            cost=SchoolProfileCost(
                tuition_in_state=14200,
                tuition_out_state=31800,
                net_price=22100,
                average_aid=12600,
                debt_median=21000,
            ),
            outcomes=SchoolProfileOutcomes(
                median_earnings=52000,
                completion_rate=None,
                repayment_rate=0.76,
                outcome_percentiles=None,
            ),
            campus_life=SchoolProfileCampusLife(
                sports="DIII",
                greek_life=0.08,
                housing=True,
                weather_band=None,
                diversity_metrics=None,
                culture_tags=["research", "commuter-friendly", "mid-size"],
            ),
            data_fields_missing=[
                "outcomes.completion_rate",
                "outcomes.outcome_percentiles",
                "campus_life.weather_band",
                "campus_life.diversity_metrics",
            ],
            data_confidence_score=0.8571,
        )


def override_school_service() -> FakeProfileService:
    return FakeProfileService()


def test_valid_school_id_returns_full_profile(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["school_id"] == 1
    assert payload["acceptance_rate"] == 0.64
    assert payload["academics"]["popular_majors"] == ["Biology", "Psychology", "Business"]
    assert payload["cost"]["net_price"] == 22100
    assert payload["outcomes"]["repayment_rate"] == 0.76
    assert payload["campus_life"]["sports"] == "DIII"
    assert payload["fit_score"] is None
    assert payload["similar_schools"] == []


def test_missing_optional_fields_are_null_and_tracked(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/2")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["cost"]["net_price"] is None
    assert payload["academics"]["retention_rate"] is None
    assert "cost.net_price" in payload["data_fields_missing"]
    assert "academics.retention_rate" in payload["data_fields_missing"]


def test_nonexistent_school_id_returns_404(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/404", headers={"X-Request-ID": "test-request"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_404"


def test_confidence_score_calculation_is_returned(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["data_confidence_score"] == 0.8571


def test_response_structure_correctness(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/1")
    finally:
        app.dependency_overrides.clear()

    payload = response.json()
    assert set(payload) == {
        "school_id",
        "name",
        "city",
        "state",
        "region",
        "type",
        "setting",
        "enrollment",
        "acceptance_rate",
        "academics",
        "cost",
        "outcomes",
        "campus_life",
        "data_fields_missing",
        "data_confidence_score",
        "fit_score",
        "category_scores",
        "top_reasons",
        "top_tradeoffs",
        "similar_schools",
    }
    assert set(payload["academics"]) == {
        "majors",
        "popular_majors",
        "graduation_rate",
        "retention_rate",
        "student_faculty_ratio",
    }
    assert set(payload["cost"]) == {
        "tuition_in_state",
        "tuition_out_state",
        "net_price",
        "average_aid",
        "debt_median",
    }
    assert set(payload["outcomes"]) == {
        "median_earnings",
        "completion_rate",
        "repayment_rate",
        "outcome_percentiles",
    }
    assert set(payload["campus_life"]) == {
        "sports",
        "greek_life",
        "housing",
        "weather_band",
        "diversity_metrics",
        "culture_tags",
    }


def test_service_computes_confidence_from_profile_completeness() -> None:
    class FakeRepository:
        def get_school_profile_row(self, school_id: int) -> dict[str, object]:
            return {
                "school_id": school_id,
                "name": "Incomplete College",
                "city": "Mesa",
                "state": "AZ",
                "region": "West",
                "type": "Public",
                "setting": "Urban",
                "enrollment": None,
                "acceptance_rate": None,
                "top_majors": ["Biology"],
                "graduation_rate": None,
                "retention_rate": 0.8,
                "student_faculty_ratio": 16.0,
                "tuition_in_state": 12000,
                "tuition_out_state": None,
                "net_price": 18000,
                "average_aid": None,
                "debt_median": 21000,
                "median_earnings": 50000,
                "repayment_rate": None,
                "housing_available": False,
                "sports_division": None,
                "greek_life_rate": None,
                "culture_tags": ["urban"],
            }

    service = SchoolService.__new__(SchoolService)
    service.repository = FakeRepository()
    service.cache = make_cache()[0]

    profile = service.get_school_profile(10)

    assert profile is not None
    assert profile.enrollment is None
    assert "enrollment" in profile.data_fields_missing
    assert "outcomes.completion_rate" in profile.data_fields_missing
    assert "acceptance_rate" in profile.data_fields_missing
    assert profile.data_confidence_score == 0.5862
