"""
Universal Blockchain Platform (UBP)

Module:
    Application Menus

Purpose:
    Display and handle all application menus.

Responsibilities:
    • Display main menu
    • Display blockchain-specific menus
    • Get user selections
    • Validate menu input
    • Show help information

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from core.display.utils import (
    clear_screen,
    print_header,
    print_divider,
    print_error,
    print_info,
    print_bold,
)


class MainMenu:
    """
    Main application menu.
    """

    @staticmethod
    def display() -> str:
        """
        Display the main menu and get user choice.

        Returns
        -------
        str
            User's menu selection.
        """
        clear_screen()
        print_header("🌐 UNIVERSAL BLOCKCHAIN PLATFORM (UBP)", "=", 60)
        print("  Version: 2.0.0")
        print("  Author: Jaramogi Diddy")
        print_divider("=", 60)
        print()

        print("📋 MAIN MENU")
        print_divider("-", 40)
        print("  1. 🟣 Ethereum")
        print("  2. 🟠 Bitcoin")
        print("  3. 🔴 TRON")
        print("  4. ⚙️  Settings")
        print("  5. 📖 Help")
        print("  6. 🚪 Exit")
        print_divider("-", 40)

        return input("\nEnter your choice (1-6): ").strip()

    @staticmethod
    def invalid_choice() -> None:
        """Display invalid choice message."""
        print_error("Invalid choice. Please enter 1-6.")
        input("\nPress Enter to continue...")


class EthereumMenu:
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header("🟣 ETHEREUM MODULE", "=", 60)
        print()

        print("🔹 Ethereum Operations")
        print_divider("-", 40)
        print("  1. 👛 Inspect Wallet")
        print("  2. 📄 Inspect Contract")
        print("  3. 💱 Inspect Token")
        print("  4. 🔍 Explore Block")
        print("  5. 📊 Analyze Transaction")
        print("  6. 🖥️  Validate Node")
        print("  7. 🔄 Compare Nodes")
        print("  8. ⛽ Gas Price Optimization")
        print("  9. 🔙 Back to Main Menu")
        print_divider("-", 40)

        return input("\nEnter your choice (1-9): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        """Display invalid choice message."""
        print_error("Invalid choice. Please enter 1-8.")
        input("\nPress Enter to continue...")


class BitcoinMenu:
    """
    Bitcoin blockchain menu.
    """

    @staticmethod
    def display() -> str:
        """
        Display the Bitcoin menu and get user choice.

        Returns
        -------
        str
            User's menu selection.
        """
        clear_screen()
        print_header("🟠 BITCOIN MODULE", "=", 60)
        print()

        print("🔹 Bitcoin Operations")
        print_divider("-", 40)
        print("  1. 👛 Inspect Wallet")
        print("  2. 🔍 Explore Block")
        print("  3. 📊 Analyze Transaction")
        print("  4. 🔙 Back to Main Menu")
        print_divider("-", 40)

        return input("\nEnter your choice (1-4): ").strip()

    @staticmethod
    def invalid_choice() -> None:
        """Display invalid choice message."""
        print_error("Invalid choice. Please enter 1-4.")
        input("\nPress Enter to continue...")


class TronMenu:
    """
    TRON blockchain menu.
    """

    @staticmethod
    def display() -> str:
        """
        Display the TRON menu and get user choice.

        Returns
        -------
        str
            User's menu selection.
        """
        clear_screen()
        print_header("🔴 TRON MODULE", "=", 60)
        print()

        print("🔹 TRON Operations")
        print_divider("-", 40)
        print("  1. 👛 Inspect Wallet")
        print("  2. 📄 Inspect Contract")
        print("  3. 💱 Inspect Token")
        print("  4. 🔙 Back to Main Menu")
        print_divider("-", 40)

        return input("\nEnter your choice (1-4): ").strip()

    @staticmethod
    def invalid_choice() -> None:
        """Display invalid choice message."""
        print_error("Invalid choice. Please enter 1-4.")
        input("\nPress Enter to continue...")


class SettingsMenu:
    """
    Settings menu.
    """

    @staticmethod
    def display() -> str:
        """
        Display the settings menu and get user choice.

        Returns
        -------
        str
            User's menu selection.
        """
        clear_screen()
        print_header("⚙️  SETTINGS", "=", 60)
        print()

        print("🔹 Settings Options")
        print_divider("-", 40)
        print("  1. 🔄 Switch Network")
        print("  2. 🔌 Select Provider")
        print("  3. 📝 View Configuration")
        print("  4. 🔙 Back to Main Menu")
        print_divider("-", 40)

        return input("\nEnter your choice (1-4): ").strip()

    @staticmethod
    def invalid_choice() -> None:
        """Display invalid choice message."""
        print_error("Invalid choice. Please enter 1-4.")
        input("\nPress Enter to continue...")


class HelpMenu:
    """
    Help menu.
    """

    @staticmethod
    def display() -> None:
        """
        Display help information.
        """
        clear_screen()
        print_header("📖 HELP", "=", 60)
        print()

        print("Universal Blockchain Platform (UBP)")
        print("Version: 2.0.0")
        print_divider("-", 40)
        print()

        print("📌 DESCRIPTION")
        print("  A modular, provider-independent blockchain")
        print("  intelligence platform for multiple networks.")
        print()

        print("🛠️  FEATURES")
        print("  • Wallet Inspection (Ethereum, Bitcoin, TRON)")
        print("  • Contract Analysis (Ethereum, TRON)")
        print("  • Token Information (ERC-20, TRC-20)")
        print("  • Block Exploration (Ethereum, Bitcoin)")
        print("  • Transaction Analysis (Ethereum, Bitcoin)")
        print("  • Node Validation & Comparison")
        print()

        print("⛓️  SUPPORTED BLOCKCHAINS")
        print("  • 🟣 Ethereum (Mainnet, Goerli, Sepolia)")
        print("  • 🟠 Bitcoin (Mainnet)")
        print("  • 🔴 TRON (Mainnet)")
        print()

        print("🔌 PROVIDER SUPPORT")
        print("  • Alchemy")
        print("  • Infura")
        print("  • QuickNode")
        print("  • Ankr")
        print("  • Self-hosted Nodes")
        print()

        print("📂 PROJECT STRUCTURE")
        print("  • controllers/  - Handle user input")
        print("  • services/     - Business logic")
        print("  • providers/    - Blockchain communication")
        print("  • core/display/ - Formatting and display")
        print("  • core/models/  - Data models")
        print("  • config/       - Configuration")
        print("  • tests/        - Unit tests")
        print()

        print("📚 DOCUMENTATION")
        print("  • docs/ENGINEERING_BIBLE.md")
        print("  • docs/CHANGELOG.md")
        print("  • docs/ROADMAP.md")
        print()

        input("Press Enter to continue...")


# Backward compatibility
def main_menu():
    """Legacy function for backward compatibility."""
    return MainMenu.display()