import logging
import sys
from services.core.config import settings

def setup_logging() -> None:
    """Configures logging for the application using settings."""
    log_level = logging.INFO
    configured_level = settings.LOG_LEVEL.upper()
    if configured_level == "DEBUG":
        log_level = logging.DEBUG
    elif configured_level == "WARNING":
        log_level = logging.WARNING
    elif configured_level == "ERROR":
        log_level = logging.ERROR

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Direct logs to standard output
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)
