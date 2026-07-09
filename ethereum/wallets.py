"""
Ethereum wallet functions.
"""

from web3 import Web3

from ethereum.connection import get_connection


def is_valid_address(address: str) -> bool:
    """
    Check whether an Ethereum address is valid.
    """
    return Web3.is_address(address)


def checksum_address(address: str) -> str:
    """
    Convert an address to EIP-55 checksum format.
    """
    return Web3.to_checksum_address(address)


def get_eth_balance(address: str):
    """
    Get the ETH balance of a wallet.
    """

    w3 = get_connection()

    checksum = checksum_address(address)

    balance_wei = w3.eth.get_balance(checksum)

    balance_eth = w3.from_wei(balance_wei, "ether")

    return {
        "wei": balance_wei,
        "ether": balance_eth
    }


def get_nonce(address: str):
    """
    Get the transaction count (nonce).
    """

    w3 = get_connection()

    checksum = checksum_address(address)

    return w3.eth.get_transaction_count(checksum)