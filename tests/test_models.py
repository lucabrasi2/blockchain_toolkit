#!/usr/bin/env python3
"""
Test the database models.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, User, Wallet, UserTransaction


def test_user_model():
    """Test User model creation."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    print("✅ User model test passed")


def test_wallet_model():
    """Test Wallet model creation."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = User(
        username="testuser2",
        email="test2@example.com",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    
    wallet = Wallet(
        user_id=user.id,
        wallet_id="eth_test_123",
        blockchain="ethereum",
        address="0x1234567890123456789012345678901234567890",
        label="Test ETH Wallet"
    )
    session.add(wallet)
    session.commit()
    
    assert wallet.id is not None
    assert wallet.user_id == user.id
    assert wallet.blockchain == "ethereum"
    print("✅ Wallet model test passed")


def test_transaction_model():
    """Test UserTransaction model creation."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = User(
        username="testuser3",
        email="test3@example.com",
        password_hash="hashed_password"
    )
    session.add(user)
    session.commit()
    
    wallet = Wallet(
        user_id=user.id,
        wallet_id="btc_test_123",
        blockchain="bitcoin",
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        label="Test BTC Wallet"
    )
    session.add(wallet)
    session.commit()
    
    tx = UserTransaction(
        wallet_id=wallet.id,
        user_id=user.id,
        tx_hash="0x1234567890123456789012345678901234567890123456789012345678901234",
        blockchain="bitcoin",
        from_address=wallet.address,
        to_address="1CounterpartyXyz",
        amount=0.5,
        asset="BTC",
        status="pending"
    )
    session.add(tx)
    session.commit()
    
    assert tx.id is not None
    assert tx.wallet_id == wallet.id
    assert tx.status == "pending"
    print("✅ Transaction model test passed")


if __name__ == "__main__":
    test_user_model()
    test_wallet_model()
    test_transaction_model()
    print("\n🎉 All model tests passed!")
