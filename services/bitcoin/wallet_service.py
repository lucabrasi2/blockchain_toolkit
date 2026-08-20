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
- Validate Bitcoin wallet addresses
- Retrieve wallet balances
- Retrieve wallet metadata
- Generate controller-friendly wallet reports

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

from bitcoin.wallets import (
    get_address_info,
    get_btc_balance,
    is_valid_address,
)

from core.logger import get_logger


logger = get_logger(__name__)


# =============================================================================
# Bitcoin Wallet Service
# =============================================================================


class BitcoinWalletService:
    """
    Bitcoin wallet business logic service.

    The service coordinates Bitcoin address validation, blockchain data
    retrieval, address metadata, and construction of normalized wallet
    reports for higher application layers.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the Bitcoin Wallet Service."""
        logger.info(
            "BitcoinWalletService initialized."
        )

    # =========================================================================
    # Address Validation
    # =========================================================================

    @staticmethod
    def validate_address(
        address: str,
    ) -> bool:
        """
        Validate a Bitcoin wallet address.

        Parameters
        ----------
        address:
            Bitcoin wallet address.

        Returns
        -------
        bool
            ``True`` when the address is valid.
        """
        if not isinstance(address, str):
            return False

        address = address.strip()

        if not address:
            return False

        return bool(
            is_valid_address(address)
        )

    # =========================================================================
    # Address Classification
    # =========================================================================

    @staticmethod
    def _get_address_type(
        address: str,
    ) -> tuple[bool, str]:
        """
        Determine the basic Bitcoin address script type.

        Parameters
        ----------
        address:
            Bitcoin wallet address.

        Returns
        -------
        tuple[bool, str]
            A tuple containing:

            - whether the address is a SegWit/witness address
            - normalized script type label
        """
        is_witness = address.lower().startswith(
            "bc1"
        )

        script_type = (
            "Witness"
            if is_witness
            else "Legacy"
        )

        return (
            is_witness,
            script_type,
        )

    # =========================================================================
    # Wallet Report
    # =========================================================================

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete Bitcoin wallet report.

        Parameters
        ----------
        address:
            Bitcoin wallet address.

        Returns
        -------
        dict[str, Any]
            Normalized Bitcoin wallet report.

        Notes
        -----
        Invalid addresses return a structured error response rather than
        raising an exception. This preserves the existing service contract.
        """
        logger.info(
            "Generating Bitcoin wallet report for: %s",
            address,
        )

        if not isinstance(address, str):
            logger.warning(
                "Invalid Bitcoin address type."
            )

            return {
                "address": address,
                "error": "Invalid Bitcoin address",
                "is_valid": False,
            }

        normalized_address = address.strip()

        if not self.validate_address(
            normalized_address
        ):
            logger.warning(
                "Invalid Bitcoin address: %s",
                normalized_address,
            )

            return {
                "address": normalized_address,
                "error": "Invalid Bitcoin address",
                "is_valid": False,
            }

        try:
            # -----------------------------------------------------------------
            # Retrieve blockchain data
            # -----------------------------------------------------------------

            balance = get_btc_balance(
                normalized_address
            )

            address_info = get_address_info(
                normalized_address
            )

            # -----------------------------------------------------------------
            # Determine address type
            # -----------------------------------------------------------------

            is_witness, script_type = (
                self._get_address_type(
                    normalized_address
                )
            )

            # -----------------------------------------------------------------
            # Normalize returned blockchain data
            # -----------------------------------------------------------------

            if not isinstance(balance, dict):
                balance = {}

            if not isinstance(address_info, dict):
                address_info = {}

            # -----------------------------------------------------------------
            # Build normalized report
            # -----------------------------------------------------------------

            report: dict[str, Any] = {
                "address": normalized_address,

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

            logger.info(
                "Bitcoin wallet report generated successfully."
            )

            return report

        except Exception:
            logger.exception(
                "Failed to generate Bitcoin wallet report."
            )
            raise

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return (
            f"{self.__class__.__name__}()"
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "BitcoinWalletService",
]


# =============================================================================
# End of File
# =============================================================================