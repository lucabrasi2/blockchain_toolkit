"""
Logging Configuration

Central logging configuration for UBP.
"""

import logging
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(exist_ok=True)

LOG_FILE = LOG_DIRECTORY / "ubp.log"


def configure_logging():
    """
    Configure the application's logging system.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ],
        force=True,
    )