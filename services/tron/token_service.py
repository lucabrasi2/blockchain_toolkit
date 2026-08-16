"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.tron.token_service

Purpose
-------
Business logic for TRON token operations.

Responsibilities
----------------
• Validate TRC-20 token addresses
• Retrieve TRC-20 metadata
• Retrieve wallet token balances
• Generate controller-friendly token reports

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
    get_trc20_balance,
    get_trc20_metadata,
    is_trc20,
)

from tron.wallets import (
    is_valid_address,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# TRON Token Service
###############################################################################


class TronTokenService:
    """
    TRON token business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the TRON Token Service.
        """

        logger.info(
            "TronTokenService initialized."
        )

    ###########################################################################
    # Token Report
    ###########################################################################

    def get_token_report(
        self,
        address: str,
        wallet_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a complete TRC-20 token report.

        Parameters
        ----------
        address : str
            TRC-20 contract address.

        wallet_address : str | None
            Wallet address for balance lookup.

        Returns
        -------
        dict[str, Any]
            TRC-20 token report.
        """

        logger.info(
            "Generating TRON token report for: %s",
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
            # Verify TRC-20 Token
            ###################################################################

            if not is_trc20(
                address,
            ):

                logger.warning(
                    "Address is not a TRC-20 token: %s",
                    address,
                )

                return {
                    "address": address,
                    "is_token": False,
                    "error": "Not a TRC-20 token",
                }

            ###################################################################
            # Retrieve Metadata
            ###################################################################

            metadata = get_trc20_metadata(
                address,
            )

            ###################################################################
            # Build Token Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,

                "is_token": True,

                "name": metadata.get(
                    "name",
                    "Unknown",
                ),

                "symbol": metadata.get(
                    "symbol",
                    "Unknown",
                ),

                "decimals": metadata.get(
                    "decimals",
                    18,
                ),

                "total_supply": metadata.get(
                    "total_supply",
                    0,
                ),
            }

            ###################################################################
            # Optional Wallet Balance
            ###################################################################

            if wallet_address:

                try:

                    report["balance"] = (
                        get_trc20_balance(
                            address,
                            wallet_address,
                        )
                    )

                except Exception:

                    logger.exception(
                        "Unable to retrieve TRC-20 balance."
                    )

                    report["balance"] = None

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "TRON token report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate TRON token report."
            )

            raise


###############################################################################
# End of Part 1
###############################################################################
###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TronTokenService",
]


###############################################################################
# End of File
###############################################################################