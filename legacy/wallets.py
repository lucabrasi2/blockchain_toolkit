"""
Wallet-related blockchain functions.
"""

from web3 import Web3
from blockchain.connection import get_connection


def is_valid_address(address: str) -> bool:
    """
    Check whether an Ethereum address is valid.
    """
    return Web3.is_address(address)


def get_eth_balance(address: str):
    """
    Return the ETH balance of a wallet.
    """

    w3 = get_connection()

    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, "ether")

    return {
        "wei": balance_wei,
        "ether": balance_eth
    }


def get_transaction_count(address: str):
    """
    Return the wallet nonce.
    """

    w3 = get_connection()

    return w3.eth.get_transaction_count(address)