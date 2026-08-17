"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
database.models_extended

Purpose
-------
Extended SQLAlchemy database models for UBP (User & Wallet Management).

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, BigInteger, DECIMAL, Index, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

# Reuse the same Base from existing models
from database.models import Base


class User(Base):
    """
    User account model.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User preferences
    default_network = Column(String(20), default="ethereum")
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(20), default="user")  # user, admin, viewer, api
    
    # API Key (for API access)
    api_key = Column(String(255), unique=True, nullable=True)
    
    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    user_transactions = relationship("UserTransaction", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_username_email', 'username', 'email'),
    )


class Wallet(Base):
    """
    User-owned wallet model (non-custodial).
    """
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Wallet identification
    wallet_id = Column(String(100), unique=True, nullable=False, index=True)
    blockchain = Column(String(20), nullable=False, index=True)  # ethereum, bitcoin, tron
    network = Column(String(20), default="mainnet")
    
    # Addresses
    address = Column(String(255), nullable=False, index=True)
    public_key = Column(Text, nullable=True)
    
    # Wallet metadata
    wallet_type = Column(String(20), default="hd")  # hd, imported, watch-only
    custody_type = Column(String(20), default="non_custodial")
    
    # Encrypted seed/mnemonic (stored encrypted)
    encrypted_seed = Column(Text, nullable=True)
    encrypted_private_key = Column(Text, nullable=True)
    
    # Wallet status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    label = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("UserTransaction", back_populates="wallet", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_wallet_user_blockchain', 'user_id', 'blockchain'),
        Index('idx_wallet_address_blockchain', 'address', 'blockchain'),
    )


class UserTransaction(Base):
    """
    User-initiated transaction record.
    """
    __tablename__ = "user_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    tx_hash = Column(String(255), unique=True, nullable=False, index=True)
    blockchain = Column(String(20), nullable=False, index=True)
    
    # Sender and receiver
    from_address = Column(String(255), nullable=False)
    to_address = Column(String(255), nullable=False)
    
    # Amount and asset
    amount = Column(DECIMAL(78, 18), nullable=False)
    asset = Column(String(20), nullable=False)
    
    # Transaction metadata
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    
    # Fee
    fee = Column(DECIMAL(78, 18), nullable=True)
    fee_asset = Column(String(20), nullable=True)
    
    # Raw transaction data
    raw_transaction = Column(Text, nullable=True)
    signed_transaction = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime, nullable=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    user = relationship("User", back_populates="user_transactions")

    __table_args__ = (
        Index('idx_user_tx_user_blockchain', 'user_id', 'blockchain'),
        Index('idx_user_tx_hash_status', 'tx_hash', 'status'),
    )


# ============ Migration Helper ============

def create_tables(engine):
    """
    Create all tables if they don't exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
    logger.info("Database tables created/verified")


###############################################################################
# End of File
###############################################################################
