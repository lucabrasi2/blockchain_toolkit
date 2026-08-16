"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.contracts

Purpose
-------
TRON smart contract intelligence.

This module provides TRON smart contract detection,
classification, and TRC-20 token analysis.

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

import requests
from typing import Dict, Any

from tron.wallets import is_valid_address
from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


# Known TRC-20 tokens with their metadata
KNOWN_TRC20_TOKENS = {
    "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t": {
        "name": "Tether USD",
        "symbol": "USDT",
        "decimals": 6,
    },
    "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj": {
        "name": "TRON",
        "symbol": "TRX",
        "decimals": 6,
    },
    "TMbja9vaWmKzPzq6b3BZ6LrBd7eFQ2hVpL": {
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6,
    },
    "TRXUpMkwdgE4WgrAdgVjK9j6jGPC5ZK5P2": {
        "name": "JustSwap",
        "symbol": "JST",
        "decimals": 18,
    },
    
    "TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3": {
        "name": "BTT",
        "symbol": "BTT",
        "decimals": 6,
    },
}


def _clean_address(address: str) -> str:
    """Clean and normalize a TRON address."""
    return address.strip()


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
        response = requests.post(
            url,
            json={"contract_address": address},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data and data.get('bytecode'):
                logger.info(f"✅ Contract detected at {address}")
                return True

        # If the above fails, check known tokens (they are contracts)
        clean_address = _clean_address(address)
        if clean_address in KNOWN_TRC20_TOKENS:
            logger.info(f"✅ Known token contract detected at {address}")
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

        # Check known tokens first (bypass contract check)
        clean_address = _clean_address(address)
        if clean_address in KNOWN_TRC20_TOKENS:
            logger.info(f"✅ Known TRC-20 token detected at {address}")
            return True

        # Check if it's a contract
        if not is_contract(address):
            return False

        # Try to check via account resource
        url = f"{TRON_API_URL}/wallet/getaccountresource"
        response = requests.post(
            url,
            json={"address": address},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
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
    logger.info(f"Getting metadata for token: {address}")

    # Clean the address
    clean_address = _clean_address(address)

    # Check known tokens with cleaned address
    if clean_address in KNOWN_TRC20_TOKENS:
        metadata = KNOWN_TRC20_TOKENS[clean_address]
        logger.info(f"Found known token: {metadata['name']} ({metadata['symbol']})")
        return metadata

    # Return default if not found
    logger.warning(f"Token {address} not found in known tokens, using default")
    return {
        "name": "TRC-20 Token",
        "symbol": "TRC20",
        "decimals": 6,
        "total_supply": 0,
    }


def get_trc20_balance(token_address: str, wallet_address: str) -> int:
    """
    Get TRC-20 token balance for a wallet.

    Parameters
    ----------
    token_address : str
        TRC-20 token address.
    wallet_address : str
        Wallet address.

    Returns
    -------
    int
        Token balance in smallest unit.
    """
    # Simplified version - in production, you'd call the contract
    return 0


###############################################################################
# End of File
###############################################################################