#!/usr/bin/env python3
"""
Universal Blockchain Platform (UBP)
Module: core/menu.py
Purpose: Menu definitions for CLI
Author: UBP Engineering Team
Version: 2.2.0
"""
from core.display.utils import clear_screen, print_header, print_divider, print_error, print_info


class MainMenu:
    """Main application menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" UNIVERSAL BLOCKCHAIN PLATFORM", "=", 60)
        print()
        print(" Main Menu")
        print_divider("-", 40)
        print("  1. 🟣 Ethereum")
        print("  2. 🟠 Bitcoin")
        print("  3. 🔴 TRON")
        print("  4. 👛 Wallet Management")
        print("  5. ⚙️  Settings")
        print("  6. 📖 Help")
        print("  7. 🚪 Exit")
        print_divider("-", 40)
        return input("\nEnter your choice (1-7): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice. Please enter 1-7.")
        input("\nPress Enter to continue...")


class EthereumMenu:
    """Ethereum blockchain menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" 🟣 ETHEREUM MODULE", "=", 60)
        print()
        print(" Ethereum Operations")
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
        print_error("Invalid choice. Please enter 1-9.")
        input("\nPress Enter to continue...")


class BitcoinMenu:
    """Bitcoin blockchain menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" 🟠 BITCOIN MODULE", "=", 60)
        print()
        print(" Bitcoin Operations")
        print_divider("-", 40)
        print("  1. 👛 Inspect Wallet")
        print("  2. 🔍 Explore Block")
        print("  3. 📊 Analyze Transaction")
        print("  4. 🖥️  Validate Node")
        print("  5. 🔄 Compare Nodes")
        print("  6. ⛽ Fee Optimization")
        print("  7. 🔙 Back to Main Menu")
        print_divider("-", 40)
        return input("\nEnter your choice (1-7): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice. Please enter 1-7.")
        input("\nPress Enter to continue...")


class TronMenu:
    """TRON blockchain menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" 🔴 TRON MODULE", "=", 60)
        print()
        print(" TRON Operations")
        print_divider("-", 40)
        print("  1. 👛 Inspect Wallet")
        print("  2. 📄 Inspect Contract")
        print("  3. 💱 Inspect Token")
        print("  4. 🔍 Explore Block")
        print("  5. 📊 Analyze Transaction")
        print("  6. 🖥️  Validate Node")
        print("  7. 🔄 Compare Nodes")
        print("  8. ⚡ Energy Optimization")
        print("  9. 🔙 Back to Main Menu")
        print_divider("-", 40)
        return input("\nEnter your choice (1-9): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice. Please enter 1-9.")
        input("\nPress Enter to continue...")


class WalletMenu:
    """Wallet management menu with all features."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" 👛 WALLET MANAGEMENT", "=", 60)
        print()
        print(" Wallet Operations")
        print_divider("-", 40)
        print("  1. 🔑 Create New Wallet")
        print("  2. 📋 List All Wallets")
        print("  3. 🔍 Inspect Wallet")
        print("  4. 🗑️  Delete Wallet")
        print("  5. 🔒 Lock Wallet")
        print("  6. 🔓 Unlock Wallet")
        print("  7. 📊 Wallet Status")
        print("  8. 📤 Export Wallet")
        print("  9. 📥 Import Wallet")
        print(" 10. 💾 Backup All Wallets")
        print(" 11. 📂 Restore Wallets")
        print(" 12. 📈 Monitor Balances")
        print(" 13. 📜 Transaction History")
        print(" 14. 🔙 Back to Main Menu")
        print_divider("-", 40)
        return input("\nEnter your choice (1-14): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice. Please enter 1-14.")
        input("\nPress Enter to continue...")


class SettingsMenu:
    """Settings menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" ⚙️ SETTINGS", "=", 60)
        print()
        print(" Settings")
        print_divider("-", 40)
        print("  1. 📁 Storage Location")
        print("  2. 🌐 Default Network")
        print("  3. 🔌 Provider Selection")
        print("  4. 📊 Show Configuration")
        print("  5. 🔙 Back to Main Menu")
        print_divider("-", 40)
        return input("\nEnter your choice (1-5): ").strip()
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice. Please enter 1-5.")
        input("\nPress Enter to continue...")


class HelpMenu:
    """Help menu."""
    
    @staticmethod
    def display() -> str:
        clear_screen()
        print_header(" 📖 HELP", "=", 60)
        print()
        print(" Universal Blockchain Platform (UBP)")
        print(" Version: 3.0.0")
        print()
        print(" Features:")
        print("   • Wallet Inspection (Ethereum, Bitcoin, TRON)")
        print("   • Wallet Creation & Management")
        print("   • Wallet Export/Import")
        print("   • Wallet Backup/Restore")
        print("   • Transaction Signing (Ethereum)")
        print("   • Balance Monitoring")
        print("   • Transaction History")
        print("   • Contract Analysis (Ethereum, TRON)")
        print("   • Token Information (ERC-20, TRC-20)")
        print("   • Block Exploration")
        print("   • Transaction Analysis")
        print("   • Node Validation & Comparison")
        print("   • Gas/Energy Optimization")
        print()
        print(" Supported Blockchains:")
        print("   • Ethereum")
        print("   • Bitcoin")
        print("   • TRON")
        print()
        print(" Wallet Management:")
        print("   • Create/List/Inspect/Delete wallets")
        print("   • Lock/Unlock wallets")
        print("   • Export/Import/Backup/Restore")
        print("   • Monitor balances")
        print("   • View transaction history")
        print_divider("-", 40)
        input("\nPress Enter to continue...")
        return "back"
    
    @staticmethod
    def invalid_choice() -> None:
        print_error("Invalid choice.")
        input("\nPress Enter to continue...")


# Backward compatibility
def main_menu() -> str:
    return MainMenu.display()


def ethereum_menu() -> str:
    return EthereumMenu.display()


def bitcoin_menu() -> str:
    return BitcoinMenu.display()


def tron_menu() -> str:
    return TronMenu.display()