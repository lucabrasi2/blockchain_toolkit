"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Wallets

Purpose:
    Bitcoin wallet utilities using public API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


def is_valid_address(address: str) -> bool:
    """
    Check if a Bitcoin address is valid.

    Parameters
    ----------
    address : str
        Bitcoin address.

    Returns
    -------
    bool
        True if valid.
    """
    try:
        if not address or not isinstance(address, str):
            return False
            
        # Bitcoin addresses start with 1, 3, or bc1
        if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
            return False
        
        # Try to get address info from API
        client = get_connection()
        result = client.get_address(address)
        return "error" not in result
        
    except Exception as error:
        logger.error(f"Error validating Bitcoin address: {error}")
        return False


def get_btc_balance(address: str) -> Dict[str, Any]:
    """
    Get BTC balance for an address.

    Parameters
    ----------
    address : str
        Bitcoin address.

    Returns
    -------
    Dict[str, Any]
        Balance in BTC and satoshis.
    """
    try:
        client = get_connection()
        result = client.get_address(address)
        
        if "error" in result:
            return {"btc": 0.0, "satoshis": 0, "error": result["error"]}
        
        return {
            "btc": result.get("balance", 0),
            "satoshis": result.get("balance_satoshis", 0),
            "transaction_count": result.get("transaction_count", 0),
            "total_received": result.get("total_received", 0),
            "total_sent": result.get("total_sent", 0),
        }
        
    except Exception as error:
        logger.error(f"Error getting BTC balance for {address}: {error}")
        return {"btc": 0.0, "satoshis": 0, "error": str(error)}


def get_address_info(address: str) -> Dict[str, Any]:
    """
    Get detailed address information.

    Parameters
    ----------
    address : str
        Bitcoin address.

    Returns
    -------
    Dict[str, Any]
        Address information.
    """
    try:
        client = get_connection()
        return client.get_address(address)
        
    except Exception as error:
        logger.error(f"Error getting address info: {error}")
        return {"error": str(error)}