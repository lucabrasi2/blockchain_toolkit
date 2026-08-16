"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Bitcoin Controller
Author  : Jaramogi Diddy

Architecture Layer
------------------
Controller

Responsibilities
----------------
✓ Coordinate Bitcoin user requests
✓ Delegate business logic to services
✓ Log controller operations
✓ Return inspection reports

Not Responsible For
-------------------
✗ Blockchain communication
✗ Business logic
✗ Report formatting
✗ Data persistence
"""

from __future__ import annotations

from typing import Any, Dict

from core.logger import get_logger
from services.bitcoin import (
    BitcoinBlockService,
    BitcoinTransactionService,
    BitcoinWalletService,
)

logger = get_logger(__name__)


class BitcoinController:
    """
    Controller responsible for Bitcoin-related operations.

    The controller coordinates requests and delegates all
    business logic to the corresponding service layer.
    """

    def __init__(self) -> None:
        """Initialize Bitcoin services."""
        self.wallet_service = BitcoinWalletService()
        self.block_service = BitcoinBlockService()
        self.transaction_service = BitcoinTransactionService()

        logger.info("BitcoinController initialized.")

    def wallet_inspector(
        self,
        address: str,
    ) -> Dict[str, Any]:
        """
        Inspect a Bitcoin wallet.

        Parameters
        ----------
        address : str
            Bitcoin wallet address.

        Returns
        -------
        dict
            Wallet inspection report.
        """
        try:
            logger.info(
                "Inspecting Bitcoin wallet: %s",
                address,
            )

            report = self.wallet_service.get_wallet_report(
                address
            )

            logger.info(
                "Bitcoin wallet inspection completed successfully."
            )

            return report

        except Exception:
            logger.exception(
                "Bitcoin wallet inspection failed."
            )
            raise

    def block_explorer(
        self,
        block_identifier: str | int,
    ) -> Dict[str, Any]:
        """
        Explore a Bitcoin block.

        Parameters
        ----------
        block_identifier : str | int
            Block hash or block height.

        Returns
        -------
        dict
            Block inspection report.
        """
        try:
            logger.info(
                "Exploring Bitcoin block: %s",
                block_identifier,
            )

            report = self.block_service.get_block_report(
                block_identifier
            )

            logger.info(
                "Bitcoin block exploration completed successfully."
            )

            return report

        except Exception:
            logger.exception(
                "Bitcoin block exploration failed."
            )
            raise

    def transaction_analyzer(
        self,
        tx_hash: str,
    ) -> Dict[str, Any]:
        """
        Analyze a Bitcoin transaction.

        Parameters
        ----------
        tx_hash : str
            Bitcoin transaction hash.

        Returns
        -------
        dict
            Transaction analysis report.
        """
        try:
            logger.info(
                "Analyzing Bitcoin transaction: %s",
                tx_hash,
            )

            report = self.transaction_service.get_transaction_report(
                tx_hash
            )

            logger.info(
                "Bitcoin transaction analysis completed successfully."
            )

            return report

        except Exception:
            logger.exception(
                "Bitcoin transaction analysis failed."
            )
            raise