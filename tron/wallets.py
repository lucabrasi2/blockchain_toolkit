"""
Universal Blockchain Platform (UBP)

Module:
    TRON Wallets

Purpose:
    TRON wallet utilities using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


def is_valid_address(address: str) -> bool:
    """
    Check if a TRON address is valid.

    Parameters
    ----------
    address : str
        TRON address (starts with 'T').

    Returns
    -------
    bool
        True if valid.
    """
    try:
        if not address or not isinstance(address, str):
            return False
            
        # TRON addresses start with 'T' and are 34 characters long
        if not address.startswith('T'):
            return False
            
        if len(address) != 34:
            return False
            
        return True
        
    except Exception as error:
        logger.error(f"Error validating TRON address: {error}")
        return False


def get_trx_balance(address: str) -> Dict[str, Any]:
    """
    Get TRX balance for a wallet.

    Parameters
    ----------
    address : str
        TRON wallet address.

    Returns
    -------
    Dict[str, Any]
        Balance in TRX and SUN.
    """
    try:
        client = get_connection()
        balance_sun = client.get_balance(address)
        balance_trx = balance_sun / 1_000_000
        
        return {
            "trx": float(balance_trx),
            "sun": int(balance_sun),
        }
        
    except Exception as error:
        logger.error(f"Error getting TRX balance for {address}: {error}")
        return {"trx": 0.0, "sun": 0}


def get_account_info(address: str) -> Dict[str, Any]:
    """
    Get TRON account information.

    Parameters
    ----------
    address : str
        TRON wallet address.

    Returns
    -------
    Dict[str, Any]
        Account information.
    """
    try:
        client = get_connection()
        return client.get_account(address)
        
    except Exception as error:
        logger.error(f"Error getting account info for {address}: {error}")
        return {"address": address, "error": str(error)}