"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Package

Purpose:
    Bitcoin blockchain utilities and intelligence.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from bitcoin.connection import get_connection, BitcoinClient
from bitcoin.wallets import is_valid_address, get_btc_balance, get_address_info
from bitcoin.blocks import get_block, get_latest_block, get_block_transactions
from bitcoin.transactions import get_transaction, get_transaction_status

__all__ = [
    "get_connection",
    "BitcoinClient",
    "is_valid_address",
    "get_btc_balance",
    "get_address_info",
    "get_block",
    "get_latest_block",
    "get_block_transactions",
    "get_transaction",
    "get_transaction_status",
]