#!/usr/bin/env python3
"""
Universal Blockchain Platform (UBP)
Module: test_wallet_creation.py
Purpose: Test wallet creation, storage, and multi-wallet support
Author: UBP Engineering Team
Version: 2.0.0
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallets.manager import WalletManager
from wallets.storage import WalletStorage
from wallets.encryption import EncryptionManager
from wallets.wallet import Wallet
from core.logger import get_logger

logger = get_logger(__name__)

class WalletCreationTester:
    """
    Test suite for wallet creation and multi-wallet functionality.
    """
    
    def __init__(self):
        """Initialize the tester with all required components."""
        self.storage = WalletStorage("data/wallets")
        self.encryption = EncryptionManager()
        self.manager = WalletManager(
            storage=self.storage,
            encryption=self.encryption
        )
        self.test_results = []
    
    def run_all_tests(self):
        """Run all wallet creation tests."""
        print("\n" + "=" * 70)
        print(" 🟣 UBP WALLET SYSTEM TEST SUITE")
        print("=" * 70)
        
        self.test_wallet_creation()
        self.test_multi_wallet_support()
        self.test_wallet_persistence()
        self.test_wallet_encryption()
        self.test_wallet_metadata()
        
        self.print_summary()
    
    def test_wallet_creation(self):
        """Test creating a single wallet."""
        print("\n📋 TEST 1: Wallet Creation")
        print("-" * 50)
        
        try:
            wallet = self.manager.create_wallet(
                wallet_id="test-wallet-001",
                address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                network="ethereum",
                wallet_type="software",
                metadata={
                    "created_at": datetime.utcnow().isoformat(),
                    "purpose": "testing",
                    "owner": "UBP Developer"
                }
            )
            
            self.manager.save_wallet(wallet)
            
            print(f"   ✅ Wallet created: {wallet.wallet_id}")
            print(f"   📍 Address: {wallet.address}")
            print(f"   🌐 Network: {wallet.network}")
            print(f"   🔒 Locked: {wallet.is_locked}")
            print(f"   📝 Metadata: {wallet.metadata}")
            
            self.test_results.append(("Wallet Creation", True))
            return wallet
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results.append(("Wallet Creation", False))
            return None
    
    def test_multi_wallet_support(self):
        """Test creating and managing multiple wallets."""
        print("\n📋 TEST 2: Multi-Wallet Support")
        print("-" * 50)
        
        test_wallets = [
            {
                "id": "eth-wallet-001",
                "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "network": "ethereum"
            },
            {
                "id": "eth-wallet-002",
                "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "network": "ethereum"
            },
            {
                "id": "btc-wallet-001",
                "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "network": "bitcoin"
            }
        ]
        
        try:
            created = []
            for wallet_data in test_wallets:
                wallet = self.manager.create_wallet(
                    wallet_id=wallet_data["id"],
                    address=wallet_data["address"],
                    network=wallet_data["network"],
                    wallet_type="software"
                )
                self.manager.save_wallet(wallet)
                created.append(wallet.wallet_id)
                print(f"   ✅ Created: {wallet.wallet_id} ({wallet.network})")
            
            # List all wallets
            all_wallets = self.manager.list_wallets()
            print(f"\n   📂 All wallets: {all_wallets}")
            print(f"   📊 Total wallets: {self.manager.count_wallets()}")
            
            self.test_results.append(("Multi-Wallet Support", True))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results.append(("Multi-Wallet Support", False))
    
    def test_wallet_persistence(self):
        """Test saving and loading wallets."""
        print("\n📋 TEST 3: Wallet Persistence")
        print("-" * 50)
        
        try:
            # Create a wallet
            wallet = self.manager.create_wallet(
                wallet_id="persistence-test",
                address="0x6B175474E89094C44Da98b954EedeAC495271d0F",
                network="ethereum"
            )
            self.manager.save_wallet(wallet)
            print(f"   ✅ Wallet saved: {wallet.wallet_id}")
            
            # Load it back
            loaded = self.manager.load_wallet("persistence-test")
            print(f"   ✅ Wallet loaded: {loaded.wallet_id}")
            print(f"   📍 Address: {loaded.address}")
            print(f"   🌐 Network: {loaded.network}")
            
            # Verify they match
            assert wallet.wallet_id == loaded.wallet_id
            assert wallet.address == loaded.address
            assert wallet.network == loaded.network
            
            print(f"   ✅ Persistence verified")
            self.test_results.append(("Wallet Persistence", True))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results.append(("Wallet Persistence", False))
    
    def test_wallet_encryption(self):
        """Test wallet encryption and decryption."""
        print("\n📋 TEST 4: Wallet Encryption")
        print("-" * 50)
        
        try:
            # Create a wallet with private key simulation
            from wallets.keys import WalletKey
            
            # Create a key
            key = WalletKey(
                algorithm="secp256k1",
                network="ethereum",
                public_key="0xPublicKey123",
                private_key=b"\x01" * 32  # Simulated private key
            )
            
            # Encrypt the key
            encrypted = key.to_encrypted_dict(
                self.encryption,
                "test-password-123"
            )
            print(f"   ✅ Key encrypted")
            print(f"   🔐 Version: {encrypted.get('version')}")
            print(f"   🔑 Algorithm: {encrypted.get('algorithm')}")
            
            # Decrypt and restore
            restored = WalletKey.from_encrypted_dict(
                encrypted,
                self.encryption,
                "test-password-123"
            )
            print(f"   ✅ Key decrypted and restored")
            print(f"   🔑 Algorithm: {restored.algorithm}")
            print(f"   🌐 Network: {restored.network}")
            
            self.test_results.append(("Wallet Encryption", True))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results.append(("Wallet Encryption", False))
    
    def test_wallet_metadata(self):
        """Test wallet metadata management."""
        print("\n📋 TEST 5: Wallet Metadata")
        print("-" * 50)
        
        try:
            wallet = self.manager.create_wallet(
                wallet_id="metadata-test",
                address="0x0000000000000000000000000000000000000000",
                network="ethereum",
                metadata={
                    "app": "UBP",
                    "version": "2.0.0",
                    "created": datetime.utcnow().isoformat()
                }
            )
            
            # Update metadata
            wallet.update_metadata("purpose", "testing metadata")
            wallet.update_metadata("tags", ["test", "development"])
            
            print(f"   ✅ Metadata updated")
            print(f"   📝 Purpose: {wallet.get_metadata('purpose')}")
            print(f"   🏷️ Tags: {wallet.get_metadata('tags')}")
            print(f"   📋 All metadata: {wallet.metadata}")
            
            self.manager.save_wallet(wallet)
            
            # Load and verify
            loaded = self.manager.load_wallet("metadata-test")
            print(f"   ✅ Metadata persisted")
            print(f"   📝 Purpose: {loaded.get_metadata('purpose')}")
            
            self.test_results.append(("Wallet Metadata", True))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.test_results.append(("Wallet Metadata", False))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print(" 📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {test_name}")
        
        print("\n" + "-" * 50)
        print(f"   Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n 🎉 ALL TESTS PASSED! Wallet system is operational.")
        else:
            print("\n ⚠️ Some tests failed. Please review the output above.")
        
        print("=" * 70)


def main():
    """Main entry point."""
    tester = WalletCreationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
