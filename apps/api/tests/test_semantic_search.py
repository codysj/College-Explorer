from fastapi.testclient import TestClient

from api.routes.semantic_search import get_semantic_search_service
from apps.api.main import app
from schemas.preferences import Preference
from schemas.semantic_search import SemanticSearchRequest
from services.semantic_search import (
    EMBEDDING_TYPE,
    LOCAL_EMBEDDING_MODEL,
    LocalHashEmbeddingProvider,
    SemanticSearchService,
    build_search_document,
)


def make_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "school_id": 1,
        "name": "Bayview Technical University",
        "city": "New Haven",
        "state": "CT",
        "region": "Northeast",
        "type": "Public",
        "setting": "Urban",
        "enrollment": 11800,
        "acceptance_rate": 0.52,
        "source_name": "fixture",
        "source_year": 2026,
        "data_version": "test",
        "top_majors": ["Computer Science", "Data Science", "Engineering"],
        "graduation_rate": 0.78,
        "retention_rate": 0.87,
        "student_faculty_ratio": 14.0,
        "tuition_in_state": 15900,
        "tuition_out_state": 34900,
        "net_price": 24400,
        "average_aid": 14200,
        "debt_median": 23000,
        "median_earnings": 68000,
        "repayment_rate": 0.81,
        "housing_available": True,
        "sports_division": "DII",
        "greek_life_rate": 0.12,
        "culture_tags": ["technical", "urban", "career-focused"],
    }
    row.update(overrides)
    return row


class FakeSemanticRepository:
    def __init__(self, rows: list[dict[str, object]], vector_rows: list[dict[str, object]] | None = None) -> None:
        self.rows = rows
        self.vector_rows = vector_rows or []
        self.upserts: list[dict[str, object]] = []

    def get_semantic_document_rows(self) -> list[dict[str, object]]:
        return self.rows

    def upsert_school_embedding(
        self,
        school_id: int,
        embedding_type: str,
        embedding_model: str,
        vector: list[float],
        text_snapshot_hash: str,
    ) -> None:
        self.upserts.append(
            {
                "school_id": school_id,
                "embedding_type": embedding_type,
                "embedding_model": embedding_model,
                "vector": vector,
                "text_snapshot_hash": text_snapshot_hash,
            }
        )

    def get_vector_candidate_rows(
        self,
        query_vector: list[float],
        embedding_type: str,
        embedding_model: str,
        limit: int,
    ) -> list[dict[str, object]]:
        return self.vector_rows[:limit]

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return self.rows


def make_service(
    rows: list[dict[str, object]] | None = None,
    vector_rows: list[dict[str, object]] | None = None,
) -> SemanticSearchService:
    return SemanticSearchService(FakeSemanticRepository(rows or [make_row()], vector_rows))


def test_search_document_generation_includes_structured_fields() -> None:
    document = build_search_document(make_row())

    assert document.school_id == 1
    assert "Bayview Technical University" in document.text
    assert "Data Science" in document.text
    assert "net price 24400" in document.text
    assert "culture tags technical, urban, career-focused" in document.text
    assert len(document.text_snapshot_hash) == 64


def test_embedding_refresh_stores_versioned_metadata() -> None:
    repository = FakeSemanticRepository([make_row()])
    service = SemanticSearchService(repository)

    refreshed = service.refresh_embeddings()

    assert refreshed == 1
    assert repository.upserts[0]["embedding_type"] == EMBEDDING_TYPE
    assert repository.upserts[0]["embedding_model"] == LOCAL_EMBEDDING_MODEL
    assert len(repository.upserts[0]["vector"]) == 64
    assert len(repository.upserts[0]["text_snapshot_hash"]) == 64


def test_local_embedding_provider_is_deterministic() -> None:
    provider = LocalHashEmbeddingProvider()

    first = provider.embed("affordable data science schools near cities")
    second = provider.embed("affordable data science schools near cities")

    assert first == second
    assert len(first) == 64


def test_semantic_endpoint_validates_request(client: TestClient) -> None:
    response = client.post("/semantic-search", json={"query": "ai"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_deterministic_fallback_when_embeddings_are_missing() -> None:
    service = make_service(
        [
            make_row(school_id=1, name="Bayview Technical University"),
            make_row(school_id=2, name="Cedar Hill College", top_majors=["Biology"], setting="Rural"),
        ],
        vector_rows=[],
    )

    response = service.search(SemanticSearchRequest(query="affordable data science schools near cities"))

    assert response.retrieval_mode == "deterministic_fallback"
    assert response.results
    assert response.results[0].school_id == 1
    assert response.results[0].semantic_score is not None


def test_fallback_still_returns_stable_results_for_sparse_queries() -> None:
    service = make_service([make_row()], vector_rows=[])

    response = service.search(SemanticSearchRequest(query="schools like Berkeley but smaller"))

    assert response.retrieval_mode == "deterministic_fallback"
    assert response.total_results == 1
    assert response.results[0].match_reasons


def test_hybrid_reranking_preserves_hard_constraints() -> None:
    rows = [
        make_row(school_id=1, name="Expensive Data Science Institute", net_price=60000, semantic_score=0.99),
        make_row(school_id=2, name="Affordable Data Science College", net_price=18000, semantic_score=0.75),
    ]
    service = make_service(rows, vector_rows=rows)

    response = service.search(
        SemanticSearchRequest(
            query="affordable data science schools near cities",
            preferences=Preference(
                intended_major="Data Science",
                max_annual_cost=30000,
                constraints={"strict_cost": True},
            ),
        )
    )

    assert [result.school_id for result in response.results] == [2]


def test_explanation_reason_tags_are_returned() -> None:
    service = make_service([make_row()], vector_rows=[make_row(semantic_score=0.9)])

    response = service.search(SemanticSearchRequest(query="urban data science career outcomes campus"))

    assert response.results[0].match_reasons
    assert "major_match" in response.results[0].match_reasons
    assert "setting_match" in response.results[0].match_reasons
    assert "outcomes_match" in response.results[0].match_reasons


def test_semantic_endpoint_returns_ranked_response(client: TestClient) -> None:
    def override_semantic_service() -> SemanticSearchService:
        return make_service([make_row()], vector_rows=[])

    app.dependency_overrides[get_semantic_search_service] = override_semantic_service
    try:
        response = client.post(
            "/semantic-search",
            json={
                "query": "large public schools with strong outcomes",
                "filters": {"page": 1, "page_size": 10},
                "preferences": {"constraints": {"preferred_school_types": ["Public"]}},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking_version"] == "v1.0"
    assert payload["embedding_model"] == LOCAL_EMBEDDING_MODEL
    assert payload["results"][0]["fit_score"] is not None
    assert payload["results"][0]["match_reasons"]
