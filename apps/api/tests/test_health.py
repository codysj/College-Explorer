from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "College Exploration API"
    assert payload["environment"] == "development"
    assert "timestamp" in payload


def test_basic_test_db_fixture(test_database_url: str) -> None:
    assert test_database_url == "sqlite+pysqlite:///:memory:"
