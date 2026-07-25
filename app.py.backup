#!/usr/bin/env python3
"""
Universal Blockchain Platform (UBP)

Module:
    Application Entry Point

Purpose:
    Main application entry point that
    coordinates the UBP platform.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import sys
from typing import Optional

from core.logger import get_logger
from core.menu import MainMenu, EthereumMenu, BitcoinMenu, TronMenu
from core.display import (
    WalletDisplay,
    ContractDisplay,
    TokenDisplay,
    BlockDisplay,
    TransactionDisplay,
    NodeDisplay,
)
from core.display import print_error, print_info, print_success, print_warning

from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from config.settings import Settings


logger = get_logger(__name__)


class App:
    """
    Main application class.
    """

    def __init__(self):
        """Initialize the application."""
        self.running = True
        self.settings = Settings()

        logger.info("Initializing controllers...")
        self.ethereum_controller = EthereumController()
        self.bitcoin_controller = BitcoinController()
        self.tron_controller = TronController()

        logger.info("Application initialized successfully.")

    def run(self) -> None:
        """
        Run the main application loop.
        """
        try:
            while self.running:
                choice = MainMenu.display()

                if choice == "1":
                    self._handle_ethereum_menu()
                elif choice == "2":
                    self._handle_bitcoin_menu()
                elif choice == "3":
                    self._handle_tron_menu()
                elif choice == "4":
                    self._show_settings()
                elif choice == "5":
                    self._show_help()
                elif choice == "6":
                    self._exit_app()
                else:
                    MainMenu.invalid_choice()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            print(f"\n❌ An unexpected error occurred: {error}")
            sys.exit(1)

    def _handle_ethereum_menu(self) -> None:
        """Handle Ethereum menu."""
        while True:
            choice = EthereumMenu.display()

            if choice == "1":
                self._inspect_wallet()
            elif choice == "2":
                self._inspect_contract()
            elif choice == "3":
                self._inspect_token()
            elif choice == "4":
                self._explore_block()
            elif choice == "5":
                self._analyze_transaction()
            elif choice == "6":
                self._validate_node()
            elif choice == "7":
                self._compare_nodes()
            elif choice == "8":
                break
            else:
                EthereumMenu.invalid_choice()

    def _inspect_wallet(self) -> None:
        """Inspect an Ethereum wallet."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter Ethereum wallet address")
            if not address:
                return
            print("\n⏳ Inspecting wallet...")
            report = self.ethereum_controller.wallet_inspector(address)
            WalletDisplay.display_wallet_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Wallet inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _inspect_contract(self) -> None:
        """Inspect an Ethereum contract."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter Ethereum contract address")
            if not address:
                return
            print("\n⏳ Inspecting contract...")
            report = self.ethereum_controller.contract_inspector(address)
            ContractDisplay.display_contract_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Contract inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _inspect_token(self) -> None:
        """Inspect an Ethereum token."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter ERC-20 token address")
            if not address:
                return
            print("\n⏳ Inspecting token...")
            report = self.ethereum_controller.token_inspector(address)
            TokenDisplay.display_token_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Token inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _explore_block(self) -> None:
        """Explore an Ethereum block."""
        try:
            from core.input import get_block_input
            block_number = get_block_input("Enter block number")
            if block_number is None:
                return
            print("\n⏳ Fetching block...")
            report = self.ethereum_controller.block_explorer(block_number)
            BlockDisplay.display_block_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Block exploration failed: {error}")
        input("\nPress Enter to continue...")

    def _analyze_transaction(self) -> None:
        """Analyze an Ethereum transaction."""
        try:
            from core.input import get_transaction_hash
            tx_hash = get_transaction_hash("Enter transaction hash")
            if not tx_hash:
                return
            print("\n⏳ Analyzing transaction...")
            report = self.ethereum_controller.transaction_analyzer(tx_hash)
            TransactionDisplay.display_transaction_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Transaction analysis failed: {error}")
        input("\nPress Enter to continue...")

    def _validate_node(self) -> None:
        """Validate a blockchain node."""
        try:
            print("\n🖥️  Node Validation")
            print("-" * 40)
            print("  1. Validate Current Node")
            print("  2. Validate Custom Node")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating current node...")
                report = self.ethereum_controller.node_validator()
            elif choice == "2":
                from core.input import get_text_input
                rpc_url = get_text_input("Enter RPC URL")
                if not rpc_url:
                    return
                print(f"\n⏳ Validating node: {rpc_url}")
                report = self.ethereum_controller.node_validator(rpc_url)
            else:
                print_error("Invalid choice")
                return
            
            NodeDisplay.display_node_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Node validation failed: {error}")
        input("\nPress Enter to continue...")

    def _compare_nodes(self) -> None:
        """Compare multiple nodes."""
        try:
            print("\n🔄 Node Comparison")
            print("-" * 40)
            
            node_urls = []
            print("Enter up to 5 node URLs (press Enter with empty line to stop):")
            
            for i in range(5):
                url = input(f"  Node {i+1}: ").strip()
                if not url:
                    break
                node_urls.append(url)
            
            if not node_urls:
                print_error("No nodes to compare")
                return
            
            if len(node_urls) < 2:
                print_warning("Need at least 2 nodes to compare")
                return
            
            print(f"\n⏳ Comparing {len(node_urls)} nodes...")
            comparison = self.ethereum_controller.compare_nodes(node_urls)
            NodeDisplay.display_node_comparison(comparison)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Node comparison failed: {error}")
        input("\nPress Enter to continue...")

    def _handle_bitcoin_menu(self) -> None:
        """Handle Bitcoin menu."""
        while True:
            choice = BitcoinMenu.display()

            if choice == "1":
                self._inspect_bitcoin_wallet()
            elif choice == "2":
                self._explore_bitcoin_block()
            elif choice == "3":
                self._analyze_bitcoin_transaction()
            elif choice == "4":
                break
            else:
                BitcoinMenu.invalid_choice()

    def _inspect_bitcoin_wallet(self) -> None:
        """Inspect a Bitcoin wallet."""
        try:
            from core.input import get_btc_address
            address = get_btc_address()
            if not address:
                return
            print("\n⏳ Inspecting Bitcoin wallet...")
            report = self.bitcoin_controller.wallet_inspector(address)
            WalletDisplay.display_wallet_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Bitcoin wallet inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _explore_bitcoin_block(self) -> None:
        """Explore a Bitcoin block."""
        try:
            from core.input import get_block_input
            block = get_block_input("Enter Bitcoin block number or 'latest'")
            if block is None:
                return
            print("\n⏳ Fetching Bitcoin block...")
            report = self.bitcoin_controller.block_explorer(block)
            BlockDisplay.display_block_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Bitcoin block exploration failed: {error}")
        input("\nPress Enter to continue...")

    def _analyze_bitcoin_transaction(self) -> None:
        """Analyze a Bitcoin transaction."""
        try:
            from core.input import get_text_input
            tx_hash = get_text_input("Enter Bitcoin transaction hash")
            if not tx_hash:
                return
            print("\n⏳ Analyzing Bitcoin transaction...")
            report = self.bitcoin_controller.transaction_analyzer(tx_hash)
            TransactionDisplay.display_transaction_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"Bitcoin transaction analysis failed: {error}")
        input("\nPress Enter to continue...")

    def _handle_tron_menu(self) -> None:
        """Handle TRON menu."""
        while True:
            choice = TronMenu.display()

            if choice == "1":
                self._inspect_tron_wallet()
            elif choice == "2":
                self._inspect_tron_contract()
            elif choice == "3":
                self._inspect_tron_token()
            elif choice == "4":
                break
            else:
                TronMenu.invalid_choice()

    def _inspect_tron_wallet(self) -> None:
        """Inspect a TRON wallet."""
        try:
            from core.input import get_tron_address
            address = get_tron_address()
            if not address:
                return
            print("\n⏳ Inspecting TRON wallet...")
            report = self.tron_controller.wallet_inspector(address)
            WalletDisplay.display_wallet_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON wallet inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _inspect_tron_contract(self) -> None:
        """Inspect a TRON contract."""
        try:
            from core.input import get_tron_address
            address = get_tron_address("Enter TRON contract address")
            if not address:
                return
            print("\n⏳ Inspecting TRON contract...")
            report = self.tron_controller.contract_inspector(address)
            ContractDisplay.display_contract_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON contract inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _inspect_tron_token(self) -> None:
        """Inspect a TRON token."""
        try:
            from core.input import get_tron_address
            address = get_tron_address("Enter TRC-20 token address")
            if not address:
                return
            print("\n⏳ Inspecting TRON token...")
            report = self.tron_controller.token_inspector(address)
            TokenDisplay.display_token_report(report)
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON token inspection failed: {error}")
        input("\nPress Enter to continue...")

    def _show_settings(self) -> None:
        """Show settings."""
        print("\n⚙️  Settings")
        print("=" * 60)
        print(f"  Network: {self.settings.get('network', 'mainnet')}")
        print(f"  RPC URL: {self.settings.get('rpc_url', 'Not set')}")
        print(f"  Provider: {self.settings.get('provider', 'auto')}")
        print("\n  To change settings, edit .env file")
        input("\nPress Enter to continue...")

    def _show_help(self) -> None:
        """Show help information."""
        print("\n📖 HELP")
        print("=" * 60)
        print("  Universal Blockchain Platform (UBP)")
        print("  Version: 2.0.0")
        print()
        print("  Features:")
        print("  • Wallet Inspection (Ethereum, Bitcoin, TRON)")
        print("  • Contract Analysis (Ethereum, TRON)")
        print("  • Token Information (ERC-20, TRC-20)")
        print("  • Block Exploration (Ethereum, Bitcoin)")
        print("  • Transaction Analysis (Ethereum, Bitcoin)")
        print("  • Node Validation & Comparison")
        print()
        print("  Supported Blockchains:")
        print("  • 🟣 Ethereum")
        print("  • 🟠 Bitcoin")
        print("  • 🔴 TRON")
        print()
        input("Press Enter to continue...")

    def _exit_app(self) -> None:
        """Exit the application."""
        print("\n👋 Thank you for using UBP!")
        print("   Goodbye!")
        self.running = False
        sys.exit(0)


def main() -> None:
    """Main entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()