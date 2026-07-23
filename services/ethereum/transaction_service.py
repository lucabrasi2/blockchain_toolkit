"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.transaction_service

Purpose
-------
Ethereum transaction service layer.

This service provides comprehensive transaction analysis,
retrieval, and reporting functionality.

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

from __future__ import annotations

from typing import Dict, Any, Optional
from web3 import Web3

from core.logger import get_logger
from ethereum.connection import get_connection
from ethereum.transactions import get_transaction as get_raw_transaction

logger = get_logger(__name__)


class TransactionService:
    """
    Ethereum transaction service.
    
    Provides transaction analysis, retrieval, and reporting.
    """

    def __init__(self):
        """Initialize the transaction service."""
        self.w3 = get_connection()
        logger.info("TransactionService initialized.")

    def get_connection(self) -> Web3:
        """Get the Web3 connection."""
        return self.w3

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get raw transaction by hash.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Dict[str, Any]
            Raw transaction data.
        """
        try:
            return self.w3.eth.get_transaction(tx_hash)
        except Exception as error:
            logger.error(f"Error getting transaction: {error}")
            raise

    def get_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Optional[Dict[str, Any]]
            Transaction receipt or None.
        """
        try:
            return self.w3.eth.get_transaction_receipt(tx_hash)
        except Exception:
            return None

    def wei_to_eth(self, wei: int) -> float:
        """
        Convert Wei to Ether.

        Parameters
        ----------
        wei : int
            Amount in Wei.

        Returns
        -------
        float
            Amount in Ether.
        """
        return float(self.w3.from_wei(wei, "ether"))

    def eth_to_wei(self, eth: float) -> int:
        """
        Convert Ether to Wei.

        Parameters
        ----------
        eth : float
            Amount in Ether.

        Returns
        -------
        int
            Amount in Wei.
        """
        return int(self.w3.to_wei(eth, "ether"))

    def get_transaction_report(self, tx_hash: str) -> Dict[str, Any]:
        """
        Generate a complete transaction report.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Dict[str, Any]
            Complete transaction report.
        """
        logger.info(f"Generating transaction report for: {tx_hash}")

        try:
            # Normalize the hash
            if isinstance(tx_hash, bytes):
                tx_hash = '0x' + tx_hash.hex()
            elif not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash

            # Get transaction
            tx = self.get_transaction(tx_hash)

            # Get receipt
            receipt = self.get_receipt(tx_hash)

            # Build report
            report = {
                "hash": tx_hash,
                "block_number": tx.get("blockNumber"),
                "block_hash": tx.get("blockHash").hex() if tx.get("blockHash") else None,
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": self.wei_to_eth(tx.get("value", 0)),
                "gas": tx.get("gas"),
                "gas_price": tx.get("gasPrice"),
                "nonce": tx.get("nonce"),
                "input": tx.get("input").hex() if tx.get("input") else "0x",
                "chain_id": tx.get("chainId"),
                "transaction_index": tx.get("transactionIndex"),
                "type": tx.get("type"),
            }

            # Add receipt data if available
            if receipt:
                report["is_success"] = receipt.get("status") == 1
                report["gas_used"] = receipt.get("gasUsed")
                report["cumulative_gas_used"] = receipt.get("cumulativeGasUsed")
                report["contract_address"] = receipt.get("contractAddress")
                report["logs"] = receipt.get("logs", [])
                report["effective_gas_price"] = receipt.get("effectiveGasPrice")
                report["logs_count"] = len(receipt.get("logs", []))
            else:
                report["is_success"] = None
                report["gas_used"] = None
                report["cumulative_gas_used"] = None
                report["contract_address"] = None
                report["logs"] = []
                report["effective_gas_price"] = None
                report["logs_count"] = 0

            logger.info(f"Transaction report generated for: {tx_hash}")
            return report

        except Exception as error:
            logger.error(f"Error generating transaction report: {error}")
            return {"hash": tx_hash, "error": str(error)}

    def get_transaction_status(self, tx_hash: str) -> str:
        """
        Get transaction status as string.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        str
            Transaction status.
        """
        try:
            receipt = self.get_receipt(tx_hash)
            if receipt is None:
                return "Pending"

            if receipt.get("status") == 1:
                return "Success"
            elif receipt.get("status") == 0:
                return "Failed"
            else:
                return "Unknown"

        except Exception as error:
            logger.error(f"Error getting transaction status: {error}")
            return "Unknown"

    def get_gas_price(self) -> int:
        """
        Get current gas price in Wei.

        Returns
        -------
        int
            Gas price in Wei.
        """
        return self.w3.eth.gas_price

    def get_gas_price_gwei(self) -> float:
        """
        Get current gas price in Gwei.

        Returns
        -------
        float
            Gas price in Gwei.
        """
        return float(self.w3.from_wei(self.get_gas_price(), "gwei"))

    def is_transaction_confirmed(self, tx_hash: str) -> bool:
        """
        Check if a transaction is confirmed.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        bool
            True if confirmed.
        """
        receipt = self.get_receipt(tx_hash)
        return receipt is not None

    def get_transaction_confirmations(self, tx_hash: str) -> int:
        """
        Get number of confirmations for a transaction.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        int
            Number of confirmations.
        """
        try:
            receipt = self.get_receipt(tx_hash)
            if receipt is None:
                return 0

            current_block = self.w3.eth.block_number
            tx_block = receipt.get("blockNumber")

            if tx_block is None:
                return 0

            return current_block - tx_block + 1

        except Exception as error:
            logger.error(f"Error getting confirmations: {error}")
            return 0


###############################################################################
# End of File
###############################################################################