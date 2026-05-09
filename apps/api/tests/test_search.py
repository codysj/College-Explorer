from fastapi.testclient import TestClient

from api.routes.schools import get_school_service
from apps.api.main import app
from schemas.schools import SchoolSearchResult, SearchRequest, SearchResponse


class FakeSchoolService:
    records = [
        SchoolSearchResult(
            school_id=1,
            name="Adams State College",
            city="Northbridge",
            state="MA",
            type="Public",
            setting="Suburban",
            enrollment=6200,
            acceptance_rate=0.64,
            net_price=22100,
            graduation_rate=0.69,
        ),
        SchoolSearchResult(
            school_id=2,
            name="Bayview Technical University",
            city="New Haven",
            state="CT",
            type="Public",
            setting="Urban",
            enrollment=11800,
            acceptance_rate=0.52,
            net_price=24400,
            graduation_rate=0.78,
        ),
        SchoolSearchResult(
            school_id=3,
            name="Golden Gate Metropolitan University",
            city="San Francisco",
            state="CA",
            type="Private",
            setting="Urban",
            enrollment=7400,
            acceptance_rate=0.32,
            net_price=37200,
            graduation_rate=0.85,
        ),
    ]

    def search_schools(self, filters: SearchRequest) -> SearchResponse:
        results = self.records
        if filters.state:
            results = [record for record in results if record.state == filters.state.upper()]
        if filters.min_net_price is not None:
            results = [record for record in results if record.net_price is not None and record.net_price >= filters.min_net_price]
        if filters.max_net_price is not None:
            results = [record for record in results if record.net_price is not None and record.net_price <= filters.max_net_price]
        if filters.min_enrollment is not None:
            results = [record for record in results if record.enrollment is not None and record.enrollment >= filters.min_enrollment]
        if filters.max_enrollment is not None:
            results = [record for record in results if record.enrollment is not None and record.enrollment <= filters.max_enrollment]

        total_results = len(results)
        start = (filters.page - 1) * filters.page_size
        end = start + filters.page_size
        page_results = results[start:end]
        return SearchResponse(
            results=page_results,
            page=filters.page,
            page_size=filters.page_size,
            total_results=total_results,
            has_next=end < total_results,
        )


def override_school_service() -> FakeSchoolService:
    return FakeSchoolService()


def test_basic_search_returns_results(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/search")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_results"] == 3
    assert payload["results"][0]["school_id"] == 1
    assert payload["results"][0]["fit_score"] is None
    assert payload["results"][0]["top_reasons"] == []


def test_filter_by_state(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/search", params={"state": "CA"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_results"] == 1
    assert payload["results"][0]["state"] == "CA"


def test_numeric_range_filter_works(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get(
            "/schools/search",
            params={"min_net_price": 23000, "max_net_price": 30000},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_results"] == 1
    assert payload["results"][0]["net_price"] == 24400


def test_pagination_correctness(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/search", params={"page": 2, "page_size": 1})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 2
    assert payload["page_size"] == 1
    assert payload["total_results"] == 3
    assert payload["has_next"] is True
    assert payload["results"][0]["school_id"] == 2


def test_invalid_range_returns_error(client: TestClient) -> None:
    response = client.get(
        "/schools/search",
        params={"min_enrollment": 10000, "max_enrollment": 1000},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"


def test_empty_result_case(client: TestClient) -> None:
    app.dependency_overrides[get_school_service] = override_school_service
    try:
        response = client.get("/schools/search", params={"state": "ZZ"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []
    assert payload["total_results"] == 0
    assert payload["has_next"] is False
