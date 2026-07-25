"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
database.database

Purpose
-------
Database manager for UBP.

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

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from database.models import (
    Base,
    WalletInspection,
    ContractInspection,
    TransactionHistory,
    NodeHealth,
    CacheEntry,
)
from core.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database manager for UBP.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database manager.

        Parameters
        ----------
        database_url : str, optional
            Database URL. Defaults to environment variable or SQLite.
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "sqlite:///ubp.db"
        )

        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Initialize tables
        self._init_db()

        logger.info(f"Database initialized at {self.database_url}")

    def _init_db(self) -> None:
        """Create all tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created/verified")
        except Exception as error:
            logger.error(f"Error initializing database: {error}")

    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session.

        Yields
        ------
        Session
            SQLAlchemy session.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ============ Wallet Inspections ============

    def save_wallet_inspection(
        self,
        address: str,
        blockchain: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save a wallet inspection to the database.

        Parameters
        ----------
        address : str
            Wallet address.
        blockchain : str
            Blockchain name.
        data : dict
            Wallet data.

        Returns
        -------
        Optional[str]
            Record ID or None.
        """
        try:
            with self.get_session() as session:
                inspection = WalletInspection(
                    address=address,
                    blockchain=blockchain,
                    balance_eth=data.get("balance_eth"),
                    balance_wei=str(data.get("balance_wei")) if data.get("balance_wei") else None,
                    balance_btc=data.get("balance_btc"),
                    balance_satoshis=data.get("balance_satoshis"),
                    balance_trx=data.get("balance_trx"),
                    balance_sun=data.get("balance_sun"),
                    nonce=data.get("nonce"),
                    is_contract=data.get("is_contract", False),
                    classification=data.get("classification"),
                    transaction_count=data.get("transaction_count"),
                    full_data=data,
                    chain_id=data.get("chain_id", 1),
                )
                session.add(inspection)
                session.flush()
                logger.info(f"Saved wallet inspection for {address} on {blockchain}")
                return str(inspection.id)
        except Exception as error:
            logger.error(f"Error saving wallet inspection: {error}")
            return None

    def get_wallet_inspections(
        self,
        address: str,
        blockchain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get wallet inspections for an address.

        Parameters
        ----------
        address : str
            Wallet address.
        blockchain : str, optional
            Blockchain name.
        limit : int
            Maximum number of records.

        Returns
        -------
        List[Dict[str, Any]]
            List of inspection records.
        """
        try:
            with self.get_session() as session:
                query = session.query(WalletInspection).filter(
                    WalletInspection.address == address
                )

                if blockchain:
                    query = query.filter(WalletInspection.blockchain == blockchain)

                results = query.order_by(
                    desc(WalletInspection.created_at)
                ).limit(limit).all()

                return [
                    {
                        "id": str(r.id),
                        "address": r.address,
                        "blockchain": r.blockchain,
                        "balance": {
                            "eth": float(r.balance_eth) if r.balance_eth else None,
                            "btc": float(r.balance_btc) if r.balance_btc else None,
                            "trx": float(r.balance_trx) if r.balance_trx else None,
                        },
                        "classification": r.classification,
                        "is_contract": r.is_contract,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                        "data": r.full_data,
                    }
                    for r in results
                ]
        except Exception as error:
            logger.error(f"Error getting wallet inspections: {error}")
            return []

    # ============ Contract Inspections ============

    def save_contract_inspection(
        self,
        address: str,
        blockchain: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save a contract inspection to the database.

        Parameters
        ----------
        address : str
            Contract address.
        blockchain : str
            Blockchain name.
        data : dict
            Contract data.

        Returns
        -------
        Optional[str]
            Record ID or None.
        """
        try:
            with self.get_session() as session:
                inspection = ContractInspection(
                    address=address,
                    blockchain=blockchain,
                    contract_type=data.get("contract_type"),
                    name=data.get("name"),
                    symbol=data.get("symbol"),
                    decimals=data.get("decimals"),
                    total_supply=str(data.get("total_supply")) if data.get("total_supply") else None,
                    bytecode_size=data.get("bytecode_size"),
                    owner=data.get("owner"),
                    standard=data.get("standard"),
                    is_verified=data.get("is_verified", False),
                    full_data=data,
                    chain_id=data.get("chain_id", 1),
                )
                session.add(inspection)
                session.flush()
                logger.info(f"Saved contract inspection for {address} on {blockchain}")
                return str(inspection.id)
        except Exception as error:
            logger.error(f"Error saving contract inspection: {error}")
            return None

    # ============ Transaction History ============

    def save_transaction(
        self,
        tx_hash: str,
        blockchain: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save a transaction to the database.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.
        blockchain : str
            Blockchain name.
        data : dict
            Transaction data.

        Returns
        -------
        Optional[str]
            Record ID or None.
        """
        try:
            with self.get_session() as session:
                transaction = TransactionHistory(
                    tx_hash=tx_hash,
                    blockchain=blockchain,
                    from_address=data.get("from"),
                    to_address=data.get("to"),
                    value_eth=data.get("value"),
                    value_btc=data.get("value_btc"),
                    value_trx=data.get("value_trx"),
                    gas_used=data.get("gas_used"),
                    gas_price=data.get("gas_price"),
                    block_number=data.get("block_number"),
                    block_hash=data.get("block_hash"),
                    status=data.get("is_success"),
                    confirmations=data.get("confirmations", 0),
                    fee=str(data.get("fee")) if data.get("fee") else None,
                    full_data=data,
                    chain_id=data.get("chain_id", 1),
                )
                session.add(transaction)
                session.flush()
                logger.info(f"Saved transaction {tx_hash} on {blockchain}")
                return str(transaction.id)
        except Exception as error:
            logger.error(f"Error saving transaction: {error}")
            return None

    def get_transactions(
        self,
        tx_hash: Optional[str] = None,
        blockchain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get transactions from the database.

        Parameters
        ----------
        tx_hash : str, optional
            Transaction hash.
        blockchain : str, optional
            Blockchain name.
        limit : int
            Maximum number of records.

        Returns
        -------
        List[Dict[str, Any]]
            List of transaction records.
        """
        try:
            with self.get_session() as session:
                query = session.query(TransactionHistory)

                if tx_hash:
                    query = query.filter(TransactionHistory.tx_hash == tx_hash)

                if blockchain:
                    query = query.filter(TransactionHistory.blockchain == blockchain)

                results = query.order_by(
                    desc(TransactionHistory.created_at)
                ).limit(limit).all()

                return [
                    {
                        "id": str(r.id),
                        "tx_hash": r.tx_hash,
                        "blockchain": r.blockchain,
                        "from": r.from_address,
                        "to": r.to_address,
                        "value": float(r.value_eth) if r.value_eth else None,
                        "status": r.status,
                        "confirmations": r.confirmations,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                        "data": r.full_data,
                    }
                    for r in results
                ]
        except Exception as error:
            logger.error(f"Error getting transactions: {error}")
            return []

    # ============ Node Health ============

    def save_node_health(self, blockchain: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Save a node health check.

        Parameters
        ----------
        blockchain : str
            Blockchain name.
        data : dict
            Node health data.

        Returns
        -------
        Optional[str]
            Record ID or None.
        """
        try:
            with self.get_session() as session:
                health = NodeHealth(
                    blockchain=blockchain,
                    node_url=data.get("node_url"),
                    chain_id=data.get("chain_id"),
                    block_number=data.get("block_number"),
                    peer_count=data.get("peer_count"),
                    response_time_ms=data.get("response_time_ms"),
                    health_status=data.get("health_status"),
                    is_connected=data.get("is_connected", False),
                    is_syncing=data.get("is_syncing", False),
                    node_type=data.get("node_type"),
                    client_version=data.get("client_version"),
                    full_data=data,
                )
                session.add(health)
                session.flush()
                logger.info(f"Saved node health for {blockchain}")
                return str(health.id)
        except Exception as error:
            logger.error(f"Error saving node health: {error}")
            return None

    # ============ Cache ============

    def cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from cache.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        Optional[Dict[str, Any]]
            Cached value or None.
        """
        try:
            with self.get_session() as session:
                entry = session.query(CacheEntry).filter(
                    CacheEntry.cache_key == key
                ).first()

                if not entry:
                    return None

                if entry.expires_at and entry.expires_at < datetime.utcnow():
                    session.delete(entry)
                    return None

                return entry.cache_value
        except Exception as error:
            logger.error(f"Error getting cache: {error}")
            return None

    def cache_set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl_seconds: int = 300
    ) -> bool:
        """
        Set a value in cache.

        Parameters
        ----------
        key : str
            Cache key.
        value : dict
            Value to cache.
        ttl_seconds : int
            Time to live in seconds.

        Returns
        -------
        bool
            True if successful.
        """
        try:
            with self.get_session() as session:
                # Remove existing entry
                session.query(CacheEntry).filter(
                    CacheEntry.cache_key == key
                ).delete()

                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

                entry = CacheEntry(
                    cache_key=key,
                    cache_value=value,
                    expires_at=expires_at
                )
                session.add(entry)
                logger.info(f"Cached key: {key}")
                return True
        except Exception as error:
            logger.error(f"Error setting cache: {error}")
            return False


# Singleton instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """
    Get the database manager instance.

    Returns
    -------
    DatabaseManager
        Database manager instance.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


###############################################################################
# End of File
###############################################################################
