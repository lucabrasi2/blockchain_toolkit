"""
Universal Blockchain Platform (UBP)

Module:
    TRON Connection

Purpose:
    Manage TRON network connections using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
import requests
from typing import Optional, Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)


class TronHTTPClient:
    """
    TRON HTTP API client.
    """
    
    def __init__(self, base_url: str = "https://api.trongrid.io"):
        self.base_url = base_url
        
    def get_latest_block_number(self) -> int:
        """Get the latest TRON block number."""
        try:
            response = requests.post(f"{self.base_url}/wallet/getnowblock", timeout=10)
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
    
    def is_address(self, address: str) -> bool:
        """Check if address is valid."""
        try:
            # TRON addresses start with 'T' and are 34 characters long
            if not address.startswith('T') or len(address) != 34:
                return False
            return True
        except Exception:
            return False
    
    def get_balance(self, address: str) -> int:
        """Get TRX balance in SUN."""
        try:
            account = self.get_account(address)
            return account.get('balance', 0)
        except Exception:
            return 0


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
        TRON connection instance.
    """
    # Try from environment first
    rpc_url = os.getenv("TRON_RPC_URL")
    
    if not rpc_url:
        if network == "mainnet":
            rpc_url = "https://api.trongrid.io"
        elif network == "shasta":
            rpc_url = "https://api.shasta.trongrid.io"
        else:
            rpc_url = "https://api.trongrid.io"
    
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