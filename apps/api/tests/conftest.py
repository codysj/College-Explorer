from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from api.routes.analytics import get_analytics_service
from apps.api.main import app
from schemas.analytics import AnalyticsEventCreate


class NoopAnalyticsService:
    def try_log_event(self, request: AnalyticsEventCreate) -> None:
        return None


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_analytics_service] = lambda: NoopAnalyticsService()
    with TestClient(app) as test_client:
        try:
            yield test_client
        finally:
            app.dependency_overrides.pop(get_analytics_service, None)


@pytest.fixture
def test_database_url() -> str:
    return "sqlite+pysqlite:///:memory:"
