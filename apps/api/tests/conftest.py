from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_database_url() -> str:
    return "sqlite+pysqlite:///:memory:"
