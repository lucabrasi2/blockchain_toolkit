#!/usr/bin/env python3
"""
Test TRON wallet creation.
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.wallet_service import WalletService


def test_tron_wallet():
    """Test TRON wallet creation."""
    print("=" * 60)
    print("Testing TRON Wallet Creation")
    print("=" * 60)

    user_service = UserService()
    wallet_service = WalletService()

    print("\n1. Creating user...")
    user = user_service.create_user("tronuser", "tron@example.com", "password123")
    if not user:
        print("❌ Failed to create user")
        return False
    
    user_id = user.id
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    
    print(f"✅ User created: {user.username} (ID: {user_id})")

    print("\n2. Creating TRON wallet...")
    wallet = wallet_service.create_wallet(user_id, "tron", "My TRX Wallet")
    if wallet:
        print(f"✅ Wallet created: {wallet['wallet_id']}")
        print(f"   Address: {wallet['address']}")
        print(f"   Blockchain: {wallet['blockchain']}")
        print(f"   Label: {wallet['label']}")
    else:
        print("❌ Wallet creation failed")
        return False

    print("\n3. Getting user wallets...")
    wallets = wallet_service.get_user_wallets(user_id)
    print(f"✅ Found {len(wallets)} wallet(s)")
    for w in wallets:
        print(f"   - {w['blockchain']}: {w['address'][:15]}...")

    print("\n4. Getting wallet balance...")
    balance = wallet_service.get_wallet_balance(wallet['wallet_id'])
    if "error" not in balance:
        print(f"✅ Balance: {balance['balance']} {balance['symbol']}")
    else:
        print(f"⚠️  Balance check: {balance.get('error')}")

    print("\n" + "=" * 60)
    print("🎉 TRON wallet test passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_tron_wallet()
