from fastapi.testclient import TestClient

from api.routes.semantic_search import get_semantic_search_service
from apps.api.main import app
from schemas.preferences import Preference
from schemas.schools import SearchRequest
from schemas.semantic_search import SemanticSearchRequest
from services.ranking_service import RANKING_VERSION
from services.semantic_search import (
    DIVISION_WORDS,
    EMBEDDING_TYPE,
    LOCAL_EMBEDDING_MODEL,
    STATE_NAMES,
    LocalHashEmbeddingProvider,
    SemanticSearchService,
    build_search_document,
    row_matches_filters,
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

    def get_semantic_document_rows(self, filters: object = None) -> list[dict[str, object]]:
        return [row for row in self.rows if filters is None or row_matches_filters(row, filters)]

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
        filters: object = None,
    ) -> list[dict[str, object]]:
        eligible = [row for row in self.vector_rows if filters is None or row_matches_filters(row, filters)]
        return eligible[:limit]

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return self.rows


def make_service(
    rows: list[dict[str, object]] | None = None,
    vector_rows: list[dict[str, object]] | None = None,
) -> SemanticSearchService:
    return SemanticSearchService(FakeSemanticRepository(rows or [make_row()], vector_rows))


def test_search_document_generation_includes_structured_fields() -> None:
    row = make_row()
    document = build_search_document(row)

    assert document.school_id == 1
    assert "Bayview Technical University" in document.text
    assert "Data Science" in document.text
    assert "technical, urban, career-focused" in document.text
    assert len(document.text_snapshot_hash) == 64


def test_search_document_spells_out_codes_and_drops_shared_boilerplate() -> None:
    """Document v3.0: codes become words, and nothing appears in every school's text.

    The v2.2 labels ("in-state tuition", "cost value affordability:") and the source line
    were identical across documents, so words like "in" and "cost" matched every school.
    """
    row = make_row()
    text = build_search_document(row).text

    assert STATE_NAMES[str(row["state"])] in text
    assert DIVISION_WORDS[str(row["sports_division"])] in text
    for shared_label in ("cost value affordability", "in-state tuition", "campus culture", "source attributes"):
        assert shared_label not in text
    assert str(row["net_price"]) not in text, "raw numbers are left to structured filters"


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
    assert payload["ranking_version"] == RANKING_VERSION
    assert payload["embedding_model"] == LOCAL_EMBEDDING_MODEL
    assert payload["results"][0]["fit_score"] is not None
    assert payload["results"][0]["match_reasons"]


def test_filters_apply_before_retrieval_so_matching_schools_are_not_lost() -> None:
    """A filtered search must still find a match outside the nearest candidates overall.

    Before RANKING_VERSION v1.2 the service took the nearest `candidate_limit` schools and
    then filtered them, which returned nothing here.
    """
    nearby = [
        make_row(school_id=index, name=f"California School {index}", state="CA", semantic_score=0.9 - index / 100)
        for index in range(1, 6)
    ]
    oregon = make_row(school_id=99, name="Oregon School", state="OR", semantic_score=0.1)
    service = make_service([*nearby, oregon], vector_rows=[*nearby, oregon])

    response = service.search(
        SemanticSearchRequest(query="data science schools", filters=SearchRequest(state="OR"), candidate_limit=3)
    )

    assert [result.school_id for result in response.results] == [99]


def test_final_order_follows_relevance_with_fit_breaking_ties() -> None:
    """Relevance leads; among equally relevant schools, the deterministic fit order decides."""
    weaker_fit = make_row(
        school_id=1,
        name="Relevant But Weaker College",
        graduation_rate=0.35,
        retention_rate=0.5,
        median_earnings=26000,
        repayment_rate=0.3,
        semantic_score=0.9,
    )
    stronger_fit = make_row(school_id=2, name="Relevant And Strong University", semantic_score=0.9)
    best_fit_but_off_topic = make_row(
        school_id=3,
        name="Off Topic Institute",
        graduation_rate=0.97,
        retention_rate=0.98,
        median_earnings=120000,
        semantic_score=0.2,
    )
    rows = [weaker_fit, stronger_fit, best_fit_but_off_topic]
    service = make_service(rows, vector_rows=rows)

    response = service.search(SemanticSearchRequest(query="data science schools"))
    fit = {result.school_id: result.fit_score for result in response.results}

    assert fit[3] > fit[1], "fixture check: the off-topic school must have the better fit"
    assert fit[2] > fit[1], "fixture check: the tie must be decided by fit"
    assert [result.school_id for result in response.results] == [2, 1, 3]

