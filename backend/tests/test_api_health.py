def test_root_endpoint(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "running"


def test_health_endpoint(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_endpoint(client) -> None:
    response = client.get("/ready")

    assert response.status_code in (200, 503)
    payload = response.json()
    assert "checks" in payload
    assert "database" in payload["checks"]


def test_recent_analyses_limit_is_bounded(client) -> None:
    response = client.get("/api/v1/analysis/recent?limit=1000")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
