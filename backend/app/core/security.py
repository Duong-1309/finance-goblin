from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_device_key(x_device_key: str = Header(default="")) -> None:
    """Dependency: reject requests with wrong or missing device key.
    Skipped if DEVICE_API_KEY is not configured (dev mode)."""
    if not settings.device_api_key:
        return  # no key configured → open access (dev/local)
    if x_device_key != settings.device_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Device-Key",
        )
