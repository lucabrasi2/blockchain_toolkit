"""
Universal Blockchain Platform (UBP)

Version : 1.3.0
Module  : Bitcoin Controller
Author  : Jaramogi Diddy

Controller for Bitcoin-related operations.
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from services.bitcoin import (
    BitcoinWalletService,
    BitcoinBlockService,
    BitcoinTransactionService,
)

logger = get_logger(__name__)


class BitcoinController:
    """
    Bitcoin Controller for handling blockchain interactions.
    """

    def __init__(self):
        """Initialize the Bitcoin Controller."""
        self.wallet_service = BitcoinWalletService()
        self.block_service = BitcoinBlockService()
        self.transaction_service = BitcoinTransactionService()
        logger.info("BitcoinController initialized.")

    def wallet_inspector(self, address: str) -> Dict[str, Any]:
        """Inspect a Bitcoin wallet address."""
        try:
            logger.info(f"Inspecting Bitcoin wallet: {address}")
            report = self.wallet_service.get_wallet_report(address)
            logger.info("Bitcoin wallet inspection completed successfully.")
            return report
        except Exception as error:
            logger.error(f"Unexpected wallet inspector error: {error}")
            raise

    def block_explorer(self, block_identifier) -> Dict[str, Any]:
        """Explore a Bitcoin block."""
        try:
            logger.info(f"Exploring Bitcoin block: {block_identifier}")
            report = self.block_service.get_block_report(block_identifier)
            logger.info("Bitcoin block exploration completed successfully.")
            return report
        except Exception as error:
            logger.error(f"Unexpected block explorer error: {error}")
            raise

    def transaction_analyzer(self, tx_hash: str) -> Dict[str, Any]:
        """Analyze a Bitcoin transaction."""
        try:
            logger.info(f"Analyzing Bitcoin transaction: {tx_hash}")
            report = self.transaction_service.get_transaction_report(tx_hash)
            logger.info("Bitcoin transaction analysis completed successfully.")
            return report
        except Exception as error:
            logger.error(f"Unexpected transaction analyzer error: {error}")
            raise