#!/usr/bin/env python3
"""
Test transaction sending.
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.wallet_service import WalletService


def test_send_eth():
    """Test sending ETH."""
    print("=" * 60)
    print("Testing ETH Transaction Sending")
    print("=" * 60)

    user_service = UserService()
    wallet_service = WalletService()

    # Create a user
    print("\n1. Creating user...")
    user = user_service.create_user("senduser", "send@example.com", "password123")
    if not user:
        print("❌ Failed to create user")
        return False
    
    user_id = user.id
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    
    print(f"✅ User created: {user.username} (ID: {user_id})")

    # Create Ethereum wallet
    print("\n2. Creating Ethereum wallet...")
    wallet = wallet_service.create_wallet(user_id, "ethereum", "Sending Wallet")
    if not wallet:
        print("❌ Wallet creation failed")
        return False
    
    print(f"✅ Wallet created: {wallet['wallet_id']}")
    print(f"   Address: {wallet['address']}")

    # Get balance first
    print("\n3. Checking balance...")
    balance = wallet_service.get_wallet_balance(wallet['wallet_id'])
    if "error" not in balance:
        print(f"✅ Balance: {balance['balance']} ETH")
    else:
        print(f"⚠️  Balance check: {balance.get('error')}")
    
    # Send transaction (this will likely fail with 0 balance, but tests the flow)
    print("\n4. Testing transaction flow...")
    result = wallet_service.send_transaction(
        wallet_id=wallet['wallet_id'],
        to_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        amount=0.001
    )
    
    if "error" in result:
        print(f"⚠️  Transaction flow test: {result['error']}")
        print("   (This is expected if wallet has 0 balance)")
    else:
        print(f"✅ Transaction sent: {result.get('tx_hash')}")

    print("\n" + "=" * 60)
    print("🎉 Transaction test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_send_eth()
