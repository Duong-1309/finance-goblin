import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import device, health, notify
from app.core.config import settings
from app.core.logging_config import setup_logging

setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Finance Goblin backend starting — db=%s", settings.db_path)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router, prefix="/api")
app.include_router(device.router, prefix="/api")
app.include_router(notify.router, prefix="/api")
