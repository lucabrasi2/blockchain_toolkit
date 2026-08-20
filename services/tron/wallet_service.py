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
- Validate TRON wallet addresses
- Retrieve wallet balances
- Retrieve account information
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

from core.logger import get_logger

from tron.contracts import is_contract

from tron.wallets import (
    get_account_info,
    get_trx_balance,
    is_valid_address,
)


logger = get_logger(__name__)


# =============================================================================
# TRON Wallet Service
# =============================================================================


class TronWalletService:
    """
    TRON wallet business logic service.

    This service coordinates TRON address validation, blockchain data
    retrieval, contract detection, and construction of normalized wallet
    reports for higher application layers.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the TRON Wallet Service."""
        logger.info(
            "TronWalletService initialized."
        )

    # =========================================================================
    # Address Validation
    # =========================================================================

    @staticmethod
    def validate_address(
        address: str,
    ) -> bool:
        """
        Validate a TRON wallet address.

        Parameters
        ----------
        address:
            TRON wallet address.

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
    def _get_classification(
        is_contract_address: bool,
    ) -> str:
        """
        Determine the normalized TRON address classification.

        Parameters
        ----------
        is_contract_address:
            Whether the address represents a smart contract.

        Returns
        -------
        str
            ``Contract`` or ``EOA``.
        """
        return (
            "Contract"
            if is_contract_address
            else "EOA"
        )

    # =========================================================================
    # Wallet Report
    # =========================================================================

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete TRON wallet report.

        Parameters
        ----------
        address:
            TRON wallet address.

        Returns
        -------
        dict[str, Any]
            Normalized TRON wallet report.

        Notes
        -----
        Invalid addresses return a structured error response rather than
        raising an exception. This preserves the existing service contract.
        """
        logger.info(
            "Generating TRON wallet report for: %s",
            address,
        )

        if not isinstance(address, str):
            logger.warning(
                "Invalid TRON address type."
            )

            return {
                "address": address,
                "error": "Invalid TRON address",
                "is_valid": False,
            }

        normalized_address = address.strip()

        if not self.validate_address(
            normalized_address
        ):
            logger.warning(
                "Invalid TRON address: %s",
                normalized_address,
            )

            return {
                "address": normalized_address,
                "error": "Invalid TRON address",
                "is_valid": False,
            }

        try:
            # -----------------------------------------------------------------
            # Retrieve blockchain data
            # -----------------------------------------------------------------

            balance = get_trx_balance(
                normalized_address
            )

            account_info = get_account_info(
                normalized_address
            )

            is_contract_address = is_contract(
                normalized_address
            )

            # -----------------------------------------------------------------
            # Normalize helper responses
            # -----------------------------------------------------------------

            if not isinstance(balance, dict):
                balance = {}

            if not isinstance(account_info, dict):
                account_info = {}

            # -----------------------------------------------------------------
            # Determine address classification
            # -----------------------------------------------------------------

            classification = self._get_classification(
                is_contract_address
            )

            # -----------------------------------------------------------------
            # Build wallet report
            # -----------------------------------------------------------------

            report: dict[str, Any] = {
                "address": normalized_address,

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

                "classification": classification,

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

            logger.info(
                "TRON wallet report generated successfully."
            )

            return report

        except Exception:
            logger.exception(
                "Failed to generate TRON wallet report."
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
    "TronWalletService",
]


# =============================================================================
# End of File
# =============================================================================