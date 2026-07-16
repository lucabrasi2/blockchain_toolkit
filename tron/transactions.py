"""
Universal Blockchain Platform (UBP)

Module:
    TRON Transactions

Purpose:
    TRON transaction utilities using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import requests
from typing import Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    Get TRON transaction by hash.

    Parameters
    ----------
    tx_hash : str
        Transaction hash.

    Returns
    -------
    Dict[str, Any]
        Transaction information.
    """
    try:
        response = requests.post(
            f"{TRON_API_URL}/wallet/gettransactionbyid",
            json={"value": tx_hash},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                # Parse transaction data
                contract = data.get('raw_data', {}).get('contract', [{}])[0]
                value = contract.get('parameter', {}).get('value', {})
                
                return {
                    "hash": tx_hash,
                    "block_number": data.get('blockNumber'),
                    "from": value.get('owner_address'),
                    "to": value.get('to_address'),
                    "amount": value.get('amount'),
                    "status": data.get('status'),
                }
        else:
            return {"hash": tx_hash, "error": f"HTTP {response.status_code}"}
        
    except Exception as error:
        logger.error(f"Error getting transaction: {error}")
        return {"hash": tx_hash, "error": str(error)}