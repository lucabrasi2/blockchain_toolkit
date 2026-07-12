"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Provider Factory
Author  : Jaramogi Diddy

Responsible for creating blockchain provider instances.
"""

from providers.alchemy import AlchemyProvider
from core.logger import get_logger

logger = get_logger(__name__)


class ProviderFactory:
    """
    Factory responsible for creating blockchain providers.
    """

    @staticmethod
    def get_provider():
        """
        Create and return the configured blockchain provider.
        """

        logger.info("Creating Alchemy provider.")

        provider = AlchemyProvider()

        provider.connect()

        logger.info("Provider created successfully.")

        return provider