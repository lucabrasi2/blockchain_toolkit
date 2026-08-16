"""
Universal Blockchain Platform (UBP)

## Module

services.tron.transaction_service

## Purpose

Business logic for TRON transaction operations.

## Responsibilities

• Retrieve TRON transactions
• Determine transaction confirmation status
• Generate controller-friendly transaction reports
• Keep blockchain communication outside the controller

## Architecture

Controller
    ↓
TronTransactionService
    ↓
tron.transactions

## Author

Jaramogi Diddy

## Project

Universal Blockchain Platform (UBP)

## Version

2.0 Enterprise
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from tron.transactions import (
    get_transaction,
)


logger = get_logger(__name__)


class TronTransactionService:
    """
    TRON transaction business logic service.

    This service is responsible for retrieving
    and formatting TRON transaction information.

    The controller must not communicate directly
    with the tron.transactions module.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the TRON Transaction Service.
        """

        logger.info(
            "TronTransactionService initialized."
        )

    ###########################################################################
    # Transaction Report
    ###########################################################################

    def get_transaction_report(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Generate a TRON transaction report.

        Parameters
        ----------
        tx_hash : str
            TRON transaction hash.

        Returns
        -------
        dict[str, Any]
            Controller-friendly transaction report.
        """

        logger.info(
            "Generating TRON transaction report for: %s",
            tx_hash,
        )

        try:

            ###################################################################
            # Retrieve blockchain transaction
            ###################################################################

            transaction = get_transaction(
                tx_hash,
            )

            ###################################################################
            # Validate response
            ###################################################################

            if not isinstance(
                transaction,
                dict,
            ):

                logger.warning(
                    "Unexpected TRON transaction response."
                )

                return {
                    "hash": tx_hash,
                    "error": (
                        "Invalid transaction response."
                    ),
                }

            ###################################################################
            # Handle blockchain-level errors
            ###################################################################

            if transaction.get(
                "error"
            ):

                logger.warning(
                    "Unable to retrieve TRON transaction: %s",
                    transaction.get(
                        "error"
                    ),
                )

                return {
                    "hash": tx_hash,
                    "error": transaction.get(
                        "error"
                    ),
                }

        except Exception as error:

            logger.exception(
                "Unexpected error generating TRON transaction report."
            )

            return {
                "hash": tx_hash,
                "error": str(error),
            }
                    ###################################################################
            # Confirmation information
            ###################################################################

            confirmations = transaction.get(
                "confirmations",
                0,
            )

            if confirmations is None:
                confirmations = 0

            ###################################################################
            # Determine transaction status
            ###################################################################

            if confirmations >= 19:

                status = (
                    "Confirmed"
                )

            elif confirmations >= 1:

                status = (
                    f"Pending "
                    f"({confirmations} confirmations)"
                )

            else:

                status = (
                    "Unconfirmed"
                )

            ###################################################################
            # Build controller-friendly report
            ###################################################################

            report = {

                "hash": transaction.get(
                    "hash",
                    tx_hash,
                ),

                "block_number": transaction.get(
                    "block_number",
                ),

                "block_hash": transaction.get(
                    "block_hash",
                ),

                "confirmations": confirmations,

                "timestamp": transaction.get(
                    "timestamp",
                ),

                "contract_type": transaction.get(
                    "contract_type",
                ),

                "owner_address": transaction.get(
                    "owner_address",
                ),

                "to_address": transaction.get(
                    "to_address",
                ),

                "amount": transaction.get(
                    "amount",
                    0,
                ),

                "fee": transaction.get(
                    "fee",
                    0,
                ),

                "energy_used": transaction.get(
                    "energy_used",
                    0,
                ),

                "energy_fee": transaction.get(
                    "energy_fee",
                    0,
                ),

                "bandwidth_used": transaction.get(
                    "bandwidth_used",
                    0,
                ),

                "bandwidth_fee": transaction.get(
                    "bandwidth_fee",
                    0,
                ),

                "status": status,

                "raw": transaction,
            }

            logger.info(
                "TRON transaction report generated "
                "successfully: %s",
                tx_hash,
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate TRON transaction "
                "report."
            )

            raise

    ###########################################################################
    # Confirmation Helper
    ###########################################################################

    def get_transaction_confirmations(
        self,
        tx_hash: str,
    ) -> int:
        """
        Retrieve the confirmation count for a
        TRON transaction.

        Parameters
        ----------
        tx_hash : str
            TRON transaction hash.

        Returns
        -------
        int
            Number of confirmations.
        """

        logger.info(
            "Retrieving TRON transaction confirmations: %s",
            tx_hash,
        )

        try:

            transaction = get_transaction(
                tx_hash,
            )

            if not isinstance(
                transaction,
                dict,
            ):

                return 0

            confirmations = transaction.get(
                "confirmations",
                0,
            )

            if confirmations is None:
                return 0

            return int(
                confirmations
            )

        except Exception:

            logger.exception(
                "Failed to retrieve TRON transaction "
                "confirmations."
            )

            raise
        ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}()"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TronTransactionService",
]


###############################################################################
# End of File
###############################################################################