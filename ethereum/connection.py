"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
ethereum.connection

Purpose
-------
Ethereum network connection management.

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

import os
from typing import Optional
from web3 import Web3

from core.logger import get_logger
from providers import get_web3, get_provider

logger = get_logger(__name__)


# Public RPC endpoints as fallback
PUBLIC_RPC_ENDPOINTS = [
    "https://ethereum.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
]


def get_connection() -> Web3:
    """
    Get a Web3 connection with automatic failover.
    """
    # Try provider system first
    try:
        w3 = get_web3()
        if w3 and w3.is_connected():
            logger.info(f"✅ Connected via provider. Chain ID: {w3.eth.chain_id}")
            return w3
    except Exception as e:
        logger.debug(f"Provider connection failed: {e}")

    # Try from environment
    rpc_url = os.getenv("ETHEREUM_RPC_URL")
    if rpc_url:
        try:
            logger.info(f"Connecting via .env RPC: {rpc_url}")
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                logger.info(f"✅ Connected via .env RPC. Chain ID: {w3.eth.chain_id}")
                return w3
        except Exception as e:
            logger.warning(f".env RPC failed: {e}")

    # Try public endpoints
    for endpoint in PUBLIC_RPC_ENDPOINTS:
        try:
            logger.info(f"Trying public RPC: {endpoint}")
            w3 = Web3(Web3.HTTPProvider(endpoint))
            if w3.is_connected():
                logger.info(f"✅ Connected via public RPC. Chain ID: {w3.eth.chain_id}")
                logger.info(f"   Block: {w3.eth.block_number}")
                return w3
        except Exception as e:
            logger.debug(f"Failed: {endpoint} - {e}")

    raise ConnectionError("No connection could be established to any Ethereum node")


def get_chain_id() -> int:
    """Get the current chain ID."""
    try:
        w3 = get_connection()
        return w3.eth.chain_id
    except Exception as error:
        logger.error(f"Error getting chain ID: {error}")
        return 0


def is_connected() -> bool:
    """Check if connected to Ethereum network."""
    try:
        w3 = get_connection()
        return w3.is_connected()
    except Exception:
        return False


def get_block_number() -> int:
    """Get the current block number."""
    try:
        w3 = get_connection()
        return w3.eth.block_number
    except Exception as error:
        logger.error(f"Error getting block number: {error}")
        return 0


###############################################################################
# End of File
###############################################################################