#!/usr/bin/env python3
"""
Universal Blockchain Platform (UBP)
Module: Application Entry Point
Purpose: Main application entry point with full wallet management and transaction capabilities
Author: UBP Engineering Team
Version: 3.0.0
"""
import sys
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import show_banner
from core.menu import MainMenu, EthereumMenu, BitcoinMenu, TronMenu, WalletMenu
from core.display import (
    WalletDisplay,
    ContractDisplay,
    TokenDisplay,
    BlockDisplay,
    TransactionDisplay,
    NodeDisplay,
    GasDisplay,
    print_error,
    print_success,
    print_info,
    print_warning,
)
from controllers.ethereum_controller import EthereumController
from controllers.bitcoin_controller import BitcoinController
from controllers.tron_controller import TronController
from wallets.manager import WalletManager
from wallets.storage import WalletStorage
from wallets.wallet import Wallet
from core.logger import get_logger
from database import get_db_manager
from database.models import TransactionHistory

logger = get_logger(__name__)


class App:
    """
    Main application class with full wallet management and transaction capabilities.
    """

    def __init__(self):
        """Initialize the application."""
        self.running = True
        
        # Initialize wallet system
        self.wallet_manager = WalletManager()
        self.wallet_storage = WalletStorage("data/wallets")
        
        # Initialize database
        self.db = get_db_manager()
        
        # Initialize blockchain controllers
        logger.info("Initializing controllers...")
        self.ethereum_controller = EthereumController()
        self.bitcoin_controller = BitcoinController()
        self.tron_controller = TronController()
        logger.info("Application initialized successfully.")

    def run(self):
        """Run the main application loop."""
        try:
            while self.running:
                show_banner()
                choice = MainMenu.display()

                if choice == "1":
                    self._handle_ethereum_menu()
                elif choice == "2":
                    self._handle_bitcoin_menu()
                elif choice == "3":
                    self._handle_tron_menu()
                elif choice == "4":
                    self._handle_wallet_management()
                elif choice == "5":
                    self._show_settings()
                elif choice == "6":
                    self._show_help()
                elif choice == "7":
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

    # ================================================================
    # WALLET MANAGEMENT
    # ================================================================

    def _handle_wallet_management(self):
        """Handle wallet management menu."""
        while True:
            choice = WalletMenu.display()

            if choice == "1":
                self._create_wallet()
            elif choice == "2":
                self._list_wallets()
            elif choice == "3":
                self._inspect_saved_wallet()
            elif choice == "4":
                self._delete_wallet()
            elif choice == "5":
                self._lock_wallet()
            elif choice == "6":
                self._unlock_wallet()
            elif choice == "7":
                self._wallet_status()
            elif choice == "8":
                self._export_wallet()
            elif choice == "9":
                self._import_wallet()
            elif choice == "10":
                self._backup_wallets()
            elif choice == "11":
                self._restore_wallets()
            elif choice == "12":
                self._monitor_wallet_balances()
            elif choice == "13":
                self._view_transaction_history()
            elif choice == "14":
                break
            else:
                WalletMenu.invalid_choice()

    def _create_wallet(self):
        """Create a new wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 CREATE NEW WALLET")
        print("=" * 60)

        try:
            print("\nEnter wallet details:")
            print("-" * 40)

            wallet_id = input("  Wallet ID: ").strip()
            if not wallet_id:
                print_error("Wallet ID cannot be empty")
                input("\nPress Enter to continue...")
                return

            if self.wallet_manager.wallet_exists(wallet_id):
                overwrite = input(f"\n  Wallet '{wallet_id}' already exists. Overwrite? (y/N): ").strip().lower()
                if overwrite != 'y':
                    print_info("Wallet creation cancelled.")
                    input("\nPress Enter to continue...")
                    return
                self.wallet_manager.delete_wallet(wallet_id)
                print_info(f"  Deleted existing wallet: {wallet_id}")

            address = input("  Blockchain Address: ").strip()
            if not address:
                print_error("Address cannot be empty")
                input("\nPress Enter to continue...")
                return

            print("\n  Select Blockchain:")
            print("    1. Ethereum")
            print("    2. Bitcoin")
            print("    3. TRON")
            chain_choice = input("  > ").strip()

            chain_map = {"1": "ethereum", "2": "bitcoin", "3": "tron"}
            network = chain_map.get(chain_choice, "ethereum")

            print("\n  Optional metadata (press Enter to skip):")
            purpose = input("  Purpose: ").strip()
            label = input("  Label: ").strip()

            print("\n⏳ Creating wallet...")
            metadata = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "created_by": "CLI"
            }
            if purpose:
                metadata["purpose"] = purpose
            if label:
                metadata["label"] = label

            wallet = self.wallet_manager.create_wallet(
                wallet_id=wallet_id,
                address=address,
                network=network,
                wallet_type="software",
                metadata=metadata
            )

            self.wallet_manager.save_wallet(wallet)

            print("\n" + "=" * 60)
            print(" ✅ WALLET CREATED SUCCESSFULLY")
            print("=" * 60)
            print(f"\n  ID:       {wallet.wallet_id}")
            print(f"  Address:  {wallet.address}")
            print(f"  Network:  {wallet.network}")
            print(f"  Type:     {wallet.wallet_type}")
            print(f"  Locked:   {wallet.is_locked}")
            if purpose:
                print(f"  Purpose:  {purpose}")
            if label:
                print(f"  Label:    {label}")
            print("\n" + "=" * 60)

        except Exception as e:
            logger.error(f"Wallet creation failed: {e}")
            print_error(f"Failed to create wallet: {e}")

        input("\nPress Enter to continue...")

    def _list_wallets(self):
        """List all saved wallets."""
        print("\n" + "=" * 60)
        print(" 🟣 SAVED WALLETS")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found. Create one first!")
            input("\nPress Enter to continue...")
            return

        print(f"\n  Found {len(wallets)} wallet(s):")
        print("-" * 40)

        for i, wallet_id in enumerate(wallets, 1):
            try:
                wallet = self.wallet_manager.load_wallet(wallet_id)
                status = "🔒 Locked" if wallet.is_locked else "🔓 Unlocked"
                label = wallet.metadata.get("label", "")
                label_str = f" - {label}" if label else ""
                print(f"  {i}. {wallet_id} ({wallet.network}) {status}{label_str}")
                print(f"     📍 {wallet.address[:20]}...")
                if wallet.metadata.get("purpose"):
                    print(f"     📝 {wallet.metadata['purpose']}")
            except Exception as e:
                print(f"  {i}. {wallet_id} - ⚠️ Error loading: {e}")

        print("-" * 40)
        input("\nPress Enter to continue...")

    def _inspect_saved_wallet(self):
        """Inspect a saved wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 INSPECT WALLET")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available wallets:")
        for i, wallet_id in enumerate(wallets, 1):
            print(f"  {i}. {wallet_id}")

        try:
            choice = input("\n  Enter wallet number (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(wallets):
                    wallet_id = wallets[idx]
                else:
                    print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return
            else:
                wallet_id = choice

            wallet = self.wallet_manager.load_wallet(wallet_id)

            print("\n" + "=" * 60)
            print(" 🟣 WALLET DETAILS")
            print("=" * 60)
            print(f"\n  ID:           {wallet.wallet_id}")
            print(f"  Address:      {wallet.address}")
            print(f"  Network:      {wallet.network}")
            print(f"  Type:         {wallet.wallet_type}")
            print(f"  Locked:       {wallet.is_locked}")
            print(f"  Created:      {wallet.created_at}")
            print(f"  Updated:      {wallet.updated_at}")
            print(f"  Custody Type: {wallet.custody_type}")

            if wallet.metadata:
                print("\n  Metadata:")
                for key, value in wallet.metadata.items():
                    print(f"    {key}: {value}")

            status = wallet.get_custody_status()
            print(f"\n  Custody Status:")
            print(f"    Provider Configured: {status.get('provider_configured', False)}")
            print(f"    Locked: {status.get('locked', True)}")

            # Get latest balance
            print("\n  Getting latest balance...")
            self._update_wallet_balance(wallet)

            print("\n  Options:")
            print("    1. Inspect on blockchain")
            print("    2. Sign and send transaction")
            print("    3. View transaction history")
            print("    4. Return to menu")
            sub_choice = input("\n  > ").strip()

            if sub_choice == "1":
                self._inspect_wallet_on_blockchain(wallet)
            elif sub_choice == "2":
                self._sign_and_send_transaction(wallet)
            elif sub_choice == "3":
                self._view_wallet_transactions(wallet)

        except Exception as e:
            logger.error(f"Wallet inspection failed: {e}")
            print_error(f"Failed to load wallet: {e}")

        input("\nPress Enter to continue...")

    def _inspect_wallet_on_blockchain(self, wallet):
        """Inspect a wallet on the blockchain."""
        print(f"\n⏳ Inspecting {wallet.address} on {wallet.network}...")

        try:
            if wallet.network == "ethereum":
                report = self.ethereum_controller.wallet_inspector(wallet.address)
                WalletDisplay.display_wallet_report(report)
            elif wallet.network == "bitcoin":
                report = self.bitcoin_controller.wallet_inspector(wallet.address)
                WalletDisplay.display_wallet_report(report)
            elif wallet.network == "tron":
                report = self.tron_controller.wallet_inspector(wallet.address)
                WalletDisplay.display_wallet_report(report)
            else:
                print_error(f"Unsupported network: {wallet.network}")
        except Exception as e:
            print_error(f"Blockchain inspection failed: {e}")

    # ================================================================
    # BALANCE MONITORING
    # ================================================================

    def _update_wallet_balance(self, wallet):
        """Update and display wallet balance."""
        try:
            if wallet.network == "ethereum":
                from ethereum.wallets import get_eth_balance
                balance = get_eth_balance(wallet.address)
                print(f"    Balance: {balance.get('ether', 0):.6f} ETH")
                return balance
            elif wallet.network == "bitcoin":
                from bitcoin.wallets import get_btc_balance
                balance = get_btc_balance(wallet.address)
                print(f"    Balance: {balance.get('btc', 0):.8f} BTC")
                return balance
            elif wallet.network == "tron":
                from tron.wallets import get_trx_balance
                balance = get_trx_balance(wallet.address)
                print(f"    Balance: {balance.get('trx', 0):.6f} TRX")
                return balance
        except Exception as e:
            print_warning(f"  Could not fetch balance: {e}")
            return None

    def _monitor_wallet_balances(self):
        """Monitor all wallet balances."""
        print("\n" + "=" * 60)
        print(" 🟣 WALLET BALANCE MONITOR")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print(f"\n  Monitoring {len(wallets)} wallet(s)...\n")
        print("-" * 50)

        total_eth = 0.0
        total_btc = 0.0
        total_trx = 0.0

        for wallet_id in wallets:
            try:
                wallet = self.wallet_manager.load_wallet(wallet_id)
                label = wallet.metadata.get("label", wallet_id)

                if wallet.network == "ethereum":
                    from ethereum.wallets import get_eth_balance
                    balance = get_eth_balance(wallet.address)
                    amount = balance.get('ether', 0)
                    total_eth += amount
                    print(f"  {label}: {amount:.6f} ETH")
                elif wallet.network == "bitcoin":
                    from bitcoin.wallets import get_btc_balance
                    balance = get_btc_balance(wallet.address)
                    amount = balance.get('btc', 0)
                    total_btc += amount
                    print(f"  {label}: {amount:.8f} BTC")
                elif wallet.network == "tron":
                    from tron.wallets import get_trx_balance
                    balance = get_trx_balance(wallet.address)
                    amount = balance.get('trx', 0)
                    total_trx += amount
                    print(f"  {label}: {amount:.6f} TRX")

            except Exception as e:
                print_warning(f"  {wallet_id}: Error - {e}")

        print("-" * 50)
        print(f"\n  Total ETH: {total_eth:.6f}")
        print(f"  Total BTC: {total_btc:.8f}")
        print(f"  Total TRX: {total_trx:.6f}")
        print("=" * 60)

        input("\nPress Enter to continue...")

    # ================================================================
    # TRANSACTION SIGNING
    # ================================================================

    def _sign_and_send_transaction(self, wallet):
        """Sign and send a transaction from the wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 SIGN AND SEND TRANSACTION")
        print("=" * 60)

        # Get transaction details
        print("\nEnter transaction details:")
        print("-" * 40)

        to_address = input("  Recipient Address: ").strip()
        if not to_address:
            print_error("Recipient address cannot be empty")
            return

        amount = input("  Amount: ").strip()
        if not amount:
            print_error("Amount cannot be empty")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                print_error("Amount must be greater than 0")
                return
        except ValueError:
            print_error("Invalid amount. Please enter a number.")
            return

        # Get private key
        print("\n  Enter private key (or press Enter for demo mode):")
        private_key = input("  Private Key: ").strip()

        # Unlock wallet if locked
        if wallet.is_locked:
            print("\n  Wallet is locked. Unlocking...")
            password = input("  Enter password: ").strip()
            if not password:
                password = "default-password"
            wallet.unlock(password=password)

            try:
                self.wallet_manager.save_wallet(wallet)
            except Exception as e:
                if "already exists" in str(e).lower():
                    try:
                        self.wallet_manager.delete_wallet(wallet.wallet_id)
                        self.wallet_manager.save_wallet(wallet)
                    except Exception:
                        pass
            print_success("  Wallet unlocked!")

        # Route to appropriate blockchain signer
        if wallet.network == "ethereum":
            result = self._sign_ethereum_transaction(wallet, to_address, amount, private_key)
        elif wallet.network == "bitcoin":
            result = self._sign_bitcoin_transaction(wallet, to_address, amount, private_key)
        elif wallet.network == "tron":
            result = self._sign_tron_transaction(wallet, to_address, amount, private_key)
        else:
            print_error(f"Unsupported network: {wallet.network}")
            return

        # Save transaction to history
        if result and result.get("success"):
            self._save_transaction_history(
                wallet=wallet,
                to_address=to_address,
                amount=amount,
                tx_hash=result.get("tx_hash", "pending"),
                status="pending",
                network=wallet.network
            )

        input("\nPress Enter to continue...")

    def _sign_ethereum_transaction(self, wallet, to_address, amount, private_key):
        """Sign and send an Ethereum transaction."""
        try:
            from web3 import Web3
            from ethereum.connection import get_connection
            from eth_account import Account

            w3 = get_connection()

            # Get nonce
            nonce = w3.eth.get_transaction_count(wallet.address)
            print(f"\n  Nonce: {nonce}")

            # Get gas price
            gas_price_wei = w3.eth.gas_price
            gas_price_gwei = gas_price_wei / 1_000_000_000
            print(f"  Gas Price: {gas_price_gwei:.2f} Gwei")

            # Build transaction
            checksum_to = Web3.to_checksum_address(to_address)
            checksum_from = Web3.to_checksum_address(wallet.address)

            transaction = {
                'to': checksum_to,
                'from': checksum_from,
                'value': Web3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': gas_price_wei,
                'nonce': nonce,
                'chainId': w3.eth.chain_id,
            }

            # Estimate gas
            try:
                gas_estimate = w3.eth.estimate_gas(transaction)
                transaction['gas'] = gas_estimate
                print(f"  Estimated Gas: {gas_estimate}")
                total_cost_eth = (gas_estimate * gas_price_wei) / 1_000_000_000_000_000_000
                print(f"  Estimated Fee: {total_cost_eth:.6f} ETH")
            except Exception as e:
                print_warning(f"  Gas estimation warning: {e}")

            # Confirm
            print("\n" + "-" * 40)
            print("  Transaction Summary:")
            print(f"    From: {wallet.address}")
            print(f"    To: {to_address}")
            print(f"    Amount: {amount} ETH")
            print(f"    Gas: {transaction['gas']}")
            print(f"    Gas Price: {gas_price_gwei:.2f} Gwei")
            print("-" * 40)

            confirm = input("\n  Confirm and send transaction? (y/N): ").strip().lower()
            if confirm != 'y':
                print_info("Transaction cancelled.")
                return {"success": False}

            if private_key:
                print("\n⏳ Signing and sending transaction...")

                if private_key.startswith('0x'):
                    private_key = private_key[2:]

                signed = Account.sign_transaction(transaction, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                tx_hash_hex = tx_hash.hex()

                print("\n" + "=" * 60)
                print(" ✅ TRANSACTION SENT!")
                print("=" * 60)
                print(f"\n  Transaction Hash: {tx_hash_hex}")
                print(f"  Amount: {amount} ETH")
                print(f"  To: {to_address}")
                print(f"\n  View on Etherscan:")
                print(f"  https://etherscan.io/tx/{tx_hash_hex}")
                print("=" * 60)

                return {"success": True, "tx_hash": tx_hash_hex}
            else:
                print("\n" + "=" * 60)
                print(" ℹ️  DEMO MODE - No private key provided")
                print("=" * 60)
                print("\n  Transaction would be sent with the following data:")
                print(json.dumps({k: str(v) for k, v in transaction.items()}, indent=2))
                print("=" * 60)

                return {"success": True, "tx_hash": "demo_tx_hash"}

        except Exception as e:
            logger.error(f"Ethereum transaction failed: {e}")
            print_error(f"Transaction failed: {e}")
            return {"success": False}

    def _sign_bitcoin_transaction(self, wallet, to_address, amount, private_key):
        """Sign and send a Bitcoin transaction."""
        print("\n" + "=" * 60)
        print(" 🟠 BITCOIN TRANSACTION SIGNING")
        print("=" * 60)
        
        try:
            # Validate inputs
            if not to_address:
                print_error("Recipient address cannot be empty")
                return {"success": False}
            
            if amount <= 0:
                print_error("Amount must be greater than 0")
                return {"success": False}
            
            # Check if private key is provided
            if not private_key:
                print_info("\n  Demo mode: Showing transaction details only")
                print("\n  Transaction would be sent with:")
                print(f"    From: {wallet.address}")
                print(f"    To: {to_address}")
                print(f"    Amount: {amount} BTC")
                print("\n  To actually send, provide a private key.")
                return {"success": False}
            
            # Import Bitcoin libraries
            try:
                from bitcoinlib.transactions import Transaction
                from bitcoinlib.keys import Key
                from bitcoinlib.services.services import Service
            except ImportError:
                print_error("Bitcoin libraries not installed. Please install: pip install bitcoinlib")
                return {"success": False}
            
            # Get Bitcoin provider connection
            from bitcoin.connection import get_connection
            client = get_connection()
            
            print("\n⏳ Building Bitcoin transaction...")
            
            # Get UTXOs for the address
            try:
                address_info = client.get_address(wallet.address)
                if "error" in address_info:
                    print_error(f"Could not fetch address info: {address_info['error']}")
                    return {"success": False}
                
                balance_satoshis = address_info.get("balance_satoshis", 0)
                if balance_satoshis <= 0:
                    print_error("Insufficient balance")
                    return {"success": False}
                
                print(f"  Balance: {address_info.get('balance', 0):.8f} BTC")
                
            except Exception as e:
                print_error(f"Failed to fetch balance: {e}")
                return {"success": False}
            
            # Create a key from private key
            try:
                if private_key.startswith('0x'):
                    private_key = private_key[2:]
                
                # Try to create key
                key = Key(import_key=private_key, network='bitcoin')
                print(f"  Public Key: {key.public_hex[:20]}...")
                
            except Exception as e:
                print_error(f"Invalid private key: {e}")
                return {"success": False}
            
            # Build transaction
            try:
                # Convert amount to satoshis
                amount_satoshis = int(amount * 100_000_000)
                
                # Get UTXOs
                utxos = []
                try:
                    # Use the provider to get UTXOs
                    utxo_data = client.get_address_utxos(wallet.address) if hasattr(client, 'get_address_utxos') else []
                    
                    if utxo_data:
                        # Filter and prepare UTXOs
                        total_input = 0
                        for utxo in utxo_data[:10]:  # Limit to first 10 UTXOs
                            total_input += utxo.get('value', 0)
                            utxos.append(utxo)
                        
                        if total_input < amount_satoshis:
                            print_error(f"Insufficient funds. Required: {amount_satoshis} sat, Available: {total_input} sat")
                            return {"success": False}
                        
                        print(f"  Using {len(utxos)} UTXOs, total: {total_input} satoshis")
                    else:
                        print_info("  Using default UTXO selection")
                        
                except Exception as e:
                    print_warning(f"  UTXO fetch warning: {e}")
                    print_info("  Using simplified transaction mode")
                
                # Build transaction using bitcoinlib
                try:
                    # Create outputs
                    outputs = [
                        {'address': to_address, 'value': amount_satoshis}
                    ]
                    
                    # Add change output if needed
                    if total_input > amount_satoshis + 10000:  # 10,000 satoshi fee
                        change = total_input - amount_satoshis - 10000
                        if change > 10000:
                            outputs.append({'address': wallet.address, 'value': change})
                            print(f"  Change: {change} satoshis")
                    
                    # Create transaction
                    t = Transaction(network='bitcoin')
                    
                    # Add inputs
                    for utxo in utxos[:5]:  # Limit to 5 inputs for simplicity
                        t.add_input(
                            txid=utxo.get('txid'),
                            output_n=utxo.get('vout', 0),
                            keys=[key]
                        )
                    
                    # Add outputs
                    for output in outputs:
                        t.add_output(
                            address=output['address'],
                            value=output['value']
                        )
                    
                    # Sign the transaction
                    t.sign(keys=[key])
                    
                    # Get raw transaction
                    raw_tx = t.raw_hex()
                    print(f"  Raw Transaction: {raw_tx[:20]}...")
                    
                except Exception as e:
                    print_warning(f"  Advanced transaction building failed: {e}")
                    print_info("  Using simplified transaction format...")
                    
                    # Fallback: Use a simple transaction structure
                    raw_tx = self._create_simple_bitcoin_transaction(
                        wallet.address, to_address, amount_satoshis, private_key
                    )
                    if not raw_tx:
                        print_error("Failed to create transaction")
                        return {"success": False}
                
            except Exception as e:
                print_error(f"Transaction building failed: {e}")
                return {"success": False}
            
            # Confirm transaction
            print("\n" + "-" * 40)
            print("  Transaction Summary:")
            print(f"    From: {wallet.address[:20]}...")
            print(f"    To: {to_address[:20]}...")
            print(f"    Amount: {amount} BTC")
            print(f"    Fee: ~0.0001 BTC")
            print("-" * 40)
            
            confirm = input("\n  Confirm and broadcast transaction? (y/N): ").strip().lower()
            if confirm != 'y':
                print_info("Transaction cancelled.")
                return {"success": False}
            
            # Broadcast transaction
            print("\n⏳ Broadcasting transaction...")
            
            try:
                # Use bitcoinlib service to broadcast
                service = Service()
                tx_hash = service.sendrawtransaction(raw_tx)
                
                print("\n" + "=" * 60)
                print(" ✅ BITCOIN TRANSACTION SENT!")
                print("=" * 60)
                print(f"\n  Transaction Hash: {tx_hash}")
                print(f"  Amount: {amount} BTC")
                print(f"  To: {to_address}")
                print(f"\n  View on Blockchair:")
                print(f"  https://blockchair.com/bitcoin/transaction/{tx_hash}")
                print("=" * 60)
                
                return {"success": True, "tx_hash": tx_hash}
                
            except Exception as e:
                print_error(f"Broadcast failed: {e}")
                return {"success": False}
            
        except Exception as e:
            logger.error(f"Bitcoin transaction failed: {e}")
            print_error(f"Transaction failed: {e}")
            return {"success": False}

    def _create_simple_bitcoin_transaction(self, from_address, to_address, amount_satoshis, private_key):
        """Create a simple Bitcoin transaction."""
        try:
            from bitcoinlib.transactions import Transaction
            from bitcoinlib.keys import Key
            
            # Create key from private key
            key = Key(import_key=private_key, network='bitcoin')
            
            # Create a transaction
            t = Transaction(network='bitcoin')
            
            # Add output
            t.add_output(address=to_address, value=amount_satoshis)
            
            # Add change output
            t.add_output(address=from_address, value=amount_satoshis - 10000)  # Simplified
            
            # Sign
            t.sign(keys=[key])
            
            return t.raw_hex()
            
        except Exception as e:
            logger.error(f"Simple transaction creation failed: {e}")
            return None

    def _sign_tron_transaction(self, wallet, to_address, amount, private_key):
        """Sign and send a TRON transaction."""
        print("\n" + "=" * 60)
        print(" 🔴 TRON TRANSACTION SIGNING")
        print("=" * 60)
        
        try:
            # Validate inputs
            if not to_address:
                print_error("Recipient address cannot be empty")
                return {"success": False}
            
            if amount <= 0:
                print_error("Amount must be greater than 0")
                return {"success": False}
            
            # Check if private key is provided
            if not private_key:
                print_info("\n  Demo mode: Showing transaction details only")
                print("\n  Transaction would be sent with:")
                print(f"    From: {wallet.address}")
                print(f"    To: {to_address}")
                print(f"    Amount: {amount} TRX")
                print("\n  To actually send, provide a private key.")
                return {"success": False}
            
            # Import TRON libraries
            try:
                from tronpy import Tron
                from tronpy.keys import PrivateKey
            except ImportError:
                print_error("TRON libraries not installed. Please install: pip install tronpy")
                return {"success": False}
            
            # Get TRON provider
            from tron.connection import get_connection
            client = get_connection()
            
            print("\n⏳ Building TRON transaction...")
            
            try:
                # Initialize TRON client
                tron = Tron(provider=client.base_url if hasattr(client, 'base_url') else 'https://api.trongrid.io')
                
                # Check balance
                account_info = tron.get_account(wallet.address)
                balance_sun = account_info.get('balance', 0)
                balance_trx = balance_sun / 1_000_000
                
                print(f"  Balance: {balance_trx:.6f} TRX")
                
                if balance_sun <= 0:
                    print_error("Insufficient balance")
                    return {"success": False}
                
                amount_sun = int(amount * 1_000_000)
                if amount_sun > balance_sun:
                    print_error(f"Insufficient funds. Required: {amount_sun} SUN, Available: {balance_sun} SUN")
                    return {"success": False}
                
                # Create private key
                try:
                    if private_key.startswith('0x'):
                        private_key = private_key[2:]
                    
                    priv_key = PrivateKey(bytes.fromhex(private_key))
                    
                except Exception as e:
                    print_error(f"Invalid private key: {e}")
                    return {"success": False}
                
                # Get account address from private key
                from_address = priv_key.public_key.to_base58check_address()
                if from_address != wallet.address:
                    print_warning(f"Private key address ({from_address}) does not match wallet address ({wallet.address})")
                    confirm = input("  Continue anyway? (y/N): ").strip().lower()
                    if confirm != 'y':
                        print_info("Transaction cancelled.")
                        return {"success": False}
                
                # Build transfer transaction
                try:
                    # Get latest block for reference
                    latest_block = client.get_latest_block_number() if hasattr(client, 'get_latest_block_number') else 0
                    print(f"  Latest Block: {latest_block}")
                    
                    # Create transfer transaction
                    tx = tron.transfer(
                        from_address=from_address,
                        to_address=to_address,
                        amount=amount_sun
                    )
                    
                    # Get fee estimate
                    try:
                        fee = tx.estimate_fee()
                        print(f"  Estimated Fee: {fee}")
                    except Exception as e:
                        print_warning(f"  Fee estimation warning: {e}")
                    
                except Exception as e:
                    print_error(f"Transaction building failed: {e}")
                    return {"success": False}
                
            except Exception as e:
                print_error(f"TRON connection failed: {e}")
                return {"success": False}
            
            # Confirm transaction
            print("\n" + "-" * 40)
            print("  Transaction Summary:")
            print(f"    From: {wallet.address[:20]}...")
            print(f"    To: {to_address[:20]}...")
            print(f"    Amount: {amount} TRX ({amount_sun} SUN)")
            print(f"    Network: mainnet")
            print("-" * 40)
            
            confirm = input("\n  Confirm and broadcast transaction? (y/N): ").strip().lower()
            if confirm != 'y':
                print_info("Transaction cancelled.")
                return {"success": False}
            
            # Sign and broadcast
            print("\n⏳ Signing and broadcasting transaction...")
            
            try:
                # Sign the transaction
                signed_tx = tx.sign(priv_key)
                
                # Broadcast
                result = signed_tx.broadcast()
                
                tx_hash = result.get('txid', 'unknown')
                
                print("\n" + "=" * 60)
                print(" ✅ TRON TRANSACTION SENT!")
                print("=" * 60)
                print(f"\n  Transaction Hash: {tx_hash}")
                print(f"  Amount: {amount} TRX")
                print(f"  To: {to_address}")
                print(f"\n  View on Tronscan:")
                print(f"  https://tronscan.org/#/transaction/{tx_hash}")
                print("=" * 60)
                
                return {"success": True, "tx_hash": tx_hash}
                
            except Exception as e:
                print_error(f"Broadcast failed: {e}")
                return {"success": False}
            
        except Exception as e:
            logger.error(f"TRON transaction failed: {e}")
            print_error(f"Transaction failed: {e}")
            return {"success": False}

    # ================================================================
    # TRANSACTION HISTORY
    # ================================================================

    def _save_transaction_history(self, wallet, to_address, amount, tx_hash, status, network):
        """Save transaction to history."""
        try:
            data = {
                "from": wallet.address,
                "to": to_address,
                "amount": amount,
                "wallet_id": wallet.wallet_id,
                "network": network
            }
            self.db.save_transaction(
                tx_hash=tx_hash,
                blockchain=network,
                data=data
            )
            print_info(f"  Transaction saved to history: {tx_hash[:10]}...")
        except Exception as e:
            logger.warning(f"Could not save transaction history: {e}")

    def _view_transaction_history(self):
        """View all transaction history."""
        print("\n" + "=" * 60)
        print(" 🟣 TRANSACTION HISTORY")
        print("=" * 60)

        try:
            transactions = self.db.get_transactions(limit=50)

            if not transactions:
                print_info("\nNo transactions found.")
                input("\nPress Enter to continue...")
                return

            print(f"\n  Found {len(transactions)} transaction(s):")
            print("-" * 60)

            for tx in transactions:
                status_color = "✅" if tx.get('status') else "❌" if tx.get('status') is False else "⏳"
                print(f"\n  {status_color} {tx.get('tx_hash', 'unknown')[:20]}...")
                print(f"     Network: {tx.get('blockchain', 'unknown')}")
                print(f"     Amount: {tx.get('value', 0)}")
                print(f"     Status: {'Success' if tx.get('status') else 'Failed' if tx.get('status') is False else 'Pending'}")
                if tx.get('created_at'):
                    print(f"     Time: {tx['created_at']}")
                print("-" * 40)

        except Exception as e:
            logger.error(f"Failed to load transaction history: {e}")
            print_error(f"Failed to load history: {e}")

        input("\nPress Enter to continue...")

    def _view_wallet_transactions(self, wallet):
        """View transactions for a specific wallet."""
        print("\n" + "=" * 60)
        print(f" 🟣 TRANSACTIONS FOR {wallet.wallet_id}")
        print("=" * 60)

        try:
            transactions = self.db.get_transactions(
                tx_hash=wallet.address,
                blockchain=wallet.network,
                limit=20
            )

            if not transactions:
                print_info("\nNo transactions found for this wallet.")
                return

            print(f"\n  Found {len(transactions)} transaction(s):")
            print("-" * 60)

            for tx in transactions:
                status_color = "✅" if tx.get('status') else "❌" if tx.get('status') is False else "⏳"
                print(f"\n  {status_color} {tx.get('tx_hash', 'unknown')[:20]}...")
                if tx.get('data'):
                    data = tx.get('data', {})
                    if data.get('to'):
                        print(f"     To: {data.get('to')[:20]}...")
                    if data.get('amount'):
                        print(f"     Amount: {data.get('amount')}")
                if tx.get('created_at'):
                    print(f"     Time: {tx['created_at']}")
                print("-" * 40)

        except Exception as e:
            logger.error(f"Failed to load wallet transactions: {e}")
            print_error(f"Failed to load transactions: {e}")

    # ================================================================
    # WALLET CRUD OPERATIONS
    # ================================================================

    def _delete_wallet(self):
        """Delete a wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 DELETE WALLET")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available wallets:")
        for i, wallet_id in enumerate(wallets, 1):
            print(f"  {i}. {wallet_id}")

        try:
            choice = input("\n  Enter wallet number to delete (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(wallets):
                    wallet_id = wallets[idx]
                else:
                    print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return
            else:
                wallet_id = choice

            confirm = input(f"\n  Are you sure you want to delete '{wallet_id}'? (y/N): ").strip().lower()
            if confirm == 'y':
                self.wallet_manager.delete_wallet(wallet_id)
                print_success(f"Wallet '{wallet_id}' deleted successfully!")
            else:
                print_info("Deletion cancelled.")

        except Exception as e:
            logger.error(f"Wallet deletion failed: {e}")
            print_error(f"Failed to delete wallet: {e}")

        input("\nPress Enter to continue...")

    def _lock_wallet(self):
        """Lock a wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 LOCK WALLET")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available wallets:")
        for i, wallet_id in enumerate(wallets, 1):
            try:
                wallet = self.wallet_manager.load_wallet(wallet_id)
                status = "🔒" if wallet.is_locked else "🔓"
                print(f"  {i}. {wallet_id} {status}")
            except:
                print(f"  {i}. {wallet_id}")

        try:
            choice = input("\n  Enter wallet number (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(wallets):
                    wallet_id = wallets[idx]
                else:
                    print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return
            else:
                wallet_id = choice

            wallet = self.wallet_manager.load_wallet(wallet_id)

            if wallet.is_locked:
                print_warning(f"Wallet '{wallet_id}' is already locked.")
            else:
                wallet.lock()
                self.wallet_manager.save_wallet(wallet)
                print_success(f"Wallet '{wallet_id}' locked successfully!")

        except Exception as e:
            logger.error(f"Wallet lock failed: {e}")
            print_error(f"Failed to lock wallet: {e}")

        input("\nPress Enter to continue...")

    def _unlock_wallet(self):
        """Unlock a wallet."""
        print("\n" + "=" * 60)
        print(" 🟣 UNLOCK WALLET")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available wallets:")
        for i, wallet_id in enumerate(wallets, 1):
            try:
                wallet = self.wallet_manager.load_wallet(wallet_id)
                status = "🔒" if wallet.is_locked else "🔓"
                print(f"  {i}. {wallet_id} {status}")
            except:
                print(f"  {i}. {wallet_id}")

        try:
            choice = input("\n  Enter wallet number (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(wallets):
                    wallet_id = wallets[idx]
                else:
                    print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return
            else:
                wallet_id = choice

            wallet = self.wallet_manager.load_wallet(wallet_id)

            if not wallet.is_locked:
                print_warning(f"Wallet '{wallet_id}' is already unlocked.")
            else:
                password = input("  Enter password (press Enter for default): ").strip()
                if not password:
                    password = "default-password"
                wallet.unlock(password=password)

                try:
                    self.wallet_manager.save_wallet(wallet)
                except Exception as e:
                    if "already exists" in str(e).lower():
                        try:
                            self.wallet_manager.delete_wallet(wallet_id)
                            self.wallet_manager.save_wallet(wallet)
                        except Exception:
                            pass

                print_success(f"Wallet '{wallet_id}' unlocked successfully!")

        except Exception as e:
            logger.error(f"Wallet unlock failed: {e}")
            print_error(f"Failed to unlock wallet: {e}")

        input("\nPress Enter to continue...")

    def _wallet_status(self):
        """Show wallet status."""
        print("\n" + "=" * 60)
        print(" 🟣 WALLET STATUS SUMMARY")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print(f"\n  Total Wallets: {len(wallets)}")
        print("-" * 40)

        locked = 0
        unlocked = 0
        by_network = {}

        for wallet_id in wallets:
            try:
                wallet = self.wallet_manager.load_wallet(wallet_id)
                if wallet.is_locked:
                    locked += 1
                    status = "🔒 Locked"
                else:
                    unlocked += 1
                    status = "🔓 Unlocked"

                network = wallet.network
                by_network[network] = by_network.get(network, 0) + 1

                label = wallet.metadata.get("label", "")
                label_str = f" ({label})" if label else ""
                print(f"  {wallet_id}{label_str} - {status}")
            except Exception as e:
                print(f"  {wallet_id} - ⚠️ Error: {e}")

        print("-" * 40)
        print(f"  🔒 Locked:   {locked}")
        print(f"  🔓 Unlocked: {unlocked}")
        print(f"\n  By Network:")
        for network, count in by_network.items():
            print(f"    {network}: {count}")

        input("\nPress Enter to continue...")

    # ================================================================
    # EXPORT, IMPORT, BACKUP, RESTORE
    # ================================================================

    def _export_wallet(self):
        """Export a wallet to JSON file."""
        print("\n" + "=" * 60)
        print(" 🟣 EXPORT WALLET")
        print("=" * 60)

        wallets = self.wallet_manager.list_wallets()

        if not wallets:
            print_info("\nNo wallets found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available wallets:")
        for i, wallet_id in enumerate(wallets, 1):
            print(f"  {i}. {wallet_id}")

        try:
            choice = input("\n  Enter wallet number to export (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(wallets):
                    wallet_id = wallets[idx]
                else:
                    print_error("Invalid selection")
                    input("\nPress Enter to continue...")
                    return
            else:
                wallet_id = choice

            wallet = self.wallet_manager.load_wallet(wallet_id)

            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)

            export_file = export_dir / f"{wallet_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

            with open(export_file, 'w') as f:
                json.dump(wallet.to_dict(), f, indent=4, default=str)

            print_success(f"Wallet exported to: {export_file}")

        except Exception as e:
            logger.error(f"Wallet export failed: {e}")
            print_error(f"Failed to export wallet: {e}")

        input("\nPress Enter to continue...")

    def _import_wallet(self):
        """Import a wallet from JSON file."""
        print("\n" + "=" * 60)
        print(" 🟣 IMPORT WALLET")
        print("=" * 60)

        export_dir = Path("exports")
        if not export_dir.exists():
            print_info("\nNo exports directory found. Create one first.")
            input("\nPress Enter to continue...")
            return

        json_files = list(export_dir.glob("*.json"))
        if not json_files:
            print_info("\nNo export files found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available export files:")
        for i, file in enumerate(json_files, 1):
            print(f"  {i}. {file.name}")

        try:
            choice = input("\n  Enter file number to import: ").strip()
            if not choice.isdigit():
                print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return

            idx = int(choice) - 1
            if 0 <= idx < len(json_files):
                import_file = json_files[idx]
            else:
                print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return

            with open(import_file, 'r') as f:
                data = json.load(f)

            wallet = Wallet.from_dict(data)

            if self.wallet_manager.wallet_exists(wallet.wallet_id):
                overwrite = input(f"\n  Wallet '{wallet.wallet_id}' already exists. Overwrite? (y/N): ").strip().lower()
                if overwrite != 'y':
                    print_info("Import cancelled.")
                    input("\nPress Enter to continue...")
                    return
                self.wallet_manager.delete_wallet(wallet.wallet_id)

            self.wallet_manager.save_wallet(wallet)
            print_success(f"Wallet imported successfully: {wallet.wallet_id}")

        except Exception as e:
            logger.error(f"Wallet import failed: {e}")
            print_error(f"Failed to import wallet: {e}")

        input("\nPress Enter to continue...")

    def _backup_wallets(self):
        """Backup all wallets."""
        print("\n" + "=" * 60)
        print(" 🟣 BACKUP ALL WALLETS")
        print("=" * 60)

        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"wallets_backup_{timestamp}.json"

            wallets_data = {}
            for wallet_id in self.wallet_manager.list_wallets():
                wallet = self.wallet_manager.load_wallet(wallet_id)
                wallets_data[wallet_id] = wallet.to_dict()

            with open(backup_file, 'w') as f:
                json.dump(wallets_data, f, indent=4, default=str)

            print_success(f"All wallets backed up to: {backup_file}")
            print_info(f"  Total wallets: {len(wallets_data)}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print_error(f"Failed to backup wallets: {e}")

        input("\nPress Enter to continue...")

    def _restore_wallets(self):
        """Restore wallets from backup."""
        print("\n" + "=" * 60)
        print(" 🟣 RESTORE WALLETS")
        print("=" * 60)

        backup_dir = Path("backups")
        if not backup_dir.exists():
            print_info("\nNo backups directory found.")
            input("\nPress Enter to continue...")
            return

        backup_files = list(backup_dir.glob("*.json"))
        if not backup_files:
            print_info("\nNo backup files found.")
            input("\nPress Enter to continue...")
            return

        print("\n  Available backups:")
        for i, file in enumerate(backup_files, 1):
            print(f"  {i}. {file.name}")

        try:
            choice = input("\n  Enter backup number to restore: ").strip()
            if not choice.isdigit():
                print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return

            idx = int(choice) - 1
            if 0 <= idx < len(backup_files):
                restore_file = backup_files[idx]
            else:
                print_error("Invalid selection")
                input("\nPress Enter to continue...")
                return

            with open(restore_file, 'r') as f:
                wallets_data = json.load(f)

            print(f"\n  Found {len(wallets_data)} wallets in backup.")

            print("\n  Wallets in backup:")
            wallet_list = []
            for wallet_id in wallets_data.keys():
                exists = self.wallet_manager.wallet_exists(wallet_id)
                status = "⚠️ (already exists)" if exists else "✅ (new)"
                print(f"    • {wallet_id} {status}")
                wallet_list.append((wallet_id, exists))

            confirm = input("\n  Restore all? (y/N): ").strip().lower()

            if confirm == 'y':
                restored = 0
                skipped = 0
                for wallet_id, exists in wallet_list:
                    try:
                        if exists:
                            overwrite = input(f"\n  Wallet '{wallet_id}' already exists. Overwrite? (y/N): ").strip().lower()
                            if overwrite != 'y':
                                print_info(f"  Skipping {wallet_id}")
                                skipped += 1
                                continue
                            try:
                                self.wallet_manager.delete_wallet(wallet_id)
                                print_info(f"  Deleted existing wallet: {wallet_id}")
                            except Exception as e:
                                print_warning(f"  Could not delete existing wallet: {e}")
                                skipped += 1
                                continue

                        wallet = Wallet.from_dict(wallets_data[wallet_id])
                        self.wallet_manager.save_wallet(wallet)
                        restored += 1
                        print_success(f"  Restored: {wallet_id}")

                    except Exception as e:
                        print_warning(f"  Failed to restore {wallet_id}: {e}")
                        skipped += 1

                print_success(f"\n✅ Restored {restored} wallets successfully!")
                if skipped > 0:
                    print_info(f"  Skipped: {skipped}")
            else:
                print_info("Restore cancelled.")

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            print_error(f"Failed to restore wallets: {e}")

        input("\nPress Enter to continue...")

    # ================================================================
    # ETHEREUM MENU
    # ================================================================

    def _handle_ethereum_menu(self):
        """Handle Ethereum menu."""
        while True:
            choice = EthereumMenu.display()

            if choice == "1":
                self._inspect_ethereum_wallet()
            elif choice == "2":
                self._inspect_ethereum_contract()
            elif choice == "3":
                self._inspect_ethereum_token()
            elif choice == "4":
                self._explore_ethereum_block()
            elif choice == "5":
                self._analyze_ethereum_transaction()
            elif choice == "6":
                self._validate_ethereum_node()
            elif choice == "7":
                self._compare_ethereum_nodes()
            elif choice == "8":
                self._ethereum_gas_optimizer()
            elif choice == "9":
                break
            else:
                EthereumMenu.invalid_choice()

    def _inspect_ethereum_wallet(self):
        """Inspect an Ethereum wallet."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter Ethereum wallet address")
            if not address:
                return

            print("\n⏳ Inspecting wallet...")
            report = self.ethereum_controller.wallet_inspector(address)

            save = input("\n  Save this address as a wallet? (y/N): ").strip().lower()
            if save == 'y':
                wallet_id = input("  Enter wallet ID: ").strip()
                if wallet_id:
                    wallet = self.wallet_manager.create_wallet(
                        wallet_id=wallet_id,
                        address=address,
                        network="ethereum"
                    )
                    self.wallet_manager.save_wallet(wallet)
                    print_success(f"Wallet '{wallet_id}' saved!")

            WalletDisplay.display_wallet_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Wallet inspection failed: {error}")

        input("\nPress Enter to continue...")

    def _inspect_ethereum_contract(self):
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

    def _inspect_ethereum_token(self):
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

    def _explore_ethereum_block(self):
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

    def _analyze_ethereum_transaction(self):
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

    def _validate_ethereum_node(self):
        """Validate Ethereum node."""
        try:
            print("\n" + "=" * 60)
            print(" 🟣 ETHEREUM NODE VALIDATION")
            print("=" * 60)
            print("\n  Options:")
            print("  1. Validate Current Node")
            print("  2. Validate Custom Node")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating current node...")
                report = self.ethereum_controller.node_validator()
            elif choice == "2":
                rpc_url = input("\nEnter Ethereum RPC URL: ").strip()
                if not rpc_url:
                    print_error("RPC URL cannot be empty")
                    input("\nPress Enter to continue...")
                    return
                print(f"\n⏳ Validating node: {rpc_url}")
                report = self.ethereum_controller.node_validator(rpc_url)
            else:
                print_error("Invalid choice")
                input("\nPress Enter to continue...")
                return
            
            NodeDisplay.display_node_report(report)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Node validation failed: {error}")
        
        input("\nPress Enter to continue...")

    def _compare_ethereum_nodes(self):
        """Compare Ethereum nodes."""
        try:
            print("\nEnter node URLs (one per line, empty line to finish):")
            urls = []
            while True:
                url = input("  > ").strip()
                if not url:
                    break
                urls.append(url)

            if len(urls) < 2:
                print_warning("Need at least 2 nodes to compare")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Comparing nodes...")
            report = self.ethereum_controller.compare_nodes(urls)
            NodeDisplay.display_node_comparison(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Node comparison failed: {error}")

        input("\nPress Enter to continue...")

    def _ethereum_gas_optimizer(self):
        """Ethereum gas optimization."""
        try:
            print("\n⏳ Fetching gas price...")
            report = self.ethereum_controller.gas_optimizer()
            GasDisplay.display_gas_info(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Gas optimization failed: {error}")

        input("\nPress Enter to continue...")

    # ================================================================
    # BITCOIN MENU
    # ================================================================

    def _handle_bitcoin_menu(self):
        """Handle Bitcoin menu."""
        while True:
            print("\n" + "=" * 60)
            print(" 🟠 BITCOIN MODULE")
            print("=" * 60)
            print("\n  Bitcoin Features:")
            print("  ---------------")
            print("  1. 👛 Inspect Wallet")
            print("  2. 🔍 Explore Block")
            print("  3. 📊 Analyze Transaction")
            print("  4. 🖥️  Validate Node")
            print("  5. 🔄 Compare Nodes")
            print("  6. ⛽ Fee Optimization")
            print("  7. 🔙 Back to Main Menu")
            print("-" * 40)

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                self._inspect_bitcoin_wallet()
            elif choice == "2":
                self._explore_bitcoin_block()
            elif choice == "3":
                self._analyze_bitcoin_transaction()
            elif choice == "4":
                self._validate_bitcoin_node()
            elif choice == "5":
                self._compare_bitcoin_nodes()
            elif choice == "6":
                self._bitcoin_fee_optimizer()
            elif choice == "7":
                break
            else:
                print_error("Invalid choice. Please enter 1-7.")
                input("\nPress Enter to continue...")

    def _inspect_bitcoin_wallet(self):
        """Inspect a Bitcoin wallet."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter Bitcoin wallet address")
            if not address:
                return

            print("\n⏳ Inspecting wallet...")
            report = self.bitcoin_controller.wallet_inspector(address)

            save = input("\n  Save this address as a wallet? (y/N): ").strip().lower()
            if save == 'y':
                wallet_id = input("  Enter wallet ID: ").strip()
                if wallet_id:
                    # Check if wallet already exists
                    if self.wallet_manager.wallet_exists(wallet_id):
                        overwrite = input(f"\n  Wallet '{wallet_id}' already exists. Overwrite? (y/N): ").strip().lower()
                        if overwrite != 'y':
                            print_info("Wallet save cancelled.")
                            input("\nPress Enter to continue...")
                            return
                        self.wallet_manager.delete_wallet(wallet_id)
                        print_info(f"  Deleted existing wallet: {wallet_id}")

                    wallet = self.wallet_manager.create_wallet(
                        wallet_id=wallet_id,
                        address=address,
                        network="bitcoin"
                    )
                    self.wallet_manager.save_wallet(wallet)
                    print_success(f"Wallet '{wallet_id}' saved!")

            WalletDisplay.display_wallet_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Wallet inspection failed: {error}")

        input("\nPress Enter to continue...")

    def _explore_bitcoin_block(self):
        """Explore a Bitcoin block."""
        try:
            from core.input import get_block_input
            block_number = get_block_input("Enter Bitcoin block number")
            if block_number is None:
                return

            print("\n⏳ Fetching block...")
            report = self.bitcoin_controller.block_explorer(block_number)
            BlockDisplay.display_block_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Block exploration failed: {error}")

        input("\nPress Enter to continue...")

    def _analyze_bitcoin_transaction(self):
        """Analyze a Bitcoin transaction."""
        try:
            from core.input import get_transaction_hash
            tx_hash = get_transaction_hash("Enter Bitcoin transaction hash")
            if not tx_hash:
                return

            print("\n⏳ Analyzing transaction...")
            report = self.bitcoin_controller.transaction_analyzer(tx_hash)
            TransactionDisplay.display_transaction_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Transaction analysis failed: {error}")

        input("\nPress Enter to continue...")

    def _validate_bitcoin_node(self):
        """Validate Bitcoin node."""
        try:
            print("\n" + "=" * 60)
            print(" 🟠 BITCOIN NODE VALIDATION")
            print("=" * 60)
            print("\n  Options:")
            print("  1. Validate Default Bitcoin Node")
            print("  2. Validate Custom Bitcoin Node")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating default Bitcoin node...")
                report = self.bitcoin_controller.node_validator()
            elif choice == "2":
                rpc_url = input("\nEnter Bitcoin RPC URL: ").strip()
                if not rpc_url:
                    print_error("RPC URL cannot be empty")
                    input("\nPress Enter to continue...")
                    return
                print(f"\n⏳ Validating Bitcoin node: {rpc_url}")
                report = self.bitcoin_controller.node_validator(rpc_url)
            else:
                print_error("Invalid choice")
                input("\nPress Enter to continue...")
                return
            
            NodeDisplay.display_node_report(report)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Node validation failed: {error}")
        
        input("\nPress Enter to continue...")

    def _compare_bitcoin_nodes(self):
        """Compare Bitcoin nodes."""
        try:
            print("\nEnter node URLs (one per line, empty line to finish):")
            print("  Example: https://mempool.space/api")
            print("  Example: https://blockchain.info")
            print("-" * 40)
            
            urls = []
            while True:
                url = input("  > ").strip()
                if not url:
                    break
                urls.append(url)

            if len(urls) < 2:
                print_warning("Need at least 2 nodes to compare")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Comparing nodes...")
            report = self.bitcoin_controller.compare_nodes(urls)
            NodeDisplay.display_node_comparison(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Node comparison failed: {error}")

        input("\nPress Enter to continue...")

    def _bitcoin_fee_optimizer(self):
        """Bitcoin fee optimization."""
        try:
            from bitcoin.gas import get_fee_optimizer
            print("\n⏳ Fetching fee estimates...")
            optimizer = get_fee_optimizer()
            fees = optimizer.get_fee_estimate()
            
            print("\n" + "=" * 60)
            print(" 🟠 BITCOIN FEE ESTIMATES")
            print("=" * 60)
            print(f"\n  Slow:      {fees.get('slow', 0)} sat/byte")
            print(f"  Standard:  {fees.get('standard', 0)} sat/byte")
            print(f"  Fast:      {fees.get('fast', 0)} sat/byte")
            print(f"  Source:    {fees.get('source', 'unknown')}")
            print("=" * 60)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Fee optimization failed: {error}")

        input("\nPress Enter to continue...")

    # ================================================================
    # TRON MENU
    # ================================================================

    def _handle_tron_menu(self):
        """Handle TRON menu."""
        while True:
            print("\n" + "=" * 60)
            print(" 🔴 TRON MODULE")
            print("=" * 60)
            print("\n  TRON Features:")
            print("  -------------")
            print("  1. 👛 Inspect Wallet")
            print("  2. 📄 Inspect Contract")
            print("  3. 💱 Inspect Token")
            print("  4. 🔍 Explore Block")
            print("  5. 📊 Analyze Transaction")
            print("  6. 🖥️  Validate Node")
            print("  7. 🔄 Compare Nodes")
            print("  8. ⚡ Energy Optimization")
            print("  9. 🔙 Back to Main Menu")
            print("-" * 40)

            choice = input("\nEnter your choice (1-9): ").strip()

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
                self._tron_energy_optimizer()
            elif choice == "9":
                break
            else:
                print_error("Invalid choice. Please enter 1-9.")
                input("\nPress Enter to continue...")

    def _inspect_tron_wallet(self):
        """Inspect a TRON wallet."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter TRON wallet address")
            if not address:
                return

            print("\n⏳ Inspecting wallet...")
            report = self.tron_controller.wallet_inspector(address)

            save = input("\n  Save this address as a wallet? (y/N): ").strip().lower()
            if save == 'y':
                wallet_id = input("  Enter wallet ID: ").strip()
                if wallet_id:
                    wallet = self.wallet_manager.create_wallet(
                        wallet_id=wallet_id,
                        address=address,
                        network="tron"
                    )
                    self.wallet_manager.save_wallet(wallet)
                    print_success(f"Wallet '{wallet_id}' saved!")

            WalletDisplay.display_wallet_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Wallet inspection failed: {error}")

        input("\nPress Enter to continue...")

    def _inspect_tron_contract(self):
        """Inspect a TRON contract."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter TRON contract address")
            if not address:
                return

            print("\n⏳ Inspecting contract...")
            report = self.tron_controller.contract_inspector(address)
            ContractDisplay.display_contract_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Contract inspection failed: {error}")

        input("\nPress Enter to continue...")

    def _inspect_tron_token(self):
        """Inspect a TRON token."""
        try:
            from core.input import get_address_input
            address = get_address_input("Enter TRC-20 token address")
            if not address:
                return

            print("\n⏳ Inspecting token...")
            report = self.tron_controller.token_inspector(address)
            TokenDisplay.display_token_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Token inspection failed: {error}")

        input("\nPress Enter to continue...")

    def _explore_tron_block(self):
        """Explore a TRON block."""
        try:
            from core.input import get_block_input
            block_number = get_block_input("Enter TRON block number")
            if block_number is None:
                return

            print("\n⏳ Fetching block...")
            report = self.tron_controller.block_explorer(block_number)
            BlockDisplay.display_block_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Block exploration failed: {error}")

        input("\nPress Enter to continue...")

    def _analyze_tron_transaction(self):
        """Analyze a TRON transaction."""
        try:
            from core.input import get_transaction_hash
            tx_hash = get_transaction_hash("Enter TRON transaction hash")
            if not tx_hash:
                return

            # Clean the transaction hash
            tx_hash = tx_hash.strip()
            # Remove 0x prefix if present (TRON doesn't use it)
            if tx_hash.startswith('0x'):
                tx_hash = tx_hash[2:]
            # Ensure it's 64 characters
            if len(tx_hash) != 64:
                print_error(f"Invalid TRON transaction hash. Expected 64 characters, got {len(tx_hash)}")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Analyzing transaction...")
            report = self.tron_controller.transaction_analyzer(tx_hash)
            TransactionDisplay.display_transaction_report(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Transaction analysis failed: {error}")

        input("\nPress Enter to continue...")
    def _validate_tron_node(self):
        """Validate TRON node."""
        try:
            print("\n" + "=" * 60)
            print(" 🔴 TRON NODE VALIDATION")
            print("=" * 60)
            print("\n  Options:")
            print("  1. Validate Default TRON Node")
            print("  2. Validate Custom TRON Node")
            print("-" * 40)
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                print("\n⏳ Validating default TRON node...")
                report = self.tron_controller.node_validator()
            elif choice == "2":
                rpc_url = input("\nEnter TRON RPC URL: ").strip()
                if not rpc_url:
                    print_error("RPC URL cannot be empty")
                    input("\nPress Enter to continue...")
                    return
                print(f"\n⏳ Validating TRON node: {rpc_url}")
                report = self.tron_controller.node_validator(rpc_url)
            else:
                print_error("Invalid choice")
                input("\nPress Enter to continue...")
                return
            
            NodeDisplay.display_node_report(report)
            
        except Exception as error:
            print_error(str(error))
            logger.error(f"Node validation failed: {error}")
        
        input("\nPress Enter to continue...")

    def _compare_tron_nodes(self):
        """Compare TRON nodes."""
        try:
            print("\nEnter node URLs (one per line, empty line to finish):")
            print("  Example: https://api.trongrid.io")
            print("  Example: https://api.shasta.trongrid.io")
            print("-" * 40)
            
            urls = []
            while True:
                url = input("  > ").strip()
                if not url:
                    break
                urls.append(url)

            if len(urls) < 2:
                print_warning("Need at least 2 nodes to compare")
                input("\nPress Enter to continue...")
                return

            print("\n⏳ Comparing nodes...")
            report = self.tron_controller.compare_nodes(urls)
            NodeDisplay.display_node_comparison(report)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Node comparison failed: {error}")

        input("\nPress Enter to continue...")

    def _tron_energy_optimizer(self):
        """TRON energy optimization."""
        try:
            from tron.gas import get_energy_optimizer
            print("\n⏳ Fetching energy price...")
            optimizer = get_energy_optimizer()
            energy = optimizer.get_energy_price()
            
            print("\n" + "=" * 60)
            print(" 🔴 TRON ENERGY PRICE")
            print("=" * 60)
            print(f"\n  Energy Price: {energy.get('energy_price', 1)} SUN")
            print(f"  Unit:         {energy.get('unit', 'SUN')}")
            print("=" * 60)

        except Exception as error:
            print_error(str(error))
            logger.error(f"Energy optimization failed: {error}")

        input("\nPress Enter to continue...")

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    def _show_settings(self):
        """Show settings."""
        print("\n" + "=" * 60)
        print(" ⚙️ SETTINGS")
        print("=" * 60)
        print(f"\n  Wallets: {self.wallet_manager.count_wallets()}")
        print(f"  Storage: {self.wallet_storage.storage_path}")
        print("\n  To change settings, edit .env file")
        input("\nPress Enter to continue...")

    def _show_help(self):
        """Show help information."""
        print("\n" + "=" * 60)
        print(" 📖 HELP")
        print("=" * 60)
        print("\n  Universal Blockchain Platform (UBP)")
        print("  Version: 3.0.0")
        print("\n  Features:")
        print("    • Wallet Inspection (Ethereum, Bitcoin, TRON)")
        print("    • Wallet Creation & Management")
        print("    • Wallet Export/Import")
        print("    • Wallet Backup/Restore")
        print("    • Transaction Signing (Ethereum)")
        print("    • Balance Monitoring")
        print("    • Transaction History")
        print("    • Contract Analysis (Ethereum, TRON)")
        print("    • Token Information (ERC-20, TRC-20)")
        print("    • Block Exploration")
        print("    • Transaction Analysis")
        print("    • Node Validation & Comparison")
        print("    • Gas/Energy Optimization")
        print("\n  Supported Blockchains:")
        print("    • Ethereum")
        print("    • Bitcoin")
        print("    • TRON")
        print("\n  Wallet Management:")
        print("    • Create/List/Inspect/Delete wallets")
        print("    • Lock/Unlock wallets")
        print("    • Export/Import/Backup/Restore")
        print("    • Monitor balances")
        print("    • View transaction history")
        input("\nPress Enter to continue...")

    def _exit_app(self):
        """Exit the application."""
        print("\n👋 Thank you for using UBP!")
        print("   Goodbye!")
        self.running = False
        sys.exit(0)


def main():
    """Main entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()