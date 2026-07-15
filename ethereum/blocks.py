"""
Universal Blockchain Platform (UBP)

Module:
    Block Utilities

Purpose:
    Ethereum block retrieval and analysis.

Responsibilities:
    • Get block by number or hash
    • Get latest block
    • Get block transactions
    • Get block metadata

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional, List
from web3 import Web3

from ethereum.connection import get_connection
from ethereum.wallets import is_valid_address
from core.logger import get_logger


logger = get_logger(__name__)


def get_block(block_identifier: Any) -> Dict[str, Any]:
    """
    Get block information by number or hash.

    Parameters
    ----------
    block_identifier : int or str
        Block number (int) or 'latest', 'pending', 'earliest', or block hash (str).

    Returns
    -------
    Dict[str, Any]
        Block information.
    """
    try:
        w3 = get_connection()
        
        # If it's a string and starts with 0x, it's a block hash
        if isinstance(block_identifier, str) and block_identifier.startswith('0x'):
            block = w3.eth.get_block(block_identifier)
        else:
            # It's a block number or 'latest', 'pending', 'earliest'
            block = w3.eth.get_block(block_identifier)
        
        # Format the block data
        return {
            "number": block.get("number"),
            "hash": block.get("hash").hex() if block.get("hash") else None,
            "parent_hash": block.get("parentHash").hex() if block.get("parentHash") else None,
            "timestamp": block.get("timestamp"),
            "miner": block.get("miner"),
            "difficulty": block.get("difficulty"),
            "gas_used": block.get("gasUsed"),
            "gas_limit": block.get("gasLimit"),
            "size": block.get("size"),
            "transaction_count": len(block.get("transactions", [])),
            "transactions": block.get("transactions", []),
        }
        
    except Exception as error:
        logger.error(f"Error getting block: {error}")
        return {
            "number": None,
            "error": str(error),
        }


def get_latest_block() -> Dict[str, Any]:
    """
    Get the latest block.

    Returns
    -------
    Dict[str, Any]
        Latest block information.
    """
    return get_block("latest")


def get_block_transactions(block_identifier: Any) -> List[Dict[str, Any]]:
    """
    Get all transactions in a block.

    Parameters
    ----------
    block_identifier : int or str
        Block number or 'latest', etc.

    Returns
    -------
    List[Dict[str, Any]]
        List of transactions in the block.
    """
    try:
        block = get_block(block_identifier)
        if block.get("error"):
            return []
        
        return block.get("transactions", [])
        
    except Exception as error:
        logger.error(f"Error getting block transactions: {error}")
        return []


def get_block_transaction_count(block_identifier: Any) -> int:
    """
    Get the number of transactions in a block.

    Parameters
    ----------
    block_identifier : int or str
        Block number or 'latest', etc.

    Returns
    -------
    int
        Number of transactions.
    """
    try:
        w3 = get_connection()
        
        if isinstance(block_identifier, str) and block_identifier.startswith('0x'):
            count = w3.eth.get_block_transaction_count(block_identifier)
        else:
            count = w3.eth.get_block_transaction_count(block_identifier)
        
        return count
        
    except Exception as error:
        logger.error(f"Error getting block transaction count: {error}")
        return 0