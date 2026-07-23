"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
ethereum

Purpose
-------
Ethereum blockchain intelligence module.

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

from ethereum.connection import get_connection
from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
    get_transaction_count,
)
from ethereum.contracts import (
    is_contract,
    is_erc20,
    is_erc721,
    is_erc1155,
    classify_address,
    get_bytecode,
    get_bytecode_size,
)
from ethereum.tokens import (
    get_token_metadata,
    get_total_supply,
    get_token_balance,
)
from ethereum.blocks import get_block, get_latest_block
from ethereum.transactions import get_transaction, get_transaction_status
from ethereum.gas import get_gas_optimizer, GasOptimizer
from ethereum.metadata import get_contract_metadata
from ethereum.node_validator import validate_node, compare_nodes

__all__ = [
    "get_connection",
    "is_valid_address",
    "get_eth_balance",
    "get_nonce",
    "get_transaction_count",
    "is_contract",
    "is_erc20",
    "is_erc721",
    "is_erc1155",
    "classify_address",
    "get_bytecode",
    "get_bytecode_size",
    "get_token_metadata",
    "get_total_supply",
    "get_token_balance",
    "get_block",
    "get_latest_block",
    "get_transaction",
    "get_transaction_status",
    "get_gas_optimizer",
    "GasOptimizer",
    "get_contract_metadata",
    "validate_node",
    "compare_nodes",
]


###############################################################################
# End of File
###############################################################################