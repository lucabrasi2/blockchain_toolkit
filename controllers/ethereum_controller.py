"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Ethereum Controller
Author  : Jaramogi Didy

Handles user interaction for Ethereum operations.
"""

from core.logger import get_logger

from services.ethereum.wallet_service import WalletService

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
    UBPException,
)

logger = get_logger(__name__)


class EthereumController:
    """
    Controller responsible for Ethereum user interactions.
    """

    def __init__(self):
        """
        Initialize the Ethereum controller.
        """

        self.wallet_service = WalletService()

        logger.info("EthereumController initialized.")

    def wallet_inspector(self):
        """
        Inspect an Ethereum wallet.
        """

        logger.info("Wallet Inspector started.")

        address = input("\nEnter Ethereum wallet address:\n> ").strip()

        try:

            report = self.wallet_service.get_wallet_report(address)

            print("\n========== WALLET REPORT ==========")
            print(f"Address : {report['address']}")
            print(f"Balance : {report['balance_eth']} ETH")
            print(f"Wei     : {report['balance_wei']}")
            print(f"Nonce   : {report['nonce']}")

            logger.info("Wallet report displayed successfully.")

        except InvalidWalletAddressError as error:

            logger.warning(str(error))

            print(f"\n❌ {error}")

        except UBPException as error:

            logger.error(str(error))

            print(f"\n❌ {error}")

        except Exception as error:

            logger.exception("Unexpected error during wallet inspection.")

            print(f"\nUnexpected Error: {error}")

        input("\nPress Enter to continue...")