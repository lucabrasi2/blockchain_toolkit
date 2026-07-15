"""
Universal Blockchain Platform (UBP)

Module:
    Transaction Utilities

Purpose:
    Ethereum transaction retrieval and analysis.

Responsibilities:
    • Get transaction by hash
    • Get transaction receipt
    • Analyze transaction status
    • Get transaction details

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional
from web3 import Web3

from ethereum.connection import get_connection
from core.logger import get_logger


logger = get_logger(__name__)


def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    Get transaction by hash.

    Parameters
    ----------
    tx_hash : str
        Transaction hash.

    Returns
    -------
    Dict[str, Any]
        Transaction information.
    """
    try:
        w3 = get_connection()
        tx = w3.eth.get_transaction(tx_hash)
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        return {
            "hash": tx.get("hash").hex() if tx.get("hash") else None,
            "block_number": tx.get("blockNumber"),
            "block_hash": tx.get("blockHash").hex() if tx.get("blockHash") else None,
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": w3.from_wei(tx.get("value", 0), "ether"),
            "gas": tx.get("gas"),
            "gas_price": tx.get("gasPrice"),
            "nonce": tx.get("nonce"),
            "input": tx.get("input"),
            "status": receipt.get("status") == 1 if receipt else None,
            "gas_used": receipt.get("gasUsed") if receipt else None,
            "contract_address": receipt.get("contractAddress") if receipt else None,
            "logs": receipt.get("logs", []) if receipt else [],
        }
        
    except Exception as error:
        logger.error(f"Error getting transaction: {error}")
        return {
            "hash": tx_hash,
            "error": str(error),
        }


def get_transaction_receipt(tx_hash: str) -> Dict[str, Any]:
    """
    Get transaction receipt.

    Parameters
    ----------
    tx_hash : str
        Transaction hash.

    Returns
    -------
    Dict[str, Any]
        Transaction receipt.
    """
    try:
        w3 = get_connection()
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        return {
            "tx_hash": tx_hash,
            "block_number": receipt.get("blockNumber"),
            "block_hash": receipt.get("blockHash").hex() if receipt.get("blockHash") else None,
            "status": receipt.get("status") == 1,
            "gas_used": receipt.get("gasUsed"),
            "contract_address": receipt.get("contractAddress"),
            "logs": receipt.get("logs", []),
            "logs_count": len(receipt.get("logs", [])),
        }
        
    except Exception as error:
        logger.error(f"Error getting transaction receipt: {error}")
        return {
            "tx_hash": tx_hash,
            "error": str(error),
        }


def get_transaction_status(tx_hash: str) -> str:
    """
    Get transaction status (Success/Failed/Pending).

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
        receipt = get_transaction_receipt(tx_hash)
        
        if receipt.get("error"):
            return "Unknown"
        
        status = receipt.get("status")
        if status is True:
            return "Success"
        elif status is False:
            return "Failed"
        else:
            return "Pending"
            
    except Exception as error:
        logger.error(f"Error getting transaction status: {error}")
        return "Unknown"