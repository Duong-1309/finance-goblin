import pytest
from pydantic import ValidationError

from app.api.schemas import Buzzer, DeviceStateResponse, Led, Mood


def _valid_state(**overrides) -> dict:  # type: ignore[type-arg]
    base = {
        "line1": "Coffee +43%",
        "line2": "Goblin worried",
        "mood": Mood.warning,
        "led": Led.yellow,
        "buzzer": Buzzer.soft,
        "refresh_after": 60,
    }
    base.update(overrides)
    return base


def test_valid_mock_state() -> None:
    state = DeviceStateResponse(**_valid_state())
    assert state.mood == Mood.warning
    assert state.led == Led.yellow
    assert state.buzzer == Buzzer.soft


def test_invalid_mood_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(mood="confused"))


def test_invalid_led_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(led="purple"))


def test_invalid_buzzer_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(buzzer="loud"))


def test_line1_too_long_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(line1="A" * 17))


def test_line2_too_long_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(line2="B" * 17))


def test_refresh_after_zero_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(refresh_after=0))


def test_refresh_after_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        DeviceStateResponse(**_valid_state(refresh_after=-1))
