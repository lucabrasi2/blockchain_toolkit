"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.network

Purpose
-------
TRON network information.

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

from typing import Dict, Any, Optional
import requests

from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


def get_network_info() -> Dict[str, Any]:
    """
    Get TRON network information.

    Returns
    -------
    Dict[str, Any]
        Network information.
    """
    try:
        client = get_connection()
        block = client.get_latest_block_number()

        # Get chain parameters
        url = f"{TRON_API_URL}/wallet/getchainparameters"
        response = requests.post(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            chain_params = data.get("chainParameter", [])

            params = {}
            for param in chain_params:
                params[param.get("key")] = param.get("value")

            return {
                "network": "TRON",
                "chain_id": 0,
                "block_number": block,
                "params": params,
                "status": "active",
                "connected": True,
            }

        return {
            "network": "TRON",
            "chain_id": 0,
            "block_number": block,
            "status": "active",
            "connected": True,
        }

    except Exception as error:
        logger.error(f"Error getting network info: {error}")
        return {
            "network": "TRON",
            "chain_id": 0,
            "connected": False,
            "error": str(error),
        }


def is_connected() -> bool:
    """
    Check if connected to TRON network.

    Returns
    -------
    bool
        True if connected.
    """
    try:
        client = get_connection()
        block = client.get_latest_block_number()
        return block > 0
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
        return client.get_latest_block_number()
    except Exception as error:
        logger.error(f"Error getting block number: {error}")
        return 0


###############################################################################
# End of File
###############################################################################
