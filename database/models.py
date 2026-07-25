"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
database.models

Purpose
-------
SQLAlchemy database models for UBP.

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
    Text, BigInteger, DECIMAL, Index, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class WalletInspection(Base):
    """
    Wallet inspection record.
    """
    __tablename__ = "wallet_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(42), nullable=False, index=True)
    blockchain = Column(String(20), default="ethereum", index=True)
    balance_eth = Column(DECIMAL(78, 18), nullable=True)
    balance_wei = Column(String(78), nullable=True)
    balance_btc = Column(DECIMAL(30, 8), nullable=True)
    balance_satoshis = Column(BigInteger, nullable=True)
    balance_trx = Column(DECIMAL(30, 6), nullable=True)
    balance_sun = Column(BigInteger, nullable=True)
    nonce = Column(Integer, nullable=True)
    is_contract = Column(Boolean, default=False)
    classification = Column(String(50), nullable=True)
    transaction_count = Column(Integer, nullable=True)
    full_data = Column(JSON, nullable=True)
    chain_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_wallet_address_blockchain', 'address', 'blockchain'),
    )


class ContractInspection(Base):
    """
    Contract inspection record.
    """
    __tablename__ = "contract_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(42), nullable=False, index=True)
    blockchain = Column(String(20), default="ethereum", index=True)
    contract_type = Column(String(50), nullable=True)
    name = Column(String(255), nullable=True)
    symbol = Column(String(50), nullable=True)
    decimals = Column(Integer, nullable=True)
    total_supply = Column(String(78), nullable=True)
    bytecode_size = Column(Integer, nullable=True)
    owner = Column(String(42), nullable=True)
    standard = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False)
    full_data = Column(JSON, nullable=True)
    chain_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TransactionHistory(Base):
    """
    Transaction history record.
    """
    __tablename__ = "transaction_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tx_hash = Column(String(66), nullable=False, index=True)
    blockchain = Column(String(20), default="ethereum", index=True)
    from_address = Column(String(42), nullable=True)
    to_address = Column(String(42), nullable=True)
    value_eth = Column(DECIMAL(78, 18), nullable=True)
    value_btc = Column(DECIMAL(30, 8), nullable=True)
    value_trx = Column(DECIMAL(30, 6), nullable=True)
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Integer, nullable=True)
    block_number = Column(Integer, nullable=True)
    block_hash = Column(String(66), nullable=True)
    status = Column(Boolean, nullable=True)
    confirmations = Column(Integer, default=0)
    fee = Column(String(50), nullable=True)
    full_data = Column(JSON, nullable=True)
    chain_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_tx_hash_blockchain', 'tx_hash', 'blockchain'),
    )


class NodeHealth(Base):
    """
    Node health record.
    """
    __tablename__ = "node_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_url = Column(Text, nullable=True)
    blockchain = Column(String(20), default="ethereum", index=True)
    chain_id = Column(Integer, nullable=True)
    block_number = Column(Integer, nullable=True)
    peer_count = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    health_status = Column(String(50), nullable=True)
    is_connected = Column(Boolean, default=False)
    is_syncing = Column(Boolean, default=False)
    node_type = Column(String(50), nullable=True)
    client_version = Column(String(100), nullable=True)
    full_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_node_blockchain_created', 'blockchain', 'created_at'),
    )


class CacheEntry(Base):
    """
    Cache entry for blockchain data.
    """
    __tablename__ = "cache_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), nullable=False, unique=True, index=True)
    cache_value = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
    )


###############################################################################
# End of File
###############################################################################
