#!/usr/bin/env python3
"""
Test TRON transaction sending.
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.wallet_service import WalletService


def test_tron_send():
    """Test sending TRX."""
    print("=" * 60)
    print("Testing TRON Transaction Sending")
    print("=" * 60)

    user_service = UserService()
    wallet_service = WalletService()

    # Create a user
    print("\n1. Creating user...")
    user = user_service.create_user("tronsend", "tronsend@example.com", "password123")
    if not user:
        print("❌ Failed to create user")
        return False
    
    user_id = user.id
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    
    print(f"✅ User created: {user.username} (ID: {user_id})")

    # Create TRON wallet
    print("\n2. Creating TRON wallet...")
    wallet = wallet_service.create_wallet(user_id, "tron", "TRX Sending Wallet")
    if not wallet:
        print("❌ Wallet creation failed")
        return False
    
    print(f"✅ Wallet created: {wallet['wallet_id']}")
    print(f"   Address: {wallet['address']}")

    # Get balance first
    print("\n3. Checking TRX balance...")
    balance = wallet_service.get_wallet_balance(wallet['wallet_id'])
    if "error" not in balance:
        print(f"✅ Balance: {balance['balance']} TRX")
    else:
        print(f"⚠️  Balance check: {balance.get('error')}")
    
    # Send transaction (will show TRX-specific error since amount is 0)
    print("\n4. Testing TRX send flow...")
    result = wallet_service.send_transaction(
        wallet_id=wallet['wallet_id'],
        to_address="TQ9h9QW4Y9Q4mJ72h3X8x9Q7v",
        amount=0.001
    )
    
    if "error" in result:
        print(f"ℹ️  Transaction result: {result['error']}")
        if "insufficient" in result['error'].lower() or "balance" in result['error'].lower():
            print("   (This is expected - wallet has 0 TRX balance)")
    else:
        print(f"✅ Transaction sent: {result.get('tx_hash')}")

    print("\n" + "=" * 60)
    print("🎉 TRON transaction test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_tron_send()
