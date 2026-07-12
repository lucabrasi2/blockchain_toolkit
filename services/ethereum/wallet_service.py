"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Ethereum Wallet Service
Author  : Jaramogi Diddy

Business logic for Ethereum wallet operations.
"""

from core.logger import get_logger

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

logger = get_logger(__name__)


class WalletService:
    """
    Business logic for Ethereum wallet operations.
    """

    def __init__(self):
        """
        Initialize the wallet service.
        """
        logger.info("WalletService initialized.")

    def validate_wallet(self, address: str) -> bool:
        """
        Validate an Ethereum wallet address.

        Args:
            address (str): Ethereum wallet address.

        Returns:
            bool: True if valid.

        Raises:
            InvalidWalletAddressError:
                If the wallet address is invalid.
        """

        logger.info("Validating Ethereum wallet address.")

        if not is_valid_address(address):
            logger.warning("Invalid Ethereum wallet address received.")

            raise InvalidWalletAddressError(
                "Invalid Ethereum wallet address."
            )

        logger.info("Wallet address validation successful.")

        return True

    def get_wallet_report(self, address: str) -> dict:
        """
        Generate a complete wallet report.

        Args:
            address (str): Ethereum wallet address.

        Returns:
            dict: Wallet information.
        """

        logger.info("Generating wallet report.")

        # Validate first
        self.validate_wallet(address)

        # Retrieve blockchain information
        balance = get_eth_balance(address)
        nonce = get_nonce(address)

        report = {
            "address": address,
            "balance_eth": balance["ether"],
            "balance_wei": balance["wei"],
            "nonce": nonce,
        }

        logger.info("Wallet report generated successfully.")

        return report