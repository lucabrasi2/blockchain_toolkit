"""
Ethereum Wallet Service

Business logic for Ethereum wallet operations.
"""

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

from ubp_logging.logger import logger


class WalletService:
    """
    Ethereum wallet business service.
    """

    def validate_wallet(self, address):
        """
        Validate an Ethereum wallet address.

        Raises:
            InvalidWalletAddressError:
                If the wallet address is invalid.
        """

        logger.info("Validating Ethereum wallet address.")

        if not is_valid_address(address):
            logger.warning(f"Invalid wallet address received: {address}")

            raise InvalidWalletAddressError(
                "Invalid Ethereum wallet address."
            )

        logger.info("Ethereum wallet address validation successful.")

        return True

    def get_wallet_report(self, address):
        """
        Generate a complete wallet report.

        Returns:
            dict:
                Wallet information including address,
                ETH balance, Wei balance, and nonce.
        """

        logger.info("Generating Ethereum wallet report.")

        # Validate wallet first
        self.validate_wallet(address)

        # Retrieve blockchain data
        balance = get_eth_balance(address)
        nonce = get_nonce(address)

        report = {
            "address": address,
            "balance_eth": balance["ether"],
            "balance_wei": balance["wei"],
            "nonce": nonce,
        }

        logger.info("Ethereum wallet report successfully generated.")

        return report