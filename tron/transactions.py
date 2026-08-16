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
    """
    # Clean the hash
    tx_hash = tx_hash.strip()
    if tx_hash.startswith('0x'):
        tx_hash = tx_hash[2:]
    
    # Validate length
    if len(tx_hash) != 64:
        return {
            "hash": tx_hash,
            "error": "Invalid TRON transaction hash. Must be 64 characters."
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
    "blockchain": "tron",

    "hash": tx_hash,

    "block_number": data.get("blockNumber"),

    "from": value.get("owner_address"),

    "to": value.get("to_address"),

    # TransactionDisplay expects "value"
    "value": value.get("amount", 0),

    # Keep amount for future TRON-specific reports
    "amount": value.get("amount", 0),

    # TransactionDisplay expects this field
    "is_success": data.get("ret", [{}])[0].get("contractRet") == "SUCCESS",

    "status": data.get("ret", [{}])[0].get("contractRet", "UNKNOWN"),

    # Placeholders until we implement receipt parsing
    "gas_used": None,
    "gas_price": None,
    "nonce": None,
}
    except Exception as error:
      logger.exception(f"Error getting TRON transaction: {tx_hash}")

    return {
        "hash": tx_hash,
        "error": str(error),
    }