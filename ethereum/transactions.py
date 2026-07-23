"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
ethereum.transactions

Purpose
-------
Ethereum transaction utilities.

This module provides transaction retrieval and analysis.

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
from web3 import Web3
from eth_utils import to_hex, to_checksum_address

from ethereum.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


def normalize_hash(tx_hash: Any) -> str:
    """
    Normalize a transaction hash to hex string.

    Parameters
    ----------
    tx_hash : Any
        Transaction hash (bytes, hex string, or other).

    Returns
    -------
    str
        Normalized hex string with 0x prefix.
    """
    if tx_hash is None:
        return "0x"

    if isinstance(tx_hash, bytes):
        return '0x' + tx_hash.hex()

    if isinstance(tx_hash, str):
        if tx_hash.startswith('0x'):
            return tx_hash
        return '0x' + tx_hash

    return str(tx_hash)


def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    Get transaction by hash.

    Parameters
    ----------
    tx_hash : str
        Transaction hash (with or without 0x prefix).

    Returns
    -------
    Dict[str, Any]
        Transaction information.
    """
    try:
        w3 = get_connection()

        # Normalize the hash
        normalized_hash = normalize_hash(tx_hash)

        # Validate hash format
        clean_hash = normalized_hash.replace('0x', '')
        if not all(c in '0123456789abcdefABCDEF' for c in clean_hash):
            return {"hash": normalized_hash, "error": "Invalid transaction hash format"}

        # Get transaction
        tx = w3.eth.get_transaction(normalized_hash)

        # Get receipt for status
        try:
            receipt = w3.eth.get_transaction_receipt(normalized_hash)
            status = receipt.get('status') == 1
            gas_used = receipt.get('gasUsed')
            contract_address = receipt.get('contractAddress')
            logs = receipt.get('logs', [])
        except Exception:
            status = None
            gas_used = None
            contract_address = None
            logs = []

        # Build response
        return {
            "hash": normalized_hash,
            "block_number": tx.get("blockNumber"),
            "block_hash": normalize_hash(tx.get("blockHash")),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": w3.from_wei(tx.get("value", 0), "ether"),
            "gas": tx.get("gas"),
            "gas_price": tx.get("gasPrice"),
            "nonce": tx.get("nonce"),
            "input": normalize_hash(tx.get("input")),
            "is_success": status,
            "gas_used": gas_used,
            "contract_address": contract_address,
            "logs": logs,
            "chain_id": tx.get("chainId"),
            "max_fee_per_gas": tx.get("maxFeePerGas"),
            "max_priority_fee_per_gas": tx.get("maxPriorityFeePerGas"),
            "transaction_index": tx.get("transactionIndex"),
            "type": tx.get("type"),
            "v": tx.get("v"),
            "r": tx.get("r"),
            "s": tx.get("s"),
        }

    except Exception as error:
        logger.error(f"Error getting transaction: {error}")
        return {"hash": normalize_hash(tx_hash), "error": str(error)}


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
        normalized_hash = normalize_hash(tx_hash)
        receipt = w3.eth.get_transaction_receipt(normalized_hash)

        return {
            "tx_hash": normalized_hash,
            "block_number": receipt.get("blockNumber"),
            "block_hash": normalize_hash(receipt.get("blockHash")),
            "status": receipt.get("status") == 1,
            "gas_used": receipt.get("gasUsed"),
            "cumulative_gas_used": receipt.get("cumulativeGasUsed"),
            "contract_address": receipt.get("contractAddress"),
            "logs": receipt.get("logs", []),
            "logs_count": len(receipt.get("logs", [])),
            "transaction_index": receipt.get("transactionIndex"),
            "effective_gas_price": receipt.get("effectiveGasPrice"),
            "type": receipt.get("type"),
            "root": receipt.get("root"),
        }

    except Exception as error:
        logger.error(f"Error getting transaction receipt: {error}")
        return {"tx_hash": normalize_hash(tx_hash), "error": str(error)}


def get_transaction_status(tx_hash: str) -> str:
    """
    Get transaction status.

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


###############################################################################
# End of File
###############################################################################