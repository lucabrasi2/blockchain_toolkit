"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.network

Purpose
-------
Bitcoin network information.

This module provides network status and information.

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

from typing import Dict, Any
import requests

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


def get_network_info() -> Dict[str, Any]:
    """
    Get Bitcoin network information.

    Returns
    -------
    Dict[str, Any]
        Network information.
    """
    try:
        client = get_connection()

        # Get latest block
        block = client.get_latest_block()

        if "error" not in block:
            return {
                "network": "Bitcoin",
                "chain_id": 0,
                "block_number": block.get("number"),
                "status": "active",
                "connected": True,
                "difficulty": block.get("difficulty"),
                "transaction_count": block.get("transaction_count"),
                "size": block.get("size"),
            }

        return {
            "network": "Bitcoin",
            "chain_id": 0,
            "connected": False,
            "error": block.get("error"),
        }

    except Exception as error:
        logger.error(f"Error getting network info: {error}")
        return {
            "network": "Bitcoin",
            "chain_id": 0,
            "connected": False,
            "error": str(error),
        }


def is_connected() -> bool:
    """
    Check if connected to Bitcoin network.

    Returns
    -------
    bool
        True if connected.
    """
    try:
        client = get_connection()
        block = client.get_latest_block()
        return "error" not in block
    except Exception:
        return False


def get_block_number() -> int:
    """
    Get current block number.

    Returns
    -------
    int
        Current block number.
    """
    try:
        client = get_connection()
        block = client.get_latest_block()
        if "error" not in block:
            return block.get("number", 0)
        return 0
    except Exception as error:
        logger.error(f"Error getting block number: {error}")
        return 0


###############################################################################
# End of File
###############################################################################
