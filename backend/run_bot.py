from app.core.logging_config import setup_logging
from app.core.config import settings
setup_logging(debug=settings.debug)

from app.services.telegram_bot import run

if __name__ == "__main__":
    run()
