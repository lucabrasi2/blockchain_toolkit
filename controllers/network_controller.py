"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Network Controller
Author  : jaramogi Diddy

Handles Ethereum network information requests.
"""

from core.logger import get_logger

from services.ethereum.network_service import NetworkService

from exceptions.blockchain_exceptions import (
    UBPException,
)

logger = get_logger(__name__)


class NetworkController:
    """
    Controller for Ethereum network operations.
    """

    def __init__(self):
        """
        Initialize the controller.
        """

        self.network_service = NetworkService()

        logger.info("NetworkController initialized.")

    def network_information(self):
        """
        Display Ethereum network information.
        """

        logger.info("Displaying network information.")

        try:

            report = self.network_service.get_network_report()

            print("\n========== ETHEREUM NETWORK ==========\n")

            print(f"Connected      : {report['connected']}")
            print(f"Chain ID       : {report['chain_id']}")
            print(f"Latest Block   : {report['latest_block']}")
            print(f"Gas Price      : {report['gas_price_gwei']:.2f} Gwei")
            print(f"Client Version : {report['client_version']}")

            logger.info("Network information displayed.")

        except UBPException as error:

            logger.error(str(error))
            print(f"\n❌ {error}")

        except Exception as error:

            logger.exception("Unexpected network error.")
            print(f"\nUnexpected Error: {error}")

        input("\nPress Enter to continue...")
        