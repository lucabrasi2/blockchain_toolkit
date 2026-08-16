"""
Universal Blockchain Platform (UBP)

Module:
TRON Controller

Purpose:
Handle TRON-related operations and coordinate
between the user interface and TRON services.

Architecture:

Controller
    ↓
TRON Services
    ↓
TRON Blockchain Modules

Responsibilities:
• Coordinate TRON services
• Delegate business logic
• Handle controller-level exceptions
• Provide a stable interface for API, CLI and Web UI

Not Responsible For:
• Blockchain communication
• Blockchain business logic
• Report formatting
• Data persistence

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.0.0
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from services.tron import (
    TronBlockService,
    TronContractService,
    TronTokenService,
    TronTransactionService,
    TronWalletService,
)


logger = get_logger(__name__)


class TronController:
    """
    Controller responsible for coordinating
    TRON blockchain operations.

    The controller delegates all blockchain
    and business operations to the appropriate
    service layer.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize TRON services.
        """

        self.wallet_service = (
            TronWalletService()
        )

        self.contract_service = (
            TronContractService()
        )

        self.token_service = (
            TronTokenService()
        )

        self.block_service = (
            TronBlockService()
        )

        self.transaction_service = (
            TronTransactionService()
        )

        logger.info(
            "TronController initialized successfully."
        )

    ###########################################################################
    # Wallet Operations
    ###########################################################################

    def wallet_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect a TRON wallet.

        Parameters
        ----------
        address : str
            TRON wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet inspection report.
        """

        try:

            logger.info(
                "Inspecting TRON wallet: %s",
                address,
            )

            report = (
                self.wallet_service
                .get_wallet_report(
                    address,
                )
            )

            logger.info(
                "TRON wallet inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON wallet inspection failed."
            )

            raise

    ###########################################################################
    # Contract Operations
    ###########################################################################

    def contract_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect a TRON smart contract.

        Parameters
        ----------
        address : str
            TRON contract address.

        Returns
        -------
        dict[str, Any]
            Contract inspection report.
        """

        try:

            logger.info(
                "Inspecting TRON contract: %s",
                address,
            )

            report = (
                self.contract_service
                .get_contract_report(
                    address,
                )
            )

            logger.info(
                "TRON contract inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON contract inspection failed."
            )

            raise

    ###########################################################################
    # Token Operations
    ###########################################################################

    def token_inspector(
        self,
        address: str,
        wallet_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Inspect a TRC-20 token.

        Parameters
        ----------
        address : str
            TRC-20 token contract address.

        wallet_address : str | None
            Optional TRON wallet address used
            for token balance inspection.

        Returns
        -------
        dict[str, Any]
            TRC-20 token inspection report.
        """

        try:

            logger.info(
                "Inspecting TRON token: %s",
                address,
            )

            report = (
                self.token_service
                .get_token_report(
                    address=address,
                    wallet_address=wallet_address,
                )
            )

            logger.info(
                "TRON token inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON token inspection failed."
            )

            raise
        ###########################################################################
    # Block Operations
    ###########################################################################

    def block_explorer(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Explore a TRON block.

        Parameters
        ----------
        block_identifier : str | int
            TRON block number, block hash,
            or supported block identifier.

        Returns
        -------
        dict[str, Any]
            TRON block inspection report.
        """

        try:

            logger.info(
                "Exploring TRON block: %s",
                block_identifier,
            )

            report = (
                self.block_service
                .get_block_report(
                    block_identifier,
                )
            )

            logger.info(
                "TRON block exploration "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON block exploration failed."
            )

            raise

    ###########################################################################
    # Transaction Operations
    ###########################################################################

    def transaction_analyzer(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze a TRON transaction.

        Parameters
        ----------
        tx_hash : str
            TRON transaction hash.

        Returns
        -------
        dict[str, Any]
            TRON transaction analysis report.
        """

        try:

            logger.info(
                "Analyzing TRON transaction: %s",
                tx_hash,
            )

            report = (
                self.transaction_service
                .get_transaction_report(
                    tx_hash,
                )
            )

            logger.info(
                "TRON transaction analysis "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON transaction analysis failed."
            )

            raise

    ###########################################################################
    # Transaction Confirmation Operations
    ###########################################################################

    def transaction_confirmations(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve TRON transaction confirmations.

        Parameters
        ----------
        tx_hash : str
            TRON transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction confirmation report.
        """

        try:

            logger.info(
                "Checking TRON transaction confirmations: %s",
                tx_hash,
            )

            confirmations = (
                self.transaction_service
                .get_transaction_confirmations(
                    tx_hash,
                )
            )

            report = {
                "hash": tx_hash,
                "confirmations": confirmations,
                "status": (
                    "Confirmed"
                    if confirmations >= 19
                    else (
                        "Pending"
                        if confirmations >= 1
                        else "Unconfirmed"
                    )
                ),
            }

            logger.info(
                "TRON transaction confirmation "
                "check completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "TRON transaction confirmation "
                "check failed."
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
            f"{self.__class__.__name__}("
            f"services=5"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TronController",
]


###############################################################################
# End of File
###############################################################################