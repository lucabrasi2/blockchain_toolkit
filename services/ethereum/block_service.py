"""
Universal Blockchain Platform (UBP)

Module:
    Block Service

Purpose:
    Business logic for Ethereum block operations.

Responsibilities:
    • Get block by number or hash
    • Get latest block
    • Format block data for display
    • Analyze block metrics

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from ethereum.blocks import get_block, get_latest_block, get_block_transactions
from ethereum.connection import get_connection


logger = get_logger(__name__)


class BlockService:
    """
    Block business logic service.
    """

    def __init__(self):
        """Initialize the Block Service."""
        logger.info("BlockService initialized.")

    def get_block_report(self, block_identifier: Any) -> Dict[str, Any]:
        """
        Get a complete block report.

        Parameters
        ----------
        block_identifier : int or str
            Block number or 'latest', etc.

        Returns
        -------
        Dict[str, Any]
            Block report.
        """
        logger.info(f"Getting block report for: {block_identifier}")

        block = get_block(block_identifier)

        if block.get("error"):
            return {
                "error": block.get("error"),
                "number": None,
            }

        # Get transaction count
        tx_count = len(block.get("transactions", []))

        # Format transaction hashes
        transactions = block.get("transactions", [])
        tx_hashes = []
        for tx in transactions[:20]:  # Limit to 20 for display
            if hasattr(tx, 'hex'):
                tx_hashes.append(tx.hex())
            else:
                tx_hashes.append(str(tx))

        return {
            "number": block.get("number"),
            "hash": block.get("hash"),
            "parent_hash": block.get("parent_hash"),
            "timestamp": block.get("timestamp"),
            "miner": block.get("miner"),
            "difficulty": block.get("difficulty"),
            "gas_used": block.get("gas_used"),
            "gas_limit": block.get("gas_limit"),
            "size": block.get("size"),
            "transaction_count": tx_count,
            "transactions": tx_hashes,
            "transaction_objects": transactions[:20] if transactions else [],
        }

    def get_latest_block_report(self) -> Dict[str, Any]:
        """
        Get the latest block report.

        Returns
        -------
        Dict[str, Any]
            Latest block report.
        """
        return self.get_block_report("latest")