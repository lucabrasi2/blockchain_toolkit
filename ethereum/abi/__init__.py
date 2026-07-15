"""
Universal Blockchain Platform (UBP)

Module:
    Ethereum ABIs Package

Purpose:
    Centralized access to all contract
    ABIs used in the platform.
"""

from ethereum.abi.erc20 import ERC20_ABI
from ethereum.abi.erc165 import ERC165_ABI
from ethereum.abi.erc721 import ERC721_ABI
from ethereum.abi.erc1155 import ERC1155_ABI
from ethereum.abi.common import OWNER_ABI, METADATA_ABI


__all__ = [
    "ERC20_ABI",
    "ERC165_ABI",
    "ERC721_ABI",
    "ERC1155_ABI",
    "OWNER_ABI",
    "METADATA_ABI",
]
