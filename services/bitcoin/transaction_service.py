"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.bitcoin.transaction_service

Purpose
-------
Business logic for Bitcoin transaction operations.

Responsibilities
----------------
• Retrieve Bitcoin transaction reports
• Determine transaction confirmation status
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

from bitcoin.transactions import (
    get_transaction,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Bitcoin Transaction Service
###############################################################################


class BitcoinTransactionService:
    """
    Bitcoin transaction business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the Bitcoin Transaction Service.
        """

        logger.info(
            "BitcoinTransactionService initialized."
        )

    ###########################################################################
    # Transaction Report
    ###########################################################################

    def get_transaction_report(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Generate a Bitcoin transaction report.

        Parameters
        ----------
        tx_hash : str
            Bitcoin transaction hash.

        Returns
        -------
        dict[str, Any]
            Bitcoin transaction report.
        """

        logger.info(
            "Generating Bitcoin transaction report for: %s",
            tx_hash,
        )

        try:

            ###################################################################
            # Retrieve Transaction
            ###################################################################

            tx = get_transaction(
                tx_hash,
            )

            if tx.get("error"):

                logger.warning(
                    "Unable to retrieve Bitcoin transaction: %s",
                    tx.get("error"),
                )

                return {
                    "hash": tx_hash,
                    "error": tx.get("error"),
                }

            ###################################################################
            # Determine Confirmation Status
            ###################################################################

            confirmations = tx.get(
                "confirmations",
                0,
            )

            if confirmations >= 6:

                status = (
                    "Confirmed (6+ confirmations)"
                )

            elif confirmations >= 1:

                status = (
                    f"Pending ({confirmations} confirmations)"
                )

            else:

                status = (
                    "Unconfirmed (0 confirmations)"
                )

            ###################################################################
            # Build Transaction Report
            ###################################################################

            report: dict[str, Any] = {

                "hash": tx.get(
                    "hash",
                ),

                "block_number": tx.get(
                    "block_number",
                ),

                "block_hash": tx.get(
                    "block_hash",
                ),

                "confirmations": confirmations,

                "timestamp": tx.get(
                    "timestamp",
                ),

                "size": tx.get(
                    "size",
                ),

                "weight": tx.get(
                    "weight",
                ),

                "fee": tx.get(
                    "fee",
                ),

                "version": tx.get(
                    "version",
                ),

                "locktime": tx.get(
                    "locktime",
                ),

                "inputs_count": tx.get(
                    "inputs_count",
                    0,
                ),

                "outputs_count": tx.get(
                    "outputs_count",
                    0,
                ),

                "total_input": tx.get(
                    "total_input",
                    0,
                ),

                "total_output": tx.get(
                    "total_output",
                    0,
                ),

                "inputs": tx.get(
                    "inputs",
                    [],
                )[:5],

                "outputs": tx.get(
                    "outputs",
                    [],
                )[:5],

                "status": status,
            }

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "Bitcoin transaction report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate Bitcoin transaction report."
            )

            raise
###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "BitcoinTransactionService",
]


###############################################################################
# End of File
###############################################################################