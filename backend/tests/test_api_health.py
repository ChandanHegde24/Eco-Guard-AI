import main
from data_layer.gee_client import EarthEngineUnavailableError


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


def test_analyze_region_rejects_reverse_dates(client) -> None:
    response = client.post(
        "/api/v1/analyze-region",
        json={
            "latitude": 14.5,
            "longitude": 75.5,
            "time_t1": "2026-03-20",
            "time_t2": "2026-03-10",
        },
    )

    assert response.status_code == 422


def test_analyze_region_returns_503_when_earth_engine_unavailable(client, monkeypatch) -> None:
    main.analysis_cache.clear()

    def _raise_ee_unavailable(*_args, **_kwargs):
        raise EarthEngineUnavailableError("not authenticated")

    monkeypatch.setattr(main, "fetch_satellite_images", _raise_ee_unavailable)

    response = client.post(
        "/api/v1/analyze-region",
        json={
            "latitude": 14.5,
            "longitude": 75.5,
            "time_t1": "2026-03-01",
            "time_t2": "2026-03-10",
        },
    )

    assert response.status_code == 503
    assert "Satellite analysis is currently unavailable" in response.json()["detail"]


def test_analyze_region_hides_internal_error_details(client, monkeypatch) -> None:
    main.analysis_cache.clear()

    def _raise_unexpected_error(*_args, **_kwargs):
        raise ValueError("internal details should not leak")

    monkeypatch.setattr(main, "fetch_satellite_images", _raise_unexpected_error)

    response = client.post(
        "/api/v1/analyze-region",
        json={
            "latitude": 14.5,
            "longitude": 75.5,
            "time_t1": "2026-03-01",
            "time_t2": "2026-03-10",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error while analyzing region"


def test_analyze_region_persists_composite_change_percentage(client, monkeypatch) -> None:
    main.analysis_cache.clear()

    monkeypatch.setattr(
        main,
        "fetch_satellite_images",
        lambda *_args, **_kwargs: {"t1": object(), "t2": object(), "roi": object()},
    )
    values = iter([10.0, 2.0])
    monkeypatch.setattr(main, "analyze_environmental_change", lambda *_args, **_kwargs: next(values))
    monkeypatch.setattr(main, "get_image_thumbnail", lambda *_args, **_kwargs: "thumb-url")

    captured_save_kwargs: dict = {}

    class _FakeRun:
        id = 123

    def _capture_save_analysis_run(_session, **kwargs):
        captured_save_kwargs.update(kwargs)
        return _FakeRun()

    monkeypatch.setattr(main, "save_analysis_run", _capture_save_analysis_run)

    response = client.post(
        "/api/v1/analyze-region",
        json={
            "latitude": 14.5,
            "longitude": 75.5,
            "time_t1": "2026-03-01",
            "time_t2": "2026-03-10",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["change_percentage"] == 7.6
    assert captured_save_kwargs["change_percentage"] == payload["change_percentage"]
