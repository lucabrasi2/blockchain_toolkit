"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.bitcoin.wallet_service

Purpose
-------
Business logic for Bitcoin wallet operations.

Responsibilities
----------------
• Validate Bitcoin wallet addresses
• Retrieve wallet balances
• Retrieve wallet metadata
• Generate controller-friendly wallet reports

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

from bitcoin.wallets import (
    get_address_info,
    get_btc_balance,
    is_valid_address,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Bitcoin Wallet Service
###############################################################################


class BitcoinWalletService:
    """
    Bitcoin wallet business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the Bitcoin Wallet Service.
        """

        logger.info(
            "BitcoinWalletService initialized."
        )

    ###########################################################################
    # Wallet Report
    ###########################################################################

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete Bitcoin wallet report.

        Parameters
        ----------
        address : str
            Bitcoin wallet address.

        Returns
        -------
        dict[str, Any]
            Bitcoin wallet report.
        """

        logger.info(
            "Generating Bitcoin wallet report for: %s",
            address,
        )

        try:

            ###################################################################
            # Validate Address
            ###################################################################

            if not is_valid_address(
                address,
            ):

                logger.warning(
                    "Invalid Bitcoin address: %s",
                    address,
                )

                return {
                    "address": address,
                    "error": "Invalid Bitcoin address",
                    "is_valid": False,
                }

            ###################################################################
            # Retrieve Blockchain Data
            ###################################################################

            balance = get_btc_balance(
                address,
            )

            address_info = get_address_info(
                address,
            )

            ###################################################################
            # Determine Address Type
            ###################################################################

            is_witness = address.startswith(
                "bc1"
            )

            script_type = (
                "Witness"
                if is_witness
                else "Legacy"
            )

            ###################################################################
            # Build Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,

                "balance_btc": balance.get(
                    "btc",
                    0,
                ),

                "balance_satoshis": balance.get(
                    "satoshis",
                    0,
                ),

                "is_contract": False,

                "classification": (
                    "Bitcoin Address"
                ),

                "transaction_count": balance.get(
                    "transaction_count",
                    0,
                ),

                "total_received": balance.get(
                    "total_received",
                    0,
                ),

                "total_sent": balance.get(
                    "total_sent",
                    0,
                ),

                "is_valid": address_info.get(
                    "isvalid",
                    True,
                ),

                "is_script": address_info.get(
                    "isscript",
                    False,
                ),

                "is_witness": is_witness,

                "script_type": script_type,
            }

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "Bitcoin wallet report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate Bitcoin wallet report."
            )

            raise
###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "BitcoinWalletService",
]


###############################################################################
# End of File
###############################################################################