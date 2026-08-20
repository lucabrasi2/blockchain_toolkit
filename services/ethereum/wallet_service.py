"""
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.wallet_service

Purpose
-------
Business logic for Ethereum wallet inspection and analysis.

Responsibilities
----------------
- Validate Ethereum wallet addresses
- Retrieve ETH balances
- Retrieve wallet nonce
- Retrieve transaction counts
- Retrieve token balances
- Classify Ethereum addresses
- Generate wallet reports
- Generate wallet status information

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from ethereum.wallets import (
    get_eth_balance,
    get_nonce,
    get_token_balances,
    get_transaction_count,
    is_valid_address,
)

from ethereum.contracts import classify_address

from constants.contract_types import (
    CONTRACT,
    ERC20,
    ERC721,
    ERC1155,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)


logger = get_logger(__name__)


class WalletService:
    """
    Ethereum Wallet Intelligence Service.

    This service provides the business logic required to inspect and
    analyze Ethereum wallet addresses.

    Blockchain-specific operations are delegated to the existing
    Ethereum wallet and contract helper modules. This class is
    responsible for validation, orchestration, normalization, and
    construction of wallet reports.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the Ethereum wallet service."""
        logger.info("WalletService initialized.")

    # =========================================================================
    # Address Validation
    # =========================================================================

    def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate an Ethereum wallet address.

        Parameters
        ----------
        address:
            Ethereum wallet address.

        Returns
        -------
        bool
            ``True`` when the address is valid.

        Raises
        ------
        InvalidWalletAddressError
            If the supplied address is invalid.
        """
        logger.info(
            "Validating Ethereum address."
        )

        if not isinstance(address, str):
            logger.warning(
                "Ethereum address validation failed: "
                "address is not a string."
            )
            raise InvalidWalletAddressError(
                "Invalid Ethereum address."
            )

        address = address.strip()

        if not address:
            logger.warning(
                "Ethereum address validation failed: "
                "address is empty."
            )
            raise InvalidWalletAddressError(
                "Invalid Ethereum address."
            )

        if not is_valid_address(address):
            logger.warning(
                "Invalid Ethereum address."
            )
            raise InvalidWalletAddressError(
                "Invalid Ethereum address."
            )

        logger.info(
            "Ethereum address validation successful."
        )

        return True

    # =========================================================================
    # Address Classification
    # =========================================================================

    @staticmethod
    def _is_contract_address(
        classification: str,
    ) -> bool:
        """
        Determine whether an address classification represents a contract.

        Parameters
        ----------
        classification:
            Address classification returned by ``classify_address()``.

        Returns
        -------
        bool
            ``True`` when the address represents a contract.
        """
        return classification in {
            CONTRACT,
            ERC20,
            ERC721,
            ERC1155,
        }

    # =========================================================================
    # Full Wallet Report
    # =========================================================================

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete Ethereum wallet report.

        The report includes:

        - address
        - address classification
        - contract detection
        - ETH balance
        - balance in Wei
        - nonce
        - transaction count
        - token balances

        Parameters
        ----------
        address:
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Complete wallet report.
        """
        logger.info(
            "Generating wallet report for %s.",
            address,
        )

        self.validate_address(address)

        balance = get_eth_balance(address)
        nonce = get_nonce(address)
        transaction_count = get_transaction_count(address)

        # classify_address() remains the single source of truth
        # for Ethereum address classification.
        classification = classify_address(address)

        is_contract_address = self._is_contract_address(
            classification
        )

        token_balances = get_token_balances(address)

        report: dict[str, Any] = {
            "address": address,
            "is_contract": is_contract_address,
            "classification": classification,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
            "nonce": nonce,
            "transaction_count": transaction_count,
            "token_balances": token_balances,
        }

        logger.info(
            "Wallet report generated successfully."
        )

        return report

    # =========================================================================
    # Wallet Balance
    # =========================================================================

    def get_wallet_balance(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve the ETH balance for an Ethereum address.

        Parameters
        ----------
        address:
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Balance information containing the address, ETH balance,
            and Wei balance.
        """
        logger.info(
            "Getting balance for %s.",
            address,
        )

        self.validate_address(address)

        balance = get_eth_balance(address)

        return {
            "address": address,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
        }

    # =========================================================================
    # Wallet Status
    # =========================================================================

    def get_wallet_status(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve Ethereum wallet status information.

        The status includes:

        - address
        - classification
        - contract detection
        - ETH balance
        - Wei balance
        - nonce
        - transaction count
        - whether the wallet currently has a positive ETH balance

        Parameters
        ----------
        address:
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet status information.
        """
        logger.info(
            "Getting status for %s.",
            address,
        )

        self.validate_address(address)

        balance = get_eth_balance(address)
        nonce = get_nonce(address)
        transaction_count = get_transaction_count(address)

        # classify_address() remains the single source of truth.
        classification = classify_address(address)

        is_contract_address = self._is_contract_address(
            classification
        )

        balance_wei = balance.get("wei", 0)

        return {
            "address": address,
            "classification": classification,
            "is_contract": is_contract_address,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance_wei,
            "nonce": nonce,
            "transaction_count": transaction_count,
            "has_balance": balance_wei > 0,
        }

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{self.__class__.__name__}()"


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "WalletService",
]