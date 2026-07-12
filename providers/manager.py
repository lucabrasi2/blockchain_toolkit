"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Provider Manager
Author  : jaramogi Diddy

Compatibility layer for provider access.

New code should use ProviderFactory directly.
"""

from providers.factory import ProviderFactory
from core.logger import get_logger

logger = get_logger(__name__)


def get_provider():
    """
    Return the configured blockchain provider.

    This compatibility function allows legacy code
    to continue working while the application is
    migrated to the ProviderFactory architecture.
    """

    logger.info("Providing blockchain provider instance.")

    return ProviderFactory.get_provider()