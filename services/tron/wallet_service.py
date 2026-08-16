"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.tron.wallet_service

Purpose
-------
Business logic for TRON wallet operations.

Responsibilities
----------------
• Validate TRON wallet addresses
• Retrieve wallet balances
• Retrieve account information
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

from tron.contracts import (
    is_contract,
)

from tron.wallets import (
    get_account_info,
    get_trx_balance,
    is_valid_address,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# TRON Wallet Service
###############################################################################


class TronWalletService:
    """
    TRON wallet business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the TRON Wallet Service.
        """

        logger.info(
            "TronWalletService initialized."
        )

    ###########################################################################
    # Wallet Report
    ###########################################################################

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete TRON wallet report.

        Parameters
        ----------
        address : str
            TRON wallet address.

        Returns
        -------
        dict[str, Any]
            TRON wallet report.
        """

        logger.info(
            "Generating TRON wallet report for: %s",
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
                    "Invalid TRON address: %s",
                    address,
                )

                return {
                    "address": address,
                    "error": "Invalid TRON address",
                    "is_valid": False,
                }

            ###################################################################
            # Retrieve Blockchain Data
            ###################################################################

            balance = get_trx_balance(
                address,
            )

            account_info = get_account_info(
                address,
            )

            is_contract_address = is_contract(
                address,
            )

            ###################################################################
            # Build Wallet Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,

                "balance_trx": balance.get(
                    "trx",
                    0,
                ),

                "balance_sun": balance.get(
                    "sun",
                    0,
                ),

                "is_contract": (
                    is_contract_address
                ),

                "classification": (
                    "Contract"
                    if is_contract_address
                    else "EOA"
                ),

                "energy": account_info.get(
                    "energy",
                    0,
                ),

                "bandwidth": account_info.get(
                    "bandwidth",
                    0,
                ),

                "create_time": account_info.get(
                    "create_time",
                ),
            }

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "TRON wallet report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate TRON wallet report."
            )

            raise


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TronWalletService",
]


###############################################################################
# End of File
###############################################################################
