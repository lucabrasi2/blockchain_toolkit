"""
Universal Blockchain Platform (UBP)

Module:
    Ethereum Connection

Purpose:
    Manage Ethereum network connections with provider support.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
from web3 import Web3

from core.logger import get_logger
from providers import get_provider, get_web3

logger = get_logger(__name__)


def get_connection() -> Web3:
    """
    Get a Web3 connection using the provider system.

    Returns
    -------
    Web3
        Web3 instance.

    Raises
    ------
    ConnectionError
        If unable to connect to the network.
    """
    try:
        w3 = get_web3()
        if w3 and w3.is_connected():
            logger.info(f"✅ Connected via provider. Chain ID: {w3.eth.chain_id}")
            return w3

        # Fallback to direct RPC URL from .env
        rpc_url = os.getenv("ETHEREUM_RPC_URL")
        if rpc_url:
            logger.info(f"Using fallback RPC: {rpc_url}")
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                logger.info(f"✅ Connected via fallback RPC. Chain ID: {w3.eth.chain_id}")
                return w3

        raise ConnectionError("No connection could be established")

    except Exception as error:
        logger.error(f"Connection error: {error}")
        raise ConnectionError(f"Failed to connect: {error}")