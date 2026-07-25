"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin

Purpose
-------
Bitcoin blockchain intelligence module.

This module provides comprehensive Bitcoin blockchain
intelligence including wallet inspection, block exploration,
transaction analysis, and fee optimization.

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

from bitcoin.connection import get_connection
from bitcoin.wallets import is_valid_address, get_btc_balance, get_address_info
from bitcoin.blocks import get_block, get_latest_block, get_block_transactions
from bitcoin.transactions import get_transaction, get_transaction_status
from bitcoin.contracts import is_contract, classify_address
from bitcoin.gas import get_fee_optimizer, BitcoinFeeOptimizer
from bitcoin.metadata import get_transaction_metadata, BitcoinTransactionMetadata
from bitcoin.network import get_network_info, is_connected, get_block_number
from bitcoin.node_validator import validate_node, compare_nodes
from bitcoin.tokens import get_token_metadata, get_total_supply, get_token_balance, is_token

__all__ = [
    # Connection
    "get_connection",
    # Wallets
    "is_valid_address",
    "get_btc_balance",
    "get_address_info",
    # Blocks
    "get_block",
    "get_latest_block",
    "get_block_transactions",
    # Transactions
    "get_transaction",
    "get_transaction_status",
    # Contracts (Bitcoin doesn't have contracts, but for consistency)
    "is_contract",
    "classify_address",
    # Gas/Fees
    "get_fee_optimizer",
    "BitcoinFeeOptimizer",
    # Metadata
    "get_transaction_metadata",
    "BitcoinTransactionMetadata",
    # Network
    "get_network_info",
    "is_connected",
    "get_block_number",
    # Node Validation
    "validate_node",
    "compare_nodes",
    # Tokens (placeholder)
    "get_token_metadata",
    "get_total_supply",
    "get_token_balance",
    "is_token",
]


###############################################################################
# End of File
###############################################################################