"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Ethereum Network Service
Author  : jaramogi Diddy

Business logic for Ethereum network information.
"""

from core.logger import get_logger
from ethereum.network import get_network_information

logger = get_logger(__name__)


class NetworkService:
    """
    Business logic for Ethereum network operations.
    """

    def __init__(self):
        logger.info("NetworkService initialized.")

    def get_network_report(self) -> dict:
        """
        Generate a complete network report.

        Returns:
            dict: Ethereum network information.
        """

        logger.info("Generating Ethereum network report.")

        report = get_network_information()

        logger.info("Network report generated successfully.")

        return report