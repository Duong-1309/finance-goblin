from app.core.config import settings
from app.core.logging_config import setup_logging

setup_logging(debug=settings.debug)

from app.services.telegram_bot import run  # noqa: E402

if __name__ == "__main__":
    run()
