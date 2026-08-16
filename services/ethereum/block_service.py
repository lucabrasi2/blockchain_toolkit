"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.block_service

Purpose
-------
Business logic for Ethereum block operations.

Responsibilities
----------------
• Retrieve block reports
• Retrieve latest block
• Format blockchain data for presentation
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
from ethereum.blocks import get_block

logger = get_logger(__name__)


class BlockService:
    """
    Ethereum block business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Ethereum block service.
        """

        logger.info(
            "BlockService initialized."
        )

    ###########################################################################
    # Block Reports
    ###########################################################################

    def get_block_report(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Generate a complete Ethereum block report.

        Parameters
        ----------
        block_identifier : str | int
            Block number, block hash, or "latest".

        Returns
        -------
        dict[str, Any]
            Formatted block report.

        Raises
        ------
        Exception
            Propagates unexpected errors from the blockchain layer.
        """

        logger.info(
            "Getting block report for: %s",
            block_identifier,
        )

        try:
            block = get_block(
                block_identifier,
            )

            ###################################################################
            # Error Handling
            ###################################################################

            if block.get("error"):

                return {
                    "error": block.get("error"),
                    "number": None,
                }

            ###################################################################
            # Transactions
            ###################################################################

            transactions = block.get(
                "transactions",
                [],
            )

            tx_hashes: list[str] = []

            for transaction in transactions[:20]:

                if hasattr(transaction, "hex"):

                    tx_hashes.append(
                        transaction.hex()
                    )

                else:

                    tx_hashes.append(
                        str(transaction)
                    )

            ###################################################################
            # Report
            ###################################################################

            report: dict[str, Any] = {

                "number": block.get(
                    "number"
                ),

                "hash": block.get(
                    "hash"
                ),

                "parent_hash": block.get(
                    "parent_hash"
                ),

                "timestamp": block.get(
                    "timestamp"
                ),

                "miner": block.get(
                    "miner"
                ),

                "difficulty": block.get(
                    "difficulty"
                ),

                "gas_used": block.get(
                    "gas_used"
                ),

                "gas_limit": block.get(
                    "gas_limit"
                ),

                "size": block.get(
                    "size"
                ),

                "transaction_count": len(
                    transactions
                ),

                "transactions": tx_hashes,

                "transaction_objects": (
                    transactions[:20]
                    if transactions
                    else []
                ),
            }

            logger.info(
                "Successfully generated block report "
                "for block %s.",
                report["number"],
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate block report "
                "for %s.",
                block_identifier,
            )

            raise

    ###########################################################################
    # Latest Block
    ###########################################################################

    def get_latest_block_report(
        self,
    ) -> dict[str, Any]:
        """
        Generate a report for the latest Ethereum block.

        Returns
        -------
        dict[str, Any]
            Latest block report.
        """

        logger.info(
            "Retrieving latest Ethereum block report."
        )

        return self.get_block_report(
            "latest"
        )


###############################################################################
# End of File
###############################################################################