"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.metadata

Purpose
-------
Bitcoin transaction metadata retrieval.

This module provides metadata retrieval for Bitcoin transactions.

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

from typing import Dict, Any, Optional

from bitcoin.connection import get_connection
from bitcoin.transactions import get_transaction
from bitcoin.wallets import is_valid_address
from core.logger import get_logger

logger = get_logger(__name__)


class BitcoinTransactionMetadata:
    """
    Bitcoin transaction metadata container.
    """

    def __init__(self, tx_hash: str):
        self.tx_hash = tx_hash
        self.block_hash = None
        self.block_height = None
        self.confirmations = 0
        self.timestamp = None
        self.size = 0
        self.weight = 0
        self.version = 0
        self.locktime = 0
        self.fee = 0
        self.inputs = []
        self.outputs = []
        self._fetch_metadata()

    def _fetch_metadata(self):
        """Fetch transaction metadata from the blockchain."""
        try:
            tx = get_transaction(self.tx_hash)

            if "error" not in tx:
                self.block_hash = tx.get("block_hash")
                self.block_height = tx.get("block_height")
                self.confirmations = tx.get("confirmations", 0)
                self.timestamp = tx.get("timestamp")
                self.size = tx.get("size", 0)
                self.weight = tx.get("weight", 0)
                self.version = tx.get("version", 0)
                self.locktime = tx.get("locktime", 0)
                self.fee = tx.get("fee", 0)
                self.inputs = tx.get("inputs", [])
                self.outputs = tx.get("outputs", [])

                logger.info(f"Fetched metadata for transaction {self.tx_hash[:10]}...")
            else:
                logger.error(f"Error fetching transaction: {tx.get('error')}")

        except Exception as error:
            logger.error(f"Error fetching metadata: {error}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "tx_hash": self.tx_hash,
            "block_hash": self.block_hash,
            "block_height": self.block_height,
            "confirmations": self.confirmations,
            "timestamp": self.timestamp,
            "size": self.size,
            "weight": self.weight,
            "version": self.version,
            "locktime": self.locktime,
            "fee": self.fee,
            "inputs_count": len(self.inputs),
            "outputs_count": len(self.outputs),
        }


def get_transaction_metadata(tx_hash: str) -> BitcoinTransactionMetadata:
    """
    Get transaction metadata.

    Parameters
    ----------
    tx_hash : str
        Bitcoin transaction hash.

    Returns
    -------
    BitcoinTransactionMetadata
        Transaction metadata instance.
    """
    logger.info(f"Getting metadata for transaction {tx_hash[:10]}...")
    return BitcoinTransactionMetadata(tx_hash)


###############################################################################
# End of File
###############################################################################
