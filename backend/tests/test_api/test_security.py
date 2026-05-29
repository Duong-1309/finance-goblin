from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_is_public() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200


def test_device_state_open_when_no_key_configured() -> None:
    with patch("app.core.security.settings") as mock:
        mock.device_api_key = ""
        response = client.get("/api/device/state")
        assert response.status_code == 200


def test_device_state_rejects_missing_key() -> None:
    with patch("app.core.security.settings") as mock:
        mock.device_api_key = "secret123"
        response = client.get("/api/device/state")
        assert response.status_code == 401


def test_device_state_rejects_wrong_key() -> None:
    with patch("app.core.security.settings") as mock:
        mock.device_api_key = "secret123"
        response = client.get("/api/device/state", headers={"X-Device-Key": "wrong"})
        assert response.status_code == 401


def test_device_state_accepts_correct_key() -> None:
    with patch("app.core.security.settings") as mock:
        mock.device_api_key = "secret123"
        response = client.get("/api/device/state", headers={"X-Device-Key": "secret123"})
        assert response.status_code == 200
