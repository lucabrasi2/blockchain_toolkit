"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
core.logger

Purpose
-------
Centralized enterprise logging configuration.

Provides:

- Console logging
- Rotating file logging
- Configurable log levels
- Consistent formatting
- Automatic log directory creation

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

import logging
import os

from pathlib import Path
from logging.handlers import RotatingFileHandler

###############################################################################
# Configuration
###############################################################################

LOG_DIRECTORY = Path("logs")

LOG_FILE = LOG_DIRECTORY / "ubp.log"

DEFAULT_LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

###############################################################################
# Create Log Directory
###############################################################################

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

###############################################################################
# Log Formatter
###############################################################################

LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

FORMATTER = logging.Formatter(
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT,
)

###############################################################################
# Console Handler
###############################################################################

console_handler = logging.StreamHandler()

console_handler.setFormatter(
    FORMATTER
)

###############################################################################
# Rotating File Handler
###############################################################################

file_handler = RotatingFileHandler(
    filename=LOG_FILE,
    maxBytes=10 * 1024 * 1024,      # 10 MB
    backupCount=5,
    encoding="utf-8",
)

file_handler.setFormatter(
    FORMATTER
)

###############################################################################
# End Part 1
###############################################################################
###############################################################################
# Logger Configuration
###############################################################################

_CONFIGURED = False


def _configure_root_logger() -> None:
    """
    Configure the root logger.

    This function is intentionally executed only once.
    """

    global _CONFIGURED

    if _CONFIGURED:
        return

    root_logger = logging.getLogger()

    ###########################################################################
    # Log Level
    ###########################################################################

    level = getattr(
        logging,
        DEFAULT_LOG_LEVEL,
        logging.INFO,
    )

    root_logger.setLevel(level)

    ###########################################################################
    # Prevent Duplicate Handlers
    ###########################################################################

    if root_logger.handlers:
        root_logger.handlers.clear()

    ###########################################################################
    # Register Handlers
    ###########################################################################

    root_logger.addHandler(console_handler)

    root_logger.addHandler(file_handler)

    ###########################################################################
    # Finished
    ###########################################################################

    _CONFIGURED = True


###############################################################################
# Public Logger API
###############################################################################

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name : str
        Usually __name__ from the calling module.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    _configure_root_logger()

    logger = logging.getLogger(name)

    return logger


###############################################################################
# Convenience Functions
###############################################################################

def set_log_level(level: str) -> None:
    """
    Change the log level at runtime.

    Parameters
    ----------
    level : str
        DEBUG, INFO, WARNING, ERROR or CRITICAL.
    """

    logger = logging.getLogger()

    logger.setLevel(
        getattr(
            logging,
            level.upper(),
            logging.INFO,
        )
    )


def get_log_level() -> str:
    """
    Return the current log level.

    Returns
    -------
    str
    """

    return logging.getLevelName(
        logging.getLogger().level
    )


###############################################################################
# End Part 2
###############################################################################
###############################################################################
# Logging Utilities
###############################################################################

def flush_logs() -> None:
    """
    Flush all configured log handlers.

    Useful before application shutdown.
    """

    root_logger = logging.getLogger()

    for handler in root_logger.handlers:

        try:
            handler.flush()

        except Exception:
            pass


def shutdown_logging() -> None:
    """
    Shutdown the logging subsystem.

    Flushes all handlers before closing them.
    """

    flush_logs()

    logging.shutdown()


###############################################################################
# Startup Log
###############################################################################

startup_logger = get_logger(__name__)

startup_logger.info(
    "=" * 79
)

startup_logger.info(
    "Universal Blockchain Platform (UBP) Logging Initialized"
)

startup_logger.info(
    "Log Level: %s",
    DEFAULT_LOG_LEVEL,
)

startup_logger.info(
    "Log File : %s",
    LOG_FILE.resolve(),
)

startup_logger.info(
    "=" * 79
)

###############################################################################
# End of File
###############################################################################