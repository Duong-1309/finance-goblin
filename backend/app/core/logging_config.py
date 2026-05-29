import logging
import sys


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s %(levelname)-8s %(name)s – %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt, force=True)
    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
