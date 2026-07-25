"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron

Purpose
-------
TRON blockchain intelligence module.

This module provides comprehensive TRON blockchain
intelligence including wallet inspection, contract analysis,
token information, block exploration, and transaction analysis.

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

from tron.connection import get_connection
from tron.wallets import (
    is_valid_address,
    get_trx_balance,
    get_account_info,
)
from tron.contracts import (
    is_contract,
    is_trc20,
    get_trc20_metadata,
    get_trc20_balance,
)
from tron.tokens import (
    get_token_metadata,
    get_total_supply,
    get_token_balance,
    is_trc20_token,
)
from tron.blocks import get_latest_block_number, get_block
from tron.transactions import get_transaction
from tron.gas import get_energy_optimizer, TronEnergyOptimizer
from tron.metadata import get_contract_metadata, TronContractMetadata
from tron.network import get_network_info, is_connected, get_block_number
from tron.node_validator import validate_node, compare_nodes

__all__ = [
    # Connection
    "get_connection",
    # Wallets
    "is_valid_address",
    "get_trx_balance",
    "get_account_info",
    # Contracts
    "is_contract",
    "is_trc20",
    "get_trc20_metadata",
    "get_trc20_balance",
    # Tokens
    "get_token_metadata",
    "get_total_supply",
    "get_token_balance",
    "is_trc20_token",
    # Blocks
    "get_latest_block_number",
    "get_block",
    # Transactions
    "get_transaction",
    # Gas/Energy
    "get_energy_optimizer",
    "TronEnergyOptimizer",
    # Metadata
    "get_contract_metadata",
    "TronContractMetadata",
    # Network
    "get_network_info",
    "is_connected",
    "get_block_number",
    # Node Validation
    "validate_node",
    "compare_nodes",
]


###############################################################################
# End of File
###############################################################################