import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.schemas import Buzzer, DeviceStateResponse, Led, Mood
from app.core.security import require_device_key
from app.services.mqtt_publisher import publish_display

router = APIRouter()
logger = logging.getLogger(__name__)


class NotifyRequest(BaseModel):
    line1: str
    line2: str
    mood: Mood = Mood.happy
    led: Led = Led.green
    buzzer: Buzzer = Buzzer.silent
    refresh_after: int = 60


@router.post("/notify", dependencies=[Depends(require_device_key)], status_code=202)
async def notify(req: NotifyRequest) -> dict:
    """Push arbitrary content to the OLED display immediately via MQTT."""
    state = DeviceStateResponse(
        line1=req.line1[:16],
        line2=req.line2[:16],
        mood=req.mood,
        led=req.led,
        buzzer=req.buzzer,
        refresh_after=req.refresh_after,
    )
    publish_display(state)
    logger.info("notify → %r / %r mood=%s", state.line1, state.line2, state.mood)
    return {"status": "queued"}
