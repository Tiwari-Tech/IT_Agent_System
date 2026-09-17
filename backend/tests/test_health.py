from fastapi.testclient import TestClient

from backend.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "IT_Agent_System"}


def test_database_health_success(monkeypatch) -> None:
    async def ok() -> bool:
        return True

    monkeypatch.setattr("backend.api.routes.health.check_database", ok)

    response = TestClient(app).get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "database"}


def test_redis_health_success(monkeypatch) -> None:
    async def ok() -> bool:
        return True

    monkeypatch.setattr("backend.api.routes.health.check_redis", ok)

    response = TestClient(app).get("/health/redis")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "redis"}


def test_database_health_failure_hides_secret(monkeypatch) -> None:
    async def fail() -> bool:
        raise RuntimeError("postgres://user:secret@example/db")

    monkeypatch.setattr("backend.api.routes.health.check_database", fail)

    response = TestClient(app).get("/health/db")

    assert response.status_code == 503
    assert "secret" not in response.text
    assert response.json()["detail"] == {
        "status": "error",
        "service": "database",
        "error": "RuntimeError",
    }


def test_redis_health_failure_hides_secret(monkeypatch) -> None:
    async def fail() -> bool:
        raise RuntimeError("redis://:secret@localhost:6379")

    monkeypatch.setattr("backend.api.routes.health.check_redis", fail)

    response = TestClient(app).get("/health/redis")

    assert response.status_code == 503
    assert "secret" not in response.text
    assert response.json()["detail"] == {
        "status": "error",
        "service": "redis",
        "error": "RuntimeError",
    }
