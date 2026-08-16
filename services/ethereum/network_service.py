"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.network_service

Purpose
-------
Business logic for Ethereum network operations.

Responsibilities
----------------
• Generate Ethereum network reports
• Coordinate network business logic
• Return controller-friendly network information

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

from typing import Any

from core.logger import get_logger
from ethereum.network import get_network_information

logger = get_logger(__name__)


class NetworkService:
    """
    Ethereum Network Service.

    Provides business logic for Ethereum
    network operations.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Network Service.
        """

        logger.info(
            "NetworkService initialized."
        )

    ###########################################################################
    # Network Report
    ###########################################################################

    def get_network_report(
        self,
    ) -> dict[str, Any]:
        """
        Generate a complete Ethereum network report.

        Returns
        -------
        dict[str, Any]
            Ethereum network information.
        """

        logger.info(
            "Generating Ethereum network report."
        )

        try:

            report = get_network_information()

            logger.info(
                "Ethereum network report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate Ethereum network report."
            )

            raise


###############################################################################
# End of File
###############################################################################