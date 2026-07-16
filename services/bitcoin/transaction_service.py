"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Transaction Service

Purpose:
    Business logic for Bitcoin transaction operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.logger import get_logger
from bitcoin.transactions import get_transaction, get_transaction_status

logger = get_logger(__name__)


class BitcoinTransactionService:
    """
    Bitcoin transaction business logic service.
    """

    def __init__(self):
        logger.info("BitcoinTransactionService initialized.")

    def get_transaction_report(self, tx_hash: str) -> Dict[str, Any]:
        """
        Generate a transaction report.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Dict[str, Any]
            Transaction report.
        """
        logger.info(f"Getting transaction report for: {tx_hash}")

        tx = get_transaction(tx_hash)

        if "error" in tx:
            return {
                "hash": tx_hash,
                "error": tx["error"],
            }

        return {
            "hash": tx.get("hash"),
            "block_number": tx.get("block_number"),
            "block_hash": tx.get("block_hash"),
            "confirmations": tx.get("confirmations", 0),
            "timestamp": tx.get("timestamp"),
            "size": tx.get("size"),
            "weight": tx.get("weight"),
            "fee": tx.get("fee"),
            "version": tx.get("version"),
            "locktime": tx.get("locktime"),
            "inputs_count": tx.get("inputs_count", 0),
            "outputs_count": tx.get("outputs_count", 0),
            "total_input": tx.get("total_input", 0),
            "inputs": tx.get("inputs", [])[:5],
            "outputs": tx.get("outputs", [])[:5],
            "status": get_transaction_status(tx_hash),
        }