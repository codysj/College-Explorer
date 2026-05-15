from schemas.preferences import Preference
from schemas.rankings import RankingRequest
from schemas.schools import SearchRequest, SearchResponse
from services.cache import CacheService


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
        existed = key in self.values
        self.values.pop(key, None)
        self.ttls.pop(key, None)
        return int(existed)

    def delete_prefix(self, prefix: str) -> int:
        keys = [key for key in self.values if key.startswith(prefix)]
        for key in keys:
            self.delete(key)
        return len(keys)


def make_cache(key_version: str = "v1") -> tuple[CacheService, InMemoryBackend]:
    backend = InMemoryBackend()
    return CacheService(
        backend=backend,
        key_version=key_version,
        search_ttl_seconds=300,
        profile_ttl_seconds=3600,
        ranking_ttl_seconds=300,
    ), backend


def test_cache_round_trip_uses_configured_ttl() -> None:
    cache, backend = make_cache()
    response = SearchResponse(page=1, page_size=20, total_results=0, has_next=False)
    key = cache.search_key(SearchRequest(state="CA"))

    cache.set_model(key, response, cache.search_ttl_seconds)
    cached = cache.get_model(key, SearchResponse)

    assert cached == response
    assert backend.ttls[key] == 300


def test_cache_keys_are_stable_and_include_cache_version() -> None:
    cache_v1, _ = make_cache("v1")
    cache_v2, _ = make_cache("v2")
    filters = SearchRequest(state="CA", sort="net_price", page=2, page_size=10)

    assert cache_v1.search_key(filters) == cache_v1.search_key(filters)
    assert cache_v1.search_key(filters) != cache_v2.search_key(filters)


def test_ranking_keys_include_ranking_version() -> None:
    cache, _ = make_cache()
    request = RankingRequest(
        preferences=Preference(intended_major="Computer Science", weights={"academic": 1}),
        filters=SearchRequest(state="CA"),
    )

    assert cache.ranking_key(request, "v1.0") != cache.ranking_key(request, "v1.1")


def test_invalidate_resource_deletes_only_matching_prefix() -> None:
    cache, backend = make_cache()
    search_key = cache.search_key(SearchRequest(state="CA"))
    profile_key = cache.profile_key(1)
    backend.values[search_key] = "{}"
    backend.values[profile_key] = "{}"

    deleted = cache.invalidate_resource("search")

    assert deleted == 1
    assert search_key not in backend.values
    assert profile_key in backend.values
