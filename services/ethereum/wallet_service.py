"""
===============================================================================
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
===============================================================================
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
    get_transaction_count,
    get_token_balances,
)

from ethereum.contracts import (
    classify_address,
)

from constants.contract_types import (
    EOA,
    EOA_DELEGATED,
    CONTRACT,
    ERC20,
    ERC721,
    ERC1155,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Wallet Service
###############################################################################


class WalletService:
    """
    Ethereum Wallet Intelligence Service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the Wallet Service.
        """

        logger.info(
            "WalletService initialized."
        )

    ###########################################################################
    # Address Validation
    ###########################################################################

    def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate an Ethereum address.

        Parameters
        ----------
        address : str
            Ethereum address.

        Returns
        -------
        bool
            True if the address is valid.

        Raises
        ------
        InvalidWalletAddressError
            If the address is invalid.
        """

        logger.info(
            "Validating Ethereum address."
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

    ###########################################################################
    # Address Classification
    ###########################################################################

    def _is_contract_address(
        self,
        classification: str,
    ) -> bool:
        """
        Determine whether an address classification
        represents a smart contract.

        Parameters
        ----------
        classification : str
            Address classification returned by
            classify_address().

        Returns
        -------
        bool
            True if the address represents a contract.
        """

        return classification in (
            CONTRACT,
            ERC20,
            ERC721,
            ERC1155,
        )

    ###########################################################################
    # Full Wallet Report
    ###########################################################################

    def get_wallet_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete wallet report.

        Parameters
        ----------
        address : str
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

        #######################################################################
        # Validate Address
        #######################################################################

        self.validate_address(
            address,
        )

        #######################################################################
        # Retrieve Wallet Information
        #######################################################################

        balance = get_eth_balance(
            address,
        )

        nonce = get_nonce(
            address,
        )

        transaction_count = get_transaction_count(
            address,
        )

        #######################################################################
        # Address Classification
        #######################################################################

        # classify_address() remains the single source of truth
        # for Ethereum address classification.

        classification = classify_address(
            address,
        )

        is_contract_address = self._is_contract_address(
            classification,
        )

        #######################################################################
        # Token Balances
        #######################################################################

        token_balances = get_token_balances(
            address,
        )

        #######################################################################
        # Wallet Report
        #######################################################################

        report: dict[str, Any] = {
            "address": address,

            "is_contract": is_contract_address,

            "classification": classification,

            "balance_eth": balance.get(
                "ether",
                0,
            ),

            "balance_wei": balance.get(
                "wei",
                0,
            ),

            "nonce": nonce,

            "transaction_count": transaction_count,

            "token_balances": token_balances,
        }

        logger.info(
            "Wallet report generated successfully."
        )

        return report


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Wallet Balance
    ###########################################################################

    def get_wallet_balance(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Get wallet balance only.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Balance information.
        """

        logger.info(
            "Getting balance for %s.",
            address,
        )

        #######################################################################
        # Validate Address
        #######################################################################

        self.validate_address(
            address,
        )

        #######################################################################
        # Retrieve Balance
        #######################################################################

        balance = get_eth_balance(
            address,
        )

        #######################################################################
        # Balance Report
        #######################################################################

        return {
            "address": address,

            "balance_eth": balance.get(
                "ether",
                0,
            ),

            "balance_wei": balance.get(
                "wei",
                0,
            ),
        }

    ###########################################################################
    # Wallet Status
    ###########################################################################

    def get_wallet_status(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Get wallet status information.

        Parameters
        ----------
        address : str
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

        #######################################################################
        # Validate Address
        #######################################################################

        self.validate_address(
            address,
        )

        #######################################################################
        # Retrieve Wallet Information
        #######################################################################

        balance = get_eth_balance(
            address,
        )

        nonce = get_nonce(
            address,
        )

        transaction_count = get_transaction_count(
            address,
        )

        #######################################################################
        # Address Classification
        #######################################################################

        # classify_address() remains the single source of truth.

        classification = classify_address(
            address,
        )

        is_contract_address = self._is_contract_address(
            classification,
        )

        #######################################################################
        # Wallet Status Report
        #######################################################################

        return {
            "address": address,

            "classification": classification,

            "is_contract": is_contract_address,

            "balance_eth": balance.get(
                "ether",
                0,
            ),

            "balance_wei": balance.get(
                "wei",
                0,
            ),

            "nonce": nonce,

            "transaction_count": transaction_count,

            "has_balance": (
                balance.get(
                    "wei",
                    0,
                ) > 0
            ),
        }


###############################################################################
# End of Part 2
###############################################################################
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
    "WalletService",
]


###############################################################################
# End of File
###############################################################################
