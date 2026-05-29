import logging

from fastapi import APIRouter, Depends

from app.api.schemas import DeviceStateResponse
from app.core.security import require_device_key
from app.services.analyzer import analyze
from app.services.state_builder import build_device_state

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/device/state",
    response_model=DeviceStateResponse,
    dependencies=[Depends(require_device_key)],
)
async def device_state() -> DeviceStateResponse:
    result = analyze()
    state = build_device_state(result)
    logger.info(
        "device/state — risk=%s budget=%.1f%% mood=%s led=%s",
        result.risk_level,
        result.budget_usage_pct,
        state.mood,
        state.led,
    )
    return state
