"""
Universal Blockchain Platform (UBP)

Module:
    Ethereum Connection

Purpose:
    Manage Ethereum network connections.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
from web3 import Web3
from web3.providers import HTTPProvider

from core.logger import get_logger


logger = get_logger(__name__)


# Confirmed working public endpoints
WORKING_ENDPOINTS = [
    "https://mainnet.infura.io/v3/84842078b09946638c03157f83405213",  # ✅ Confirmed working
    "https://cloudflare-eth.com",
    "https://rpc.ankr.com/eth",
]


def get_connection():
    """
    Get a Web3 connection with automatic fallback.
    """
    # First try the confirmed working endpoints
    for endpoint in WORKING_ENDPOINTS:
        try:
            logger.info(f"Trying: {endpoint}")
            w3 = Web3(HTTPProvider(endpoint))
            if w3.is_connected():
                logger.info(f"✅ Connected to: {endpoint}")
                logger.info(f"   Chain ID: {w3.eth.chain_id}")
                logger.info(f"   Block: {w3.eth.block_number}")
                return w3
            else:
                logger.warning(f"⚠️ Failed to connect: {endpoint}")
        except Exception as e:
            logger.warning(f"⚠️ Error connecting to {endpoint}: {e}")
    
    # Try Alchemy from .env if available
    alchemy_url = os.getenv("ALCHEMY_HTTP_URL")
    if alchemy_url and "YOUR_ALCHEMY" not in alchemy_url:
        try:
            logger.info("Trying Alchemy...")
            w3 = Web3(HTTPProvider(alchemy_url))
            if w3.is_connected():
                logger.info(f"✅ Connected to Alchemy. Chain ID: {w3.eth.chain_id}")
                return w3
        except Exception as e:
            logger.warning(f"Alchemy failed: {e}")
    
    # Try RPC from .env as last resort
    rpc_url = os.getenv("ETHEREUM_RPC_URL")
    if rpc_url:
        try:
            logger.info(f"Trying .env RPC: {rpc_url}")
            w3 = Web3(HTTPProvider(rpc_url))
            if w3.is_connected():
                logger.info(f"✅ Connected to .env RPC. Chain ID: {w3.eth.chain_id}")
                return w3
        except Exception as e:
            logger.warning(f".env RPC failed: {e}")
    
    raise Exception("No connection could be established to any Ethereum node")


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