"""
Universal Blockchain Platform (UBP)

Module:
    Token Utilities

Purpose:
    Ethereum token utilities for ERC-20 tokens.

Responsibilities:
    • Get token metadata (name, symbol, decimals)
    • Get token balance
    • Get total supply
    • Check if token is ERC-20

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional
from web3 import Web3

from ethereum.connection import get_connection
from ethereum.contracts import is_erc20
from ethereum.abi import ERC20_ABI
from core.logger import get_logger


logger = get_logger(__name__)


def get_token_metadata(address: str) -> Dict[str, Any]:
    """
    Get ERC-20 token metadata.

    Parameters
    ----------
    address : str
        Token contract address.

    Returns
    -------
    Dict[str, Any]
        Token metadata including name, symbol, decimals.
    """
    try:
        w3 = get_connection()
        checksum_address = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=checksum_address, abi=ERC20_ABI)

        metadata = {}

        # Get name
        try:
            metadata["name"] = contract.functions.name().call()
        except Exception:
            metadata["name"] = "Unknown"

        # Get symbol
        try:
            metadata["symbol"] = contract.functions.symbol().call()
        except Exception:
            metadata["symbol"] = "Unknown"

        # Get decimals
        try:
            metadata["decimals"] = contract.functions.decimals().call()
        except Exception:
            metadata["decimals"] = 18

        logger.info(f"Retrieved metadata for {address}: {metadata}")
        return metadata

    except Exception as error:
        logger.error(f"Error getting token metadata for {address}: {error}")
        return {"name": "Unknown", "symbol": "Unknown", "decimals": 18}


def get_total_supply(address: str) -> Optional[int]:
    """
    Get ERC-20 token total supply.

    Parameters
    ----------
    address : str
        Token contract address.

    Returns
    -------
    Optional[int]
        Total supply in wei (smallest unit).
    """
    try:
        w3 = get_connection()
        checksum_address = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=checksum_address, abi=ERC20_ABI)

        total_supply = contract.functions.totalSupply().call()
        return total_supply

    except Exception as error:
        logger.error(f"Error getting total supply for {address}: {error}")
        return None


def get_token_balance(token_address: str, wallet_address: str) -> Optional[int]:
    """
    Get ERC-20 token balance for a wallet.

    Parameters
    ----------
    token_address : str
        Token contract address.
    wallet_address : str
        Wallet address.

    Returns
    -------
    Optional[int]
        Token balance in wei (smallest unit).
    """
    try:
        w3 = get_connection()
        checksum_token = Web3.to_checksum_address(token_address)
        checksum_wallet = Web3.to_checksum_address(wallet_address)
        contract = w3.eth.contract(address=checksum_token, abi=ERC20_ABI)

        balance = contract.functions.balanceOf(checksum_wallet).call()
        return balance

    except Exception as error:
        logger.error(f"Error getting token balance: {error}")
        return None


def get_token_info(address: str) -> Dict[str, Any]:
    """
    Get comprehensive token information.

    Parameters
    ----------
    address : str
        Token contract address.

    Returns
    -------
    Dict[str, Any]
        Token information.
    """
    metadata = get_token_metadata(address)
    total_supply = get_total_supply(address)

    return {
        "address": address,
        "name": metadata.get("name", "Unknown"),
        "symbol": metadata.get("symbol", "Unknown"),
        "decimals": metadata.get("decimals", 18),
        "total_supply": total_supply,
        "is_erc20": True,
    }