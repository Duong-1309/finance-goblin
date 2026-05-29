from app.api.schemas import Buzzer, DeviceStateResponse, Led, Mood
from app.services.ai_message import generate_ai_message
from app.services.analyzer import AnalysisResult


def build_device_state(result: AnalysisResult) -> DeviceStateResponse:
    """Convert AnalysisResult into DeviceStateResponse for ESP32."""

    if result.monthly_total == 0:
        return DeviceStateResponse(
            line1="No data yet",
            line2="Add expenses",
            mood=Mood.sleep,
            led=Led.blue,
            buzzer=Buzzer.silent,
            refresh_after=60,
        )

    if result.risk_level == "high":
        mood = Mood.panic
        led = Led.red
        buzzer = Buzzer.alert
    elif result.risk_level == "medium":
        mood = Mood.warning
        led = Led.yellow
        buzzer = Buzzer.soft
    else:
        mood = Mood.happy
        led = Led.green
        buzzer = Buzzer.silent

    msg = generate_ai_message(result)

    return DeviceStateResponse(
        line1=msg.line1,
        line2=msg.line2,
        mood=mood,
        led=led,
        buzzer=buzzer,
        refresh_after=60,
    )
