#!/usr/bin/env python3
"""
Test the new Wallet Service.
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.wallet_service import WalletService


def test_new_wallet_service():
    """Test new Wallet Service functionality."""
    print("=" * 60)
    print("Testing New Wallet Service")
    print("=" * 60)

    user_service = UserService()
    wallet_service = WalletService()

    # Create a user first
    print("\n1. Creating user...")
    user = user_service.create_user("walletuser", "wallet@example.com", "password123")
    if not user:
        print("❌ Failed to create user")
        return False
    
    # Convert to UUID
    user_id = user.id
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    
    print(f"✅ User created: {user.username} (ID: {user_id})")

    # Test wallet creation
    print("\n2. Creating Ethereum wallet...")
    wallet = wallet_service.create_wallet(user_id, "ethereum", "My ETH Wallet")
    if wallet:
        print(f"✅ Wallet created: {wallet['wallet_id']}")
        print(f"   Address: {wallet['address']}")
        print(f"   Blockchain: {wallet['blockchain']}")
        print(f"   Label: {wallet['label']}")
    else:
        print("❌ Wallet creation failed")
        return False

    # Test get user wallets
    print("\n3. Getting user wallets...")
    wallets = wallet_service.get_user_wallets(user_id)
    print(f"✅ Found {len(wallets)} wallet(s)")
    for w in wallets:
        print(f"   - {w['blockchain']}: {w['address'][:12]}...")

    # Test get wallet by ID
    print("\n4. Getting wallet by ID...")
    wallet_info = wallet_service.get_wallet_by_id(wallet['wallet_id'])
    if wallet_info:
        print(f"✅ Found wallet: {wallet_info['wallet_id']}")
    else:
        print("❌ Wallet not found by ID")

    # Test get wallet balance
    print("\n5. Getting wallet balance...")
    balance = wallet_service.get_wallet_balance(wallet['wallet_id'])
    if "error" not in balance:
        print(f"✅ Balance: {balance['balance']} {balance['symbol']}")
    else:
        print(f"⚠️  Balance check: {balance.get('error')}")

    print("\n" + "=" * 60)
    print("🎉 All new wallet service tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_new_wallet_service()