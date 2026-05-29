from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

REQUIRED_FIELDS = {"line1", "line2", "mood", "led", "buzzer", "refresh_after"}


def test_device_state_returns_200() -> None:
    response = client.get("/api/device/state")
    assert response.status_code == 200


def test_device_state_schema() -> None:
    body = client.get("/api/device/state").json()
    assert REQUIRED_FIELDS.issubset(body.keys())


def test_device_state_line_lengths() -> None:
    body = client.get("/api/device/state").json()
    assert len(body["line1"]) <= 16
    assert len(body["line2"]) <= 16


def test_device_state_refresh_after_positive() -> None:
    body = client.get("/api/device/state").json()
    assert isinstance(body["refresh_after"], int)
    assert body["refresh_after"] > 0
