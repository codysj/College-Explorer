"""Repository SQL against a real, migrated, seeded Postgres.

Every other backend test uses fakes, so without this module no SQL statement, migration,
or Postgres-only feature (full-text search, savepoints, array columns) is ever executed.
Skipped unless TEST_DATABASE_URL points at a database that has run `alembic upgrade head`
and `scripts/seed_database.py`; CI provides one. Read-only: nothing here writes rows.
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from repositories.schools import SchoolRepository
from schemas.preferences import Preference
from schemas.schools import SearchRequest
from schemas.semantic_search import SemanticSearchRequest
from services.cache import CacheService, NullCacheBackend
from services.semantic_search import SemanticSearchService, build_search_document

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL not set")


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


def test_seed_loaded_the_real_corpus(db: Session) -> None:
    assert db.scalar(text("SELECT count(*) FROM schools")) == 92


def test_search_count_matches_rows_and_filters_apply(db: Session) -> None:
    repository = SchoolRepository(db)
    everything, total = repository.search_schools(SearchRequest(page_size=50))
    assert total == 92 and len(everything) == 50

    california, ca_total = repository.search_schools(SearchRequest(state="CA", page_size=50))
    assert ca_total == len(california) > 0
    assert {school.state for school in california} == {"CA"}

    cheap, _ = repository.search_schools(SearchRequest(max_net_price=20000, sort="net_price", page_size=50))
    prices = [school.net_price for school in cheap]
    assert prices and all(price <= 20000 for price in prices)
    assert prices == sorted(prices)


def test_name_search_treats_like_wildcards_literally(db: Session) -> None:
    repository = SchoolRepository(db)
    # Unescaped, "%" would match every school.
    _, wildcard_total = repository.search_schools(SearchRequest(query="%"))
    assert wildcard_total == 0
    _, name_total = repository.search_schools(SearchRequest(query="georgetown"))
    assert name_total == 1


def test_candidate_rows_carry_every_scoring_column(db: Session) -> None:
    rows = SchoolRepository(db).get_ranking_candidate_rows_by_ids([1, 2, 3])
    assert [row["school_id"] for row in rows] == [1, 2, 3]
    for column in ("net_price", "median_earnings", "top_majors", "culture_tags", "sports_division"):
        assert column in rows[0]
    assert isinstance(rows[0]["culture_tags"], list)


def test_fulltext_scores_rank_the_named_school_first(db: Session) -> None:
    repository = SchoolRepository(db)
    rows = repository.get_semantic_document_rows()
    scores = repository.get_fulltext_scores(
        "georgetown", {int(row["school_id"]): build_search_document(row).text for row in rows}
    )
    assert len(scores) == 92
    assert all(0 <= score < 1 for score in scores.values())
    best = max(scores, key=scores.get)
    assert next(row["name"] for row in rows if row["school_id"] == best) == "Georgetown University"


def test_failed_optional_query_leaves_the_session_usable(db: Session) -> None:
    """The full-text call runs in a savepoint, so the caller's fallback still works after it fails."""
    repository = SchoolRepository(db)
    db.execute(text("SELECT 1"))  # open the outer transaction first, as a request would
    # Over Postgres's 1 MB tsvector limit: a server-side error, which aborts the transaction
    # (a client-side rejection such as a NUL byte would not, and would prove nothing).
    oversized = " ".join(f"w{i}x" for i in range(300_000))
    with pytest.raises(DBAPIError, match="too long for tsvector"):
        repository.get_fulltext_scores("georgetown", {1: oversized})
    assert len(repository.get_semantic_document_rows()) == 92


def test_semantic_search_end_to_end_uses_fulltext(db: Session) -> None:
    service = SemanticSearchService(SchoolRepository(db), CacheService(NullCacheBackend(), "test", 1, 1, 1))
    response = service.search(
        SemanticSearchRequest(query="engineering university in texas", preferences=Preference())
    )
    assert response.retrieval_mode == "fulltext"
    assert response.results
    assert response.results[0].state == "TX"
