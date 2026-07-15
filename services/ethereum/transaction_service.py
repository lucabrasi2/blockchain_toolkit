"""
Universal Blockchain Platform (UBP)

Module:
    Transaction Service

Purpose:
    Business logic for Ethereum transaction operations.

Responsibilities:
    • Get transaction by hash
    • Analyze transaction
    • Get transaction status
    • Format transaction data

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from ethereum.transactions import (
    get_transaction,
    get_transaction_receipt,
    get_transaction_status,
)


logger = get_logger(__name__)


class TransactionService:
    """
    Transaction business logic service.
    """

    def __init__(self):
        """Initialize the Transaction Service."""
        logger.info("TransactionService initialized.")

    def get_transaction_report(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get a complete transaction report.

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

        if tx.get("error"):
            return {
                "hash": tx_hash,
                "error": tx.get("error"),
            }

        status = get_transaction_status(tx_hash)

        return {
            "hash": tx.get("hash"),
            "block_number": tx.get("block_number"),
            "block_hash": tx.get("block_hash"),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": tx.get("value"),
            "gas": tx.get("gas"),
            "gas_price": tx.get("gas_price"),
            "gas_used": tx.get("gas_used"),
            "nonce": tx.get("nonce"),
            "input": tx.get("input"),
            "status": status,
            "is_success": tx.get("status", False),
            "contract_address": tx.get("contract_address"),
            "logs": tx.get("logs", []),
            "logs_count": len(tx.get("logs", [])),
        }