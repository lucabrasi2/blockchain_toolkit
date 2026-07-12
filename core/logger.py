"""
Universal Blockchain Platform

Central Logging Configuration
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module.

    Parameters
    ----------
    name : str
        Usually __name__ from the calling module.

    Returns
    -------
    logging.Logger
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    return logging.getLogger(name)