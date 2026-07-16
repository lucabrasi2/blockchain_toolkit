"""
Universal Blockchain Platform (UBP)

Module:
    TRON Package

Purpose:
    TRON blockchain utilities and intelligence.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from tron.connection import get_connection, TronHTTPClient
from tron.wallets import is_valid_address, get_trx_balance, get_account_info
from tron.contracts import is_contract, is_trc20, get_trc20_metadata

__all__ = [
    "get_connection",
    "TronHTTPClient",
    "is_valid_address",
    "get_trx_balance",
    "get_account_info",
    "is_contract",
    "is_trc20",
    "get_trc20_metadata",
]