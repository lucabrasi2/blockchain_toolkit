"""
Universal Blockchain Platform (UBP)

Main application entry point.
"""

from core.banner import show_banner
from core.menu import main_menu
from ethereum.menu import ethereum_menu

from controllers.ethereum_controller import wallet_inspector


def ethereum_section():
    """
    Ethereum submenu.
    """

    while True:

        option = ethereum_menu()

        if option == "1":
            wallet_inspector()

        elif option == "2":
            print("\nToken Inspector Coming Soon")
            input("Press Enter to continue...")

        elif option == "3":
            print("\nBlock Explorer Coming Soon")
            input("Press Enter to continue...")

        elif option == "4":
            print("\nTransaction Explorer Coming Soon")
            input("Press Enter to continue...")

        elif option == "5":
            print("\nNetwork Information Coming Soon")
            input("Press Enter to continue...")

        elif option == "6":
            break

        else:
            print("\nInvalid option.")
            input("Press Enter to continue...")


def main():
    """
    Main application loop.
    """

    while True:

        show_banner()

        choice = main_menu()

        if choice == "1":
            ethereum_section()

        elif choice == "2":
            print("\nBitcoin module is under development.")
            input("Press Enter to continue...")

        elif choice == "3":
            print("\nTRON module is under development.")
            input("Press Enter to continue...")

        elif choice == "4":
            print("\nThank you for using Universal Blockchain Platform.")
            break

        else:
            print("\nInvalid choice.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()