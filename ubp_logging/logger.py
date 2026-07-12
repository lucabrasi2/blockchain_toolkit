"""
Shared Logger

Provides a centralized logger for UBP.
"""

import logging

from ubp_logging.config import configure_logging

configure_logging()

logger = logging.getLogger("UBP")