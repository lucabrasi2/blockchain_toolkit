"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Contract Type Constants

Architectural Intent
--------------------
This module defines the official vocabulary used
by the Ethereum intelligence layer.

No service, controller, or formatter should
create its own contract classification strings.

All classification decisions must use these
constants.
"""


# ============================================================================
# Ethereum Account Types
# ============================================================================


EOA = "EOA"
"""
Externally Owned Account.

A traditional Ethereum account controlled
by a private key with no associated code.
"""


EOA_DELEGATED = "EOA_DELEGATED"
"""
Delegated Externally Owned Account.

Introduced by EIP-7702.

An EOA that temporarily or permanently
delegates execution behaviour to contract
code.

Such accounts contain bytecode but are
not traditional smart contracts.
"""


# ============================================================================
# Smart Contract Types
# ============================================================================


CONTRACT = "SMART_CONTRACT"
"""
Generic deployed smart contract.

Used when bytecode exists but no recognised
standard is detected.
"""


ERC20 = "ERC20"
"""
ERC-20 fungible token contract.

Examples:
- USDC
- USDT
- WETH
"""


ERC721 = "ERC721"
"""
ERC-721 non-fungible token contract.
"""


ERC1155 = "ERC1155"
"""
ERC-1155 multi-token contract.
"""


UNKNOWN = "UNKNOWN"
"""
Unknown or unclassified Ethereum entity.
"""


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "EOA",

    "EOA_DELEGATED",

    "CONTRACT",

    "ERC20",

    "ERC721",

    "ERC1155",

    "UNKNOWN",

]