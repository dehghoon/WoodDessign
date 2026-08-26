from fastapi.testclient import TestClient

from wooddessign.api.app import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_declares_engine_not_integrated() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["engineering_engine"] == "not-integrated"


def test_calculation_fails_closed_without_validated_engine() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={
            "design_standard": "UNVERIFIED",
            "design_standard_edition": "UNVERIFIED",
            "inputs": {},
        },
    )
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["code"] == "ENGINEERING_ENGINE_NOT_VALIDATED"
    assert "HP-01" in detail["hold_points"]
