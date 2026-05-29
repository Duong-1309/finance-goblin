from enum import StrEnum

from pydantic import BaseModel, field_validator


class Mood(StrEnum):
    happy = "happy"
    warning = "warning"
    panic = "panic"
    sleep = "sleep"
    offline = "offline"


class Led(StrEnum):
    green = "green"
    yellow = "yellow"
    red = "red"
    blue = "blue"
    white = "white"


class Buzzer(StrEnum):
    silent = "silent"
    soft = "soft"
    alert = "alert"


class DeviceStateResponse(BaseModel):
    line1: str
    line2: str
    mood: Mood
    led: Led
    buzzer: Buzzer
    refresh_after: int

    @field_validator("line1", "line2")
    @classmethod
    def max_16_chars(cls, v: str) -> str:
        if len(v) > 16:
            raise ValueError("LCD line must be 16 characters or fewer")
        return v

    @field_validator("refresh_after")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("refresh_after must be positive")
        return v
