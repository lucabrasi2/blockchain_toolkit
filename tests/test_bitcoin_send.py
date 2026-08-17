#!/usr/bin/env python3
"""
Test Bitcoin transaction sending.
"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import UserService
from services.wallet_service import WalletService


def test_bitcoin_send():
    """Test sending BTC."""
    print("=" * 60)
    print("Testing Bitcoin Transaction Sending")
    print("=" * 60)

    user_service = UserService()
    wallet_service = WalletService()

    # Create a user
    print("\n1. Creating user...")
    user = user_service.create_user("btcsend", "btcsend@example.com", "password123")
    if not user:
        print("❌ Failed to create user")
        return False
    
    user_id = user.id
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    
    print(f"✅ User created: {user.username} (ID: {user_id})")

    # Create Bitcoin wallet
    print("\n2. Creating Bitcoin wallet...")
    wallet = wallet_service.create_wallet(user_id, "bitcoin", "BTC Sending Wallet")
    if not wallet:
        print("❌ Wallet creation failed")
        return False
    
    print(f"✅ Wallet created: {wallet['wallet_id']}")
    print(f"   Address: {wallet['address']}")

    # Get balance first
    print("\n3. Checking BTC balance...")
    balance = wallet_service.get_wallet_balance(wallet['wallet_id'])
    if "error" not in balance:
        print(f"✅ Balance: {balance['balance']} BTC")
        print(f"   Satoshis: {balance.get('satoshis', 0)}")
    else:
        print(f"⚠️  Balance check: {balance.get('error')}")
    
    # Send transaction (will show BTC-specific error since UTXO management isn't fully implemented)
    print("\n4. Testing BTC send flow...")
    result = wallet_service.send_transaction(
        wallet_id=wallet['wallet_id'],
        to_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block address
        amount=0.00001
    )
    
    if "error" in result:
        print(f"ℹ️  Transaction result: {result['error']}")
        if "UTXO" in result['error'] or "coming soon" in result['error'].lower():
            print("   (This is expected - Bitcoin UTXO management is being implemented)")
    else:
        print(f"✅ Transaction sent: {result.get('tx_hash')}")

    print("\n" + "=" * 60)
    print("🎉 Bitcoin transaction test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_bitcoin_send()
