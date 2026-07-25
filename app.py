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
from database import get_db_manager

# Initialize database
db = get_db_manager()
import sys

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

    ###########################################################################
    # Ethereum Handlers
    ###########################################################################

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
                self._gas_optimizer()
            elif choice == "9":
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
            
            # Save to database
            try:
                db.save_wallet_inspection(address, 'ethereum', report)
            except Exception as e:
                logger.warning(f"Could not save to database: {e}")
            
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
        """Validate an Ethereum node."""
        try:
            print("\n🖥️  Ethereum Node Validation")
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
        """Compare Ethereum nodes."""
        try:
            print("\n🔄 Ethereum Node Comparison")
            print("-" * 40)
            
            node_urls = []
            print("Enter up to 5 node URLs (press Enter with empty line to stop):")
            print("Examples:")
            print("  https://ethereum.publicnode.com")
            print("  https://rpc.ankr.com/eth")
            print()
            
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

    def _gas_optimizer(self) -> None:
        """Optimize gas prices."""
        try:
            print("\n⛽ Gas Price Optimization")
            print("-" * 40)
            print("  1. Current Gas Price")
            print("  2. Gas Cost Estimate")
            print("  3. Optimal Gas Recommendations")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            from ethereum.gas import get_gas_optimizer
            optimizer = get_gas_optimizer()
            from core.display.gas_display import GasDisplay
            
            if choice == "1":
                gas_info = optimizer.get_gas_price()
                GasDisplay.display_gas_info(gas_info)
            elif choice == "2":
                gas_limit = input("Enter gas limit (default 21000): ").strip()
                gas_limit = int(gas_limit) if gas_limit else 21000
                estimate = optimizer.estimate_gas_cost(gas_limit)
                GasDisplay.display_gas_estimate(estimate)
            elif choice == "3":
                print("\n📊 Optimal Gas Recommendations")
                print("-" * 40)
                for urgency in ["slow", "standard", "fast", "instant"]:
                    rec = optimizer.get_optimal_gas_price(urgency)
                    print(f"  {urgency.title()}: {rec['recommended_gwei']} Gwei → {rec['estimated_time']}")
                print()
            else:
                print_error("Invalid choice")
                return
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Gas optimization failed: {error}")
        input("\nPress Enter to continue...")

    ###########################################################################
    # Bitcoin Handlers
    ###########################################################################

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
                self._validate_bitcoin_node()
            elif choice == "5":
                self._bitcoin_fee_optimizer()
            elif choice == "6":
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

    def _validate_bitcoin_node(self) -> None:
        """Validate a Bitcoin node."""
        try:
            print("\n🖥️  Bitcoin Node Validation")
            print("-" * 40)
            print("  1. Validate Bitcoin Network")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating Bitcoin network...")
                from bitcoin.node_validator import validate_node
                report = validate_node()
                NodeDisplay.display_node_report(report)
            else:
                print_error("Invalid choice")
                return
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Bitcoin node validation failed: {error}")
        input("\nPress Enter to continue...")

    def _bitcoin_fee_optimizer(self) -> None:
        """Optimize Bitcoin fees."""
        try:
            print("\n⛽ Bitcoin Fee Optimization")
            print("-" * 40)
            print("  1. Current Fee Estimates")
            print("  2. Fee Cost Estimate")
            print("  3. Optimal Fee Recommendations")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            from bitcoin.gas import get_fee_optimizer
            optimizer = get_fee_optimizer()
            
            if choice == "1":
                fee_info = optimizer.get_fee_estimate()
                print("\n📊 Current Fee Estimates:")
                print("-" * 40)
                if "error" in fee_info:
                    print_error(fee_info["error"])
                else:
                    print(f"  Fast:      {fee_info.get('fast', 0)} sat/byte")
                    print(f"  Standard:  {fee_info.get('standard', 0)} sat/byte")
                    print(f"  Slow:      {fee_info.get('slow', 0)} sat/byte")
                    print(f"  Source:    {fee_info.get('source', 'unknown')}")
                print()
            elif choice == "2":
                tx_size = input("Enter transaction size in bytes (default 250): ").strip()
                tx_size = int(tx_size) if tx_size else 250
                fee_rate = input("Enter fee rate in sat/byte (default 10): ").strip()
                fee_rate = int(fee_rate) if fee_rate else 10
                estimate = optimizer.estimate_fee(tx_size, fee_rate)
                print("\n📊 Fee Estimate:")
                print("-" * 40)
                print(f"  Transaction Size: {estimate.get('tx_size_bytes', 0)} bytes")
                print(f"  Fee Rate:         {estimate.get('fee_rate_sat_byte', 0)} sat/byte")
                print(f"  Fee (Satoshis):   {estimate.get('fee_satoshis', 0):,}")
                print(f"  Fee (BTC):        {estimate.get('fee_btc', 0)} BTC")
                print()
            elif choice == "3":
                print("\n📊 Optimal Fee Recommendations:")
                print("-" * 40)
                for urgency in ["slow", "standard", "fast"]:
                    rec = optimizer.get_optimal_fee(urgency)
                    if "error" in rec:
                        print_error(rec["error"])
                    else:
                        print(f"  {urgency.title()}: {rec.get('recommended_fee_rate_sat_byte', 0)} sat/byte → {rec.get('estimated_time', 'unknown')}")
                print()
            else:
                print_error("Invalid choice")
                return
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Bitcoin fee optimization failed: {error}")
        input("\nPress Enter to continue...")

    ###########################################################################
    # TRON Handlers
    ###########################################################################

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
                self._explore_tron_block()
            elif choice == "5":
                self._analyze_tron_transaction()
            elif choice == "6":
                self._validate_tron_node()
            elif choice == "7":
                self._compare_tron_nodes()
            elif choice == "8":
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

    def _explore_tron_block(self) -> None:
        """Explore a TRON block."""
        try:
            from core.input import get_block_input
            
            block_number = get_block_input("Enter TRON block number or 'latest'")
            if block_number is None:
                return
            
            print("\n⏳ Fetching TRON block...")
            from tron.blocks import get_block, get_latest_block_number
            
            if block_number == "latest":
                block_num = get_latest_block_number()
                report = get_block(block_num)
            else:
                report = get_block(block_number)
            
            BlockDisplay.display_block_report(report)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON block exploration failed: {error}")
        input("\nPress Enter to continue...")

    def _analyze_tron_transaction(self) -> None:
        """Analyze a TRON transaction."""
        try:
            from core.input import get_text_input
            
            tx_hash = get_text_input("Enter TRON transaction hash")
            if not tx_hash:
                return
            
            print("\n⏳ Analyzing TRON transaction...")
            from tron.transactions import get_transaction
            report = get_transaction(tx_hash)
            
            TransactionDisplay.display_transaction_report(report)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON transaction analysis failed: {error}")
        input("\nPress Enter to continue...")

    def _validate_tron_node(self) -> None:
        """Validate a TRON node."""
        try:
            print("\n🖥️  TRON Node Validation")
            print("-" * 40)
            print("  1. Validate Current TRON Node")
            print("  2. Validate Custom TRON Node")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating current TRON node...")
                from tron.node_validator import validate_node
                report = validate_node()
                NodeDisplay.display_node_report(report)
            elif choice == "2":
                from core.input import get_text_input
                rpc_url = get_text_input("Enter TRON RPC URL")
                if not rpc_url:
                    return
                print(f"\n⏳ Validating TRON node: {rpc_url}")
                from tron.node_validator import validate_node
                report = validate_node(rpc_url)
                NodeDisplay.display_node_report(report)
            else:
                print_error("Invalid choice")
                return
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON node validation failed: {error}")
        input("\nPress Enter to continue...")

    def _compare_tron_nodes(self) -> None:
        """Compare multiple TRON nodes."""
        try:
            print("\n🔄 TRON Node Comparison")
            print("-" * 40)
            
            node_urls = []
            print("Enter up to 5 TRON node URLs (press Enter with empty line to stop):")
            print("Examples:")
            print("  https://api.trongrid.io")
            print("  https://api.shasta.trongrid.io")
            print()
            
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
            
            print(f"\n⏳ Comparing {len(node_urls)} TRON nodes...")
            from tron.node_validator import compare_nodes
            comparison = compare_nodes(node_urls)
            
            NodeDisplay.display_node_comparison(comparison)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"TRON node comparison failed: {error}")
        input("\nPress Enter to continue...")

    ###########################################################################
    # Utility Methods
    ###########################################################################

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
        print("  • Block Exploration (Ethereum, Bitcoin, TRON)")
        print("  • Transaction Analysis (Ethereum, Bitcoin, TRON)")
        print("  • Node Validation & Comparison")
        print("  • Gas/Energy/Fee Optimization")
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


###############################################################################
# End of File
###############################################################################
