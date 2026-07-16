"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Blocks

Purpose:
    Bitcoin block utilities using public API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, List

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


def get_latest_block() -> Dict[str, Any]:
    """
    Get the latest Bitcoin block.

    Returns
    -------
    Dict[str, Any]
        Latest block information.
    """
    try:
        client = get_connection()
        return client.get_latest_block()
        
    except Exception as error:
        logger.error(f"Error getting latest block: {error}")
        return {"error": str(error)}


def get_block(block_identifier) -> Dict[str, Any]:
    """
    Get Bitcoin block by height or hash.

    Parameters
    ----------
    block_identifier : int or str
        Block height (int) or block hash (str).

    Returns
    -------
    Dict[str, Any]
        Block information.
    """
    try:
        client = get_connection()
        return client.get_block(block_identifier)
        
    except Exception as error:
        logger.error(f"Error getting block: {error}")
        return {"error": str(error)}


def get_block_transactions(block_identifier, limit: int = 10) -> List[str]:
    """
    Get transactions from a block.

    Parameters
    ----------
    block_identifier : int or str
        Block height or hash.
    limit : int
        Maximum number of transactions to return.

    Returns
    -------
    List[str]
        List of transaction hashes.
    """
    try:
        block = get_block(block_identifier)
        if "error" in block:
            return []
        
        transactions = block.get("transactions", [])
        return transactions[:limit]
        
    except Exception as error:
        logger.error(f"Error getting block transactions: {error}")
        return []