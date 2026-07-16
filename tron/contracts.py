"""
Universal Blockchain Platform (UBP)

Module:
    TRON Contracts

Purpose:
    TRON smart contract utilities using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import requests
from typing import Dict, Any

from tron.wallets import is_valid_address
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


def is_contract(address: str) -> bool:
    """
    Check if a TRON address is a contract.

    Parameters
    ----------
    address : str
        TRON address.

    Returns
    -------
    bool
        True if it's a contract.
    """
    try:
        if not is_valid_address(address):
            return False
            
        # Try to get contract info
        url = f"{TRON_API_URL}/wallet/getcontractinfo"
        response = requests.post(url, json={"contract_address": address}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and data.get('bytecode'):
                return True
                
        return False
        
    except Exception as error:
        logger.error(f"Error checking if address is contract: {error}")
        return False


def is_trc20(address: str) -> bool:
    """
    Check if a contract is TRC-20 token.

    Parameters
    ----------
    address : str
        TRON contract address.

    Returns
    -------
    bool
        True if it's TRC-20.
    """
    try:
        if not is_valid_address(address):
            return False
            
        # Check if it's a contract first
        if not is_contract(address):
            return False
            
        # Try to get token info via account resource
        url = f"{TRON_API_URL}/wallet/getaccountresource"
        response = requests.post(url, json={"address": address}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # If it has token-related fields, it's likely a TRC-20
            if data.get('freeNetLimit') is not None:
                logger.info(f"✅ TRC-20 token detected at {address}")
                return True
                
        return False
        
    except Exception as error:
        logger.error(f"Error checking TRC-20: {error}")
        return False


def get_trc20_metadata(address: str) -> Dict[str, Any]:
    """
    Get TRC-20 token metadata.

    Parameters
    ----------
    address : str
        TRON contract address.

    Returns
    -------
    Dict[str, Any]
        Token metadata.
    """
    try:
        # For now, return basic metadata
        # In production, you'd call the contract methods via API
        return {
            "name": "TRC-20 Token",
            "symbol": "TRC20",
            "decimals": 6,
            "total_supply": 0,
        }
        
    except Exception as error:
        logger.error(f"Error getting TRC-20 metadata: {error}")
        return {
            "name": "Unknown",
            "symbol": "Unknown",
            "decimals": 18,
            "total_supply": 0,
        }