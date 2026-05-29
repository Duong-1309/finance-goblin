import json
import logging

import paho.mqtt.publish as publish

from app.api.schemas import Buzzer, DeviceStateResponse, Led, Mood
from app.core.config import settings

logger = logging.getLogger(__name__)


def publish_display(state: DeviceStateResponse) -> None:
    """Push a DeviceState to the ESP32 via MQTT."""
    payload = json.dumps(
        {
            "line1": state.line1,
            "line2": state.line2,
            "mood": state.mood,
            "led": state.led,
            "buzzer": state.buzzer,
            "refresh_after": state.refresh_after,
        }
    )
    try:
        publish.single(
            settings.mqtt_topic_display,
            payload=payload,
            hostname=settings.mqtt_broker_host,
            port=settings.mqtt_broker_port,
        )
        logger.info("MQTT → %s: %r / %r", settings.mqtt_topic_display, state.line1, state.line2)
    except Exception as e:
        logger.warning("MQTT publish failed: %s", e)


def publish_text(
    line1: str, line2: str, mood: str = "happy", led: str = "green", buzzer: str = "silent"
) -> None:
    """Convenience wrapper — push arbitrary text to OLED."""
    state = DeviceStateResponse(
        line1=line1[:16],
        line2=line2[:16],
        mood=Mood(mood),
        led=Led(led),
        buzzer=Buzzer(buzzer),
        refresh_after=60,
    )
    publish_display(state)
