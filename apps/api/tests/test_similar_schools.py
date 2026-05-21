from fastapi.testclient import TestClient

from api.routes.schools import get_similar_schools_service
from apps.api.main import app
from schemas.similar_schools import SimilarSchoolsRequest
from services.cache import CacheService
from services.similar_schools import SimilarSchoolsService, row_matches_variant, score_candidate


def make_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "school_id": 1,
        "name": "Bayview Technical University",
        "city": "New Haven",
        "state": "CT",
        "region": "Northeast",
        "type": "Public",
        "setting": "Urban",
        "enrollment": 12000,
        "acceptance_rate": 0.45,
        "source_name": "fixture",
        "source_year": 2026,
        "data_version": "test",
        "top_majors": ["Computer Science", "Data Science"],
        "graduation_rate": 0.78,
        "retention_rate": 0.86,
        "student_faculty_ratio": 14.0,
        "tuition_in_state": 15000,
        "tuition_out_state": 32000,
        "net_price": 28000,
        "average_aid": 14000,
        "debt_median": 23000,
        "median_earnings": 68000,
        "repayment_rate": 0.82,
        "housing_available": True,
        "sports_division": "DII",
        "greek_life_rate": 0.12,
        "culture_tags": ["technical", "urban", "career-focused"],
    }
    row.update(overrides)
    return row


class FakeSimilarRepository:
    def __init__(self, rows: list[dict[str, object]], vector_rows: list[dict[str, object]] | None = None) -> None:
        self.rows = rows
        self.vector_rows = vector_rows or []
        self.profile_calls = 0

    def get_school_profile_row(self, school_id: int) -> dict[str, object] | None:
        self.profile_calls += 1
        for row in self.rows:
            if int(row["school_id"]) == school_id:
                return row
        return None

    def get_semantic_document_rows(self) -> list[dict[str, object]]:
        return self.rows

    def get_similar_vector_candidate_rows(
        self,
        school_id: int,
        embedding_type: str,
        embedding_model: str,
        limit: int,
    ) -> list[dict[str, object]]:
        return self.vector_rows[:limit]

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return self.rows


class InMemoryBackend:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.values[key] = value
        self.ttls[key] = ttl_seconds

    def delete(self, key: str) -> int:
        return 0

    def delete_prefix(self, prefix: str) -> int:
        return 0


def make_cache() -> CacheService:
    return CacheService(InMemoryBackend(), "v1", 300, 3600, 300)


def make_service(
    rows: list[dict[str, object]] | None = None,
    vector_rows: list[dict[str, object]] | None = None,
    cache: CacheService | None = None,
) -> SimilarSchoolsService:
    return SimilarSchoolsService(FakeSimilarRepository(rows or [make_row()], vector_rows), cache)


def test_variant_constraint_logic_is_directional() -> None:
    source = make_row(net_price=28000, acceptance_rate=0.4, enrollment=20000, graduation_rate=0.75, median_earnings=60000)

    assert row_matches_variant(source, make_row(school_id=2, net_price=20000), SimilarSchoolsRequest(variant="cheaper"))
    assert not row_matches_variant(source, make_row(school_id=3, net_price=30000), SimilarSchoolsRequest(variant="cheaper"))
    assert row_matches_variant(source, make_row(school_id=4, acceptance_rate=0.7), SimilarSchoolsRequest(variant="less_selective"))
    assert row_matches_variant(source, make_row(school_id=5, enrollment=8000), SimilarSchoolsRequest(variant="smaller"))
    assert row_matches_variant(source, make_row(school_id=6, graduation_rate=0.82), SimilarSchoolsRequest(variant="stronger_outcomes"))


def test_excludes_source_school_from_results() -> None:
    rows = [
        make_row(school_id=1, semantic_score=1.0),
        make_row(school_id=2, name="Related Public College", semantic_score=0.8),
    ]
    service = make_service(rows, vector_rows=rows)

    response = service.get_similar_schools(1, SimilarSchoolsRequest())

    assert response is not None
    assert [result.school_id for result in response.results] == [2]


def test_deterministic_fallback_when_embeddings_are_unavailable() -> None:
    rows = [
        make_row(school_id=1),
        make_row(school_id=2, name="Urban Technical College"),
    ]
    service = make_service(rows, vector_rows=[])

    response = service.get_similar_schools(1, SimilarSchoolsRequest())

    assert response is not None
    assert response.retrieval_mode == "deterministic_fallback"
    assert response.results[0].school_id == 2


def test_response_schema_validation_via_endpoint(client: TestClient) -> None:
    service = make_service(
        [make_row(school_id=1), make_row(school_id=2, name="Urban Technical College")],
        vector_rows=[make_row(school_id=2, name="Urban Technical College", enrollment=8000, semantic_score=0.9)],
    )

    def override_service() -> SimilarSchoolsService:
        return service

    app.dependency_overrides[get_similar_schools_service] = override_service
    try:
        response = client.get("/schools/1/similar", params={"variant": "smaller"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_school_id"] == 1
    assert payload["variant_applied"] == "smaller"
    assert payload["results"][0]["similarity_score"] >= 0
    assert payload["results"][0]["variant_applied"] == "smaller"
    assert payload["results"][0]["ranking_version"] == "v1.0"


def test_cache_avoids_recomputing_similar_schools() -> None:
    cache = make_cache()
    repository = FakeSimilarRepository(
        [make_row(school_id=1), make_row(school_id=2, name="Urban Technical College")],
        vector_rows=[make_row(school_id=2, name="Urban Technical College", semantic_score=0.9)],
    )
    service = SimilarSchoolsService(repository, cache)

    first = service.get_similar_schools(1, SimilarSchoolsRequest())
    second = service.get_similar_schools(1, SimilarSchoolsRequest())

    assert first == second
    assert repository.profile_calls == 1


def test_empty_result_handling() -> None:
    service = make_service([make_row(school_id=1)], vector_rows=[])

    response = service.get_similar_schools(1, SimilarSchoolsRequest())

    assert response is not None
    assert response.results == []
    assert response.total_results == 0
    assert response.has_next is False


def test_variant_scoring_rewards_lower_price_for_cheaper() -> None:
    source = make_row(net_price=30000)
    cheap = score_candidate(source, make_row(school_id=2, net_price=18000), "cheaper")
    expensive = score_candidate(source, make_row(school_id=3, net_price=29000), "cheaper")

    assert cheap.score > expensive.score
    assert "lower_net_price" in cheap.reasons
