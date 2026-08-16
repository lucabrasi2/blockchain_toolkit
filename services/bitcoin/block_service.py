"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.bitcoin.block_service

Purpose
-------
Business logic for Bitcoin block operations.

Responsibilities
----------------
• Retrieve Bitcoin block reports
• Retrieve the latest Bitcoin block
• Format blockchain data for controllers
• Provide controller-friendly report objects

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

from bitcoin.blocks import (
    get_block,
    get_latest_block,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Bitcoin Block Service
###############################################################################


class BitcoinBlockService:
    """
    Bitcoin block business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the Bitcoin Block Service.
        """

        logger.info(
            "BitcoinBlockService initialized."
        )

    ###########################################################################
    # Block Report
    ###########################################################################

    def get_block_report(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Generate a Bitcoin block report.

        Parameters
        ----------
        block_identifier : str | int
            Block height, block hash,
            or "latest".

        Returns
        -------
        dict[str, Any]
            Bitcoin block report.
        """

        logger.info(
            "Generating Bitcoin block report for: %s",
            block_identifier,
        )

        try:

            ###################################################################
            # Retrieve Block
            ###################################################################

            if block_identifier == "latest":

                block = get_latest_block()

            else:

                block = get_block(
                    block_identifier,
                )

            ###################################################################
            # Handle Retrieval Error
            ###################################################################

            if block.get("error"):

                logger.warning(
                    "Unable to retrieve Bitcoin block: %s",
                    block.get("error"),
                )

                return {
                    "error": block.get(
                        "error"
                    ),
                    "number": None,
                }

            ###################################################################
            # Build Block Report
            ###################################################################

            report: dict[str, Any] = {

                "number": block.get(
                    "number"
                ),

                "hash": block.get(
                    "hash"
                ),

                "previous_hash": block.get(
                    "previous_hash"
                ),

                "next_hash": block.get(
                    "next_hash"
                ),

                "timestamp": block.get(
                    "timestamp"
                ),

                "transaction_count": block.get(
                    "transaction_count",
                    0,
                ),

                "size": block.get(
                    "size"
                ),

                "weight": block.get(
                    "weight"
                ),

                "difficulty": block.get(
                    "difficulty"
                ),

                "version": block.get(
                    "version"
                ),

                "nonce": block.get(
                    "nonce"
                ),

                "bits": block.get(
                    "bits"
                ),

                "merkle_root": block.get(
                    "merkle_root"
                ),

                "transactions": (
                    block.get(
                        "transactions",
                        [],
                    )[:10]
                ),
            }

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "Bitcoin block report generated successfully "
                "for block %s.",
                report.get(
                    "number"
                ),
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate Bitcoin block report."
            )

            raise

    ###########################################################################
    # Latest Block Report
    ###########################################################################

    def get_latest_block_report(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest Bitcoin block report.

        Returns
        -------
        dict[str, Any]
            Latest Bitcoin block report.
        """

        logger.info(
            "Retrieving latest Bitcoin block report."
        )

        return self.get_block_report(
            "latest"
        )
###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "BitcoinBlockService",
]


###############################################################################
# End of File
###############################################################################