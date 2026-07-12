"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Ethereum Wallet Functions
Author  : Jaramogi Diddy

Provides wallet-related blockchain operations.
"""

from web3 import Web3

from providers.factory import ProviderFactory
from core.logger import get_logger

logger = get_logger(__name__)


def _get_web3():
    """
    Return the active Web3 instance.
    """

    provider = ProviderFactory.get_provider()

    return provider.get_web3()


def is_valid_address(address: str) -> bool:
    """
    Validate an Ethereum address.
    """

    logger.info("Validating Ethereum address.")

    return Web3.is_address(address)


def checksum_address(address: str) -> str:
    """
    Convert an address to EIP-55 checksum format.
    """

    return Web3.to_checksum_address(address)


def get_eth_balance(address: str) -> dict:
    """
    Return ETH balance.
    """

    logger.info("Retrieving wallet balance.")

    w3 = _get_web3()

    checksum = checksum_address(address)

    balance_wei = w3.eth.get_balance(checksum)

    balance_eth = w3.from_wei(balance_wei, "ether")

    logger.info("Wallet balance retrieved successfully.")

    return {
        "wei": balance_wei,
        "ether": balance_eth,
    }


def get_nonce(address: str) -> int:
    """
    Return wallet nonce.
    """

    logger.info("Retrieving wallet nonce.")

    w3 = _get_web3()

    checksum = checksum_address(address)

    nonce = w3.eth.get_transaction_count(checksum)

    logger.info("Wallet nonce retrieved successfully.")

    return nonce