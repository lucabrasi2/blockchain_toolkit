"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.connection

Purpose
-------
TRON network connection management.

This module provides TRON API connection management
with automatic provider selection and fallback.

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
import requests
from typing import Dict, Any, Optional

from core.logger import get_logger

logger = get_logger(__name__)


# TRON public endpoints
PUBLIC_ENDPOINTS = {
    "mainnet": "https://api.trongrid.io",
    "shasta": "https://api.shasta.trongrid.io",
    "nile": "https://nile.trongrid.io",
}


class TronHTTPClient:
    """
    TRON HTTP API client.
    """

    def __init__(self, base_url: str = "https://api.trongrid.io"):
        self.base_url = base_url
        self._connected = False

    def is_connected(self) -> bool:
        """
        Check if connected to TRON network.

        Returns
        -------
        bool
            True if connected.
        """
        try:
            block = self.get_latest_block_number()
            return block > 0
        except Exception:
            return False

    def get_latest_block_number(self) -> int:
        """Get the latest TRON block number."""
        try:
            response = requests.post(
                f"{self.base_url}/wallet/getnowblock",
                timeout=10
            )
            data = response.json()
            return data.get('block_header', {}).get('raw_data', {}).get('number', 0)
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return 0

    def get_account(self, address: str) -> Dict[str, Any]:
        """Get TRON account information."""
        try:
            response = requests.post(
                f"{self.base_url}/wallet/getaccount",
                json={"address": address},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return {}

    def get_balance(self, address: str) -> int:
        """Get TRX balance in SUN."""
        try:
            account = self.get_account(address)
            return account.get('balance', 0)
        except Exception:
            return 0

    def get_block(self, block_identifier: int) -> Dict[str, Any]:
        """Get block by number."""
        try:
            response = requests.post(
                f"{self.base_url}/wallet/getblockbynum",
                json={"num": block_identifier},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting block: {e}")
            return {}

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction by hash."""
        try:
            response = requests.post(
                f"{self.base_url}/wallet/gettransactionbyid",
                json={"value": tx_hash},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return {}


def get_connection(network: str = "mainnet") -> TronHTTPClient:
    """
    Get a TRON connection.

    Parameters
    ----------
    network : str
        'mainnet', 'shasta', or 'nile'

    Returns
    -------
    TronHTTPClient
        TRON client instance.
    """
    # Try from environment first
    rpc_url = os.getenv("TRON_RPC_URL")

    if not rpc_url:
        rpc_url = PUBLIC_ENDPOINTS.get(network, PUBLIC_ENDPOINTS["mainnet"])

    try:
        logger.info(f"Connecting to TRON: {rpc_url}")
        client = TronHTTPClient(rpc_url)

        # Test connection
        block = client.get_latest_block_number()
        if block > 0:
            logger.info(f"✅ Connected to TRON. Block: {block}")
            return client
        else:
            raise ConnectionError(f"Failed to connect to TRON: {rpc_url}")

    except Exception as error:
        logger.error(f"TRON connection error: {error}")
        raise ConnectionError(f"Failed to connect to TRON: {error}")


###############################################################################
# End of File
###############################################################################