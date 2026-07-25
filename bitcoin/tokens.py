"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.tokens

Purpose
-------
Bitcoin token utilities (placeholder).

Bitcoin doesn't have tokens like Ethereum.
This file exists for structural consistency.

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

from typing import Dict, Any, Optional

from core.logger import get_logger

logger = get_logger(__name__)


def get_token_metadata(address: str) -> Dict[str, Any]:
    """
    Bitcoin doesn't have tokens.

    Parameters
    ----------
    address : str
        Token address.

    Returns
    -------
    Dict[str, Any]
        Empty metadata.
    """
    return {
        "name": "N/A",
        "symbol": "N/A",
        "decimals": 0,
        "is_token": False,
        "message": "Bitcoin does not support tokens",
    }


def get_total_supply(address: str) -> Optional[int]:
    """
    Bitcoin doesn't have tokens.

    Returns
    -------
    Optional[int]
        None.
    """
    return None


def get_token_balance(token_address: str, wallet_address: str) -> Optional[int]:
    """
    Bitcoin doesn't have tokens.

    Returns
    -------
    Optional[int]
        None.
    """
    return None


def is_token(address: str) -> bool:
    """
    Bitcoin doesn't have tokens.

    Returns
    -------
    bool
        Always False.
    """
    return False


###############################################################################
# End of File
###############################################################################
