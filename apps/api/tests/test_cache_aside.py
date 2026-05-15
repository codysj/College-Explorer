from schemas.preferences import Preference
from schemas.rankings import RankingRequest, RankingResponse
from schemas.schools import (
    SchoolProfileAcademics,
    SchoolProfileCampusLife,
    SchoolProfileCost,
    SchoolProfileOutcomes,
    SchoolProfileResponse,
    SearchRequest,
    SearchResponse,
)
from services.cache import CacheService
from services.ranking_service import RANKING_VERSION, RankingService
from services.schools import SchoolService

from tests.test_cache_service import make_cache
from tests.test_ranking_service import make_row


class CountingSchoolRepository:
    def __init__(self) -> None:
        self.search_calls = 0
        self.profile_calls = 0

    def search_schools(self, filters: SearchRequest) -> tuple[list, int]:
        self.search_calls += 1
        return [], 0

    def get_school_profile_row(self, school_id: int) -> dict[str, object]:
        self.profile_calls += 1
        return {
            "school_id": school_id,
            "name": "Adams State College",
            "city": "Northbridge",
            "state": "MA",
            "region": "Northeast",
            "type": "Public",
            "setting": "Suburban",
            "enrollment": 6200,
            "acceptance_rate": 0.64,
            "top_majors": ["Biology"],
            "graduation_rate": 0.69,
            "retention_rate": 0.82,
            "student_faculty_ratio": 15.0,
            "tuition_in_state": 14200,
            "tuition_out_state": 31800,
            "net_price": 22100,
            "average_aid": 12600,
            "debt_median": 21000,
            "median_earnings": 52000,
            "repayment_rate": 0.76,
            "housing_available": True,
            "sports_division": "DIII",
            "greek_life_rate": 0.08,
            "culture_tags": ["research"],
        }


class CountingRankingRepository:
    def __init__(self) -> None:
        self.calls = 0

    def get_ranking_candidate_rows(self, filters: SearchRequest) -> list[dict[str, object]]:
        self.calls += 1
        return [make_row()]


def make_school_service(cache: CacheService) -> tuple[SchoolService, CountingSchoolRepository]:
    service = SchoolService.__new__(SchoolService)
    repository = CountingSchoolRepository()
    service.repository = repository
    service.cache = cache
    return service, repository


def sample_profile() -> SchoolProfileResponse:
    return SchoolProfileResponse(
        school_id=1,
        name="Cached College",
        city="Northbridge",
        state="MA",
        region="Northeast",
        type="Public",
        setting="Suburban",
        enrollment=6200,
        acceptance_rate=0.64,
        academics=SchoolProfileAcademics(majors=["Biology"], popular_majors=["Biology"]),
        cost=SchoolProfileCost(net_price=22100),
        outcomes=SchoolProfileOutcomes(median_earnings=52000),
        campus_life=SchoolProfileCampusLife(housing=True),
        data_confidence_score=0.5,
    )


def test_search_cache_miss_populates_cache_and_second_call_avoids_repository() -> None:
    cache, backend = make_cache()
    service, repository = make_school_service(cache)
    filters = SearchRequest(state="CA")

    first = service.search_schools(filters)
    second = service.search_schools(filters)

    assert first == second == SearchResponse(page=1, page_size=20, total_results=0, has_next=False)
    assert repository.search_calls == 1
    assert backend.ttls[cache.search_key(filters)] == cache.search_ttl_seconds


def test_profile_cache_hit_avoids_repository() -> None:
    cache, _ = make_cache()
    service, repository = make_school_service(cache)
    profile = sample_profile()
    cache.set_model(cache.profile_key(1), profile, cache.profile_ttl_seconds)

    result = service.get_school_profile(1)

    assert result == profile
    assert repository.profile_calls == 0


def test_ranking_cache_miss_populates_and_hit_avoids_repository() -> None:
    cache, backend = make_cache()
    repository = CountingRankingRepository()
    service = RankingService(repository, cache)
    request = RankingRequest(preferences=Preference(intended_major="Computer Science"), filters=SearchRequest())

    first = service.rank_schools(request)
    second = service.rank_schools(request)

    assert isinstance(first, RankingResponse)
    assert first == second
    assert repository.calls == 1
    assert backend.ttls[cache.ranking_key(request, RANKING_VERSION)] == cache.ranking_ttl_seconds
