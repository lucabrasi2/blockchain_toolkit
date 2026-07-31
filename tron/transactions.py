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

from core.http_client import http_client
from typing import Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)


import os

TRON_API_URL = os.getenv(
    "TRONGRID_API_URL",
    "https://api.trongrid.io"
)

TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")


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
    if len(tx_hash) != 64:
     return {
        "hash": tx_hash,
        "error": "Invalid TRON transaction hash",
    }
    try:
        headers = {}
        if TRONGRID_API_KEY:
            headers["TRON-PRO-API-KEY"] = TRONGRID_API_KEY

        response = http_client.post(
    f"{TRON_API_URL}/wallet/gettransactionbyid",
    json={"value": tx_hash},
    headers=headers,
)
        

        if response.status_code != 200:
            return {"hash": tx_hash, "error": f"HTTP {response.status_code}"}

        data = response.json()
        if not data:
            return {"hash": tx_hash, "error": "Transaction not found"}

        contract = data.get("raw_data", {}).get("contract", [{}])[0]
        value = contract.get("parameter", {}).get("value", {})

        return {
            "hash": tx_hash,
            "block_number": data.get("blockNumber"),
            "from": value.get("owner_address"),
            "to": value.get("to_address"),
            "amount": value.get("amount"),
            "status": data.get("status"),
        }
    except Exception as error:
      logger.exception(f"Error getting TRON transaction: {tx_hash}")

    return {
        "hash": tx_hash,
        "error": str(error),
    }