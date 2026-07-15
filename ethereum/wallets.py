"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Ethereum Wallet Utilities

Author  : Jaramogi Diddy

Description
-----------
Provides wallet-related blockchain utilities.

Responsibilities
----------------
• Address validation
• Balance retrieval
• Nonce retrieval
• Transaction count
• Token balance retrieval
"""

from web3 import Web3

from ethereum.connection import get_connection
from core.logger import get_logger


logger = get_logger(__name__)


def is_valid_address(address: str) -> bool:
    """
    Check if an Ethereum address is valid.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    bool
        True if the address is valid.
    """

    try:
        return Web3.is_checksum_address(address) or Web3.is_address(address)
    except Exception:
        return False


def get_eth_balance(address: str) -> dict:
    """
    Get ETH balance for an address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    dict
        Balance in ETH and Wei.
    """

    try:
        w3 = get_connection()
        checksum_address = Web3.to_checksum_address(address)
        balance_wei = w3.eth.get_balance(checksum_address)
        balance_eth = w3.from_wei(balance_wei, "ether")

        return {
            "wei": balance_wei,
            "ether": float(balance_eth),
        }

    except Exception as error:
        logger.error(f"Error getting balance: {error}")
        return {"wei": 0, "ether": 0.0}


def get_nonce(address: str) -> int:
    """
    Get transaction nonce for an address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    int
        Current nonce.
    """

    try:
        w3 = get_connection()
        checksum_address = Web3.to_checksum_address(address)
        return w3.eth.get_transaction_count(checksum_address)

    except Exception as error:
        logger.error(f"Error getting nonce: {error}")
        return 0


def get_transaction_count(address: str) -> int:
    """
    Get total transaction count for an address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    int
        Total transaction count.
    """

    return get_nonce(address)


def get_token_balances(address: str) -> list:
    """
    Get token balances for an address.

    Note: This is a placeholder. Full implementation
    would require iterating through token contracts.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    list
        List of token balances.
    """

    try:
        # Placeholder - implement token balance retrieval
        # This would typically involve:
        # 1. Getting all token contracts the address holds
        # 2. Calling balanceOf() on each token contract
        # 3. Returning the list of balances

        return []

    except Exception as error:
        logger.error(f"Error getting token balances: {error}")
        return []