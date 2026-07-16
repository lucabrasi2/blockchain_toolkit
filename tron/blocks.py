"""
Universal Blockchain Platform (UBP)

Module:
    TRON Blocks

Purpose:
    TRON block utilities using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import requests
from typing import Dict, Any

from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


def get_latest_block_number() -> int:
    """
    Get the latest TRON block number.

    Returns
    -------
    int
        Latest block number.
    """
    try:
        response = requests.post(f"{TRON_API_URL}/wallet/getnowblock", timeout=10)
        data = response.json()
        return data.get('block_header', {}).get('raw_data', {}).get('number', 0)
        
    except Exception as error:
        logger.error(f"Error getting latest block: {error}")
        return 0


def get_block(block_identifier: int) -> Dict[str, Any]:
    """
    Get TRON block by number.

    Parameters
    ----------
    block_identifier : int
        Block number.

    Returns
    -------
    Dict[str, Any]
        Block information.
    """
    try:
        response = requests.post(
            f"{TRON_API_URL}/wallet/getblockbynum",
            json={"num": block_identifier},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "number": data.get('block_header', {}).get('raw_data', {}).get('number'),
                "hash": data.get('blockid'),
                "timestamp": data.get('block_header', {}).get('raw_data', {}).get('timestamp'),
                "transaction_count": len(data.get('transactions', [])),
                "transactions": data.get('transactions', []),
            }
        else:
            return {"number": block_identifier, "error": f"HTTP {response.status_code}"}
        
    except Exception as error:
        logger.error(f"Error getting block: {error}")
        return {"number": block_identifier, "error": str(error)}