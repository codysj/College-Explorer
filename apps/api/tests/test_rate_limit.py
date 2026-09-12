"""V3.5: rate limiting and the internal-analytics gate.

These are security paths, so they are tested against the real dependency graph rather
than by calling the helpers directly.
"""

from collections.abc import Generator

import pytest
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient

from api.deps import get_cache_service
from core.config import Settings, get_settings
from core.rate_limit import RateLimit, client_identifier, require_analytics_token


class CountingCache:
    """Cache double with a working atomic counter."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.namespace = "test"
        self.key_version = "v1"

    def rate_limit_key(self, bucket: str, client_id: str, window_start: int) -> str:
        return f"{bucket}:{client_id}:{window_start}"

    def incr_counter(self, key: str, ttl_seconds: int) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]


class UnavailableCache(CountingCache):
    """Stands in for Redis being down: no counter is available."""

    def incr_counter(self, key: str, ttl_seconds: int) -> None:
        return None


def build_app(cache: CountingCache, settings: Settings) -> FastAPI:
    app = FastAPI()

    @app.post("/limited", dependencies=[Depends(RateLimit("test_bucket", limit=3))])
    def limited() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/gated", dependencies=[Depends(require_analytics_token)])
    def gated() -> dict[str, bool]:
        return {"ok": True}

    app.dependency_overrides[get_cache_service] = lambda: cache
    app.dependency_overrides[get_settings] = lambda: settings
    return app


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None)


def make_client(cache: CountingCache, settings: Settings) -> Generator[TestClient, None, None]:
    with TestClient(build_app(cache, settings)) as client:
        yield client


def test_requests_under_the_limit_are_allowed(settings: Settings) -> None:
    cache = CountingCache()
    for client in make_client(cache, settings):
        for _ in range(3):
            assert client.post("/limited").status_code == 200


def test_request_over_the_limit_is_rejected_with_retry_after(settings: Settings) -> None:
    cache = CountingCache()
    for client in make_client(cache, settings):
        for _ in range(3):
            assert client.post("/limited").status_code == 200

        response = client.post("/limited")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        # A client that is being throttled must be told when to come back.
        assert int(response.headers["Retry-After"]) > 0


def test_limit_is_per_client_not_global(settings: Settings) -> None:
    cache = CountingCache()
    for client in make_client(cache, settings):
        for _ in range(3):
            client.post("/limited", headers={"X-Forwarded-For": "10.0.0.1"})

        # A different client must not inherit the first client's exhausted budget.
        assert (
            client.post("/limited", headers={"X-Forwarded-For": "10.0.0.2"}).status_code == 200
        )
        assert (
            client.post("/limited", headers={"X-Forwarded-For": "10.0.0.1"}).status_code
            == status.HTTP_429_TOO_MANY_REQUESTS
        )


def test_missing_counter_backend_fails_open(settings: Settings) -> None:
    # Redis being unavailable must not take the API down with it.
    for client in make_client(UnavailableCache(), settings):
        for _ in range(10):
            assert client.post("/limited").status_code == 200


def test_disabling_the_limit_skips_enforcement() -> None:
    cache = CountingCache()
    disabled = Settings(_env_file=None, RATE_LIMIT_ENABLED=False)
    for client in make_client(cache, disabled):
        for _ in range(10):
            assert client.post("/limited").status_code == 200
        assert cache.counters == {}, "no counter should be touched when disabled"


def test_analytics_summary_is_open_in_development_without_a_token(settings: Settings) -> None:
    assert settings.app_env == "development"
    for client in make_client(CountingCache(), settings):
        assert client.get("/gated").status_code == 200


def test_analytics_summary_fails_closed_in_production_without_a_token() -> None:
    # Forgetting to configure the token in a deployed environment must not silently
    # publish product analytics.
    production = Settings(_env_file=None, APP_ENV="production")
    for client in make_client(CountingCache(), production):
        assert client.get("/gated").status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_analytics_summary_requires_a_matching_token() -> None:
    configured = Settings(_env_file=None, APP_ENV="production", ANALYTICS_API_TOKEN="s3cret")
    for client in make_client(CountingCache(), configured):
        assert client.get("/gated").status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            client.get("/gated", headers={"X-Analytics-Token": "wrong"}).status_code
            == status.HTTP_401_UNAUTHORIZED
        )
        assert client.get("/gated", headers={"X-Analytics-Token": "s3cret"}).status_code == 200


def test_client_identifier_prefers_the_first_forwarded_hop() -> None:
    class FakeRequest:
        def __init__(self, headers: dict[str, str], host: str | None) -> None:
            self.headers = headers
            self.client = type("C", (), {"host": host})() if host else None

    assert client_identifier(FakeRequest({"x-forwarded-for": "1.1.1.1, 2.2.2.2"}, "9.9.9.9")) == "1.1.1.1"
    assert client_identifier(FakeRequest({}, "9.9.9.9")) == "9.9.9.9"
    # A blank forwarded header must fall back rather than bucket everyone together.
    assert client_identifier(FakeRequest({"x-forwarded-for": "  "}, "9.9.9.9")) == "9.9.9.9"
    assert client_identifier(FakeRequest({}, None)) == "unknown"
