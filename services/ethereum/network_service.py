"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Ethereum Network Service
Author  : Jaramogi Diddy

Architecture Layer
------------------
Service Layer

Responsibilities
----------------
✓ Generate Ethereum network reports
✓ Coordinate network business logic
✓ Return immutable network information

Not Responsible For
-------------------
✗ Blockchain communication
✗ CLI formatting
✗ Provider management
"""

from __future__ import annotations

from core.logger import get_logger

from ethereum.network import (
    get_network_information,
)

logger = get_logger(__name__)


class NetworkService:
    """
    Ethereum Network Service.

    Provides business logic for Ethereum
    network operations.
    """

    def __init__(self):
        """
        Initialize the Network Service.
        """

        logger.info(
            "NetworkService initialized."
        )

    def get_network_report(
        self,
    ) -> dict:
        """
        Generate a complete Ethereum
        network report.

        Returns
        -------
        dict
            Ethereum network information.
        """

        logger.info(
            "Generating Ethereum network report."
        )

        report = get_network_information()

        logger.info(
            "Network report generated successfully."
        )

        return report