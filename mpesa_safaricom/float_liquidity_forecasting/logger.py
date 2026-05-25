"""Logging utilities for the project."""
import sys

from loguru import logger

from config import settings


def setup_logging():
    """Configure logging for the application."""
    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Add file handler
    logger.add(
        settings.LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="30 days",
    )

    return logger


# Initialize logger
logger = setup_logging()
