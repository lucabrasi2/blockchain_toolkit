"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Main Application
Author  : Jaramogi Diddy

Main entry point for the Universal Blockchain Platform.
"""

from core.banner import show_banner
from core.menu import main_menu
from ethereum.menu import ethereum_menu

from core.logger import get_logger

from controllers.ethereum_controller import EthereumController
from controllers.network_controller import NetworkController

logger = get_logger(__name__)


def ethereum_section():
    """
    Ethereum submenu.
    """

    ethereum_controller = EthereumController()
    network_controller = NetworkController()

    logger.info("Entered Ethereum module.")

    while True:

        option = ethereum_menu()

        if option == "1":

            logger.info("Wallet Inspector selected.")

            ethereum_controller.wallet_inspector()

        elif option == "2":

            logger.info("Token Inspector selected.")

            print("\nToken Inspector Coming Soon")
            input("Press Enter to continue...")

        elif option == "3":

            logger.info("Block Explorer selected.")

            print("\nBlock Explorer Coming Soon")
            input("Press Enter to continue...")

        elif option == "4":

            logger.info("Transaction Explorer selected.")

            print("\nTransaction Explorer Coming Soon")
            input("Press Enter to continue...")

        elif option == "5":

            logger.info("Network Information selected.")

            network_controller.network_information()

        elif option == "6":

            logger.info("Leaving Ethereum module.")

            break

        else:

            logger.warning("Invalid Ethereum menu option.")

            print("\nInvalid option.")
            input("Press Enter to continue...")


def main():
    """
    Main application loop.
    """

    logger.info("Universal Blockchain Platform started.")

    while True:

        show_banner()

        choice = main_menu()

        if choice == "1":

            logger.info("Ethereum selected from main menu.")

            ethereum_section()

        elif choice == "2":

            logger.info("Bitcoin selected.")

            print("\nBitcoin module is under development.")
            input("Press Enter to continue...")

        elif choice == "3":

            logger.info("TRON selected.")

            print("\nTRON module is under development.")
            input("Press Enter to continue...")

        elif choice == "4":

            logger.info("Application closed.")

            print("\nThank you for using Universal Blockchain Platform.")

            break

        else:

            logger.warning("Invalid main menu option.")

            print("\nInvalid choice.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()