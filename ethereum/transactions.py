"""
Ethereum Transaction Service

Purpose:
    Provides reusable transaction-related services for the
    Universal Blockchain Platform (UBP).

Responsibilities:
    - Retrieve transaction details
    - Retrieve transaction receipts
"""

from ethereum.connection import get_connection


def get_transaction(tx_hash: str):
    """
    Retrieve a transaction by its hash.

    Args:
        tx_hash (str): Transaction hash.

    Returns:
        AttributeDict: Transaction details.
    """

    w3 = get_connection()

    return w3.eth.get_transaction(tx_hash)


def get_transaction_receipt(tx_hash: str):
    """
    Retrieve a transaction receipt.

    Args:
        tx_hash (str): Transaction hash.

    Returns:
        AttributeDict: Transaction receipt.
    """

    w3 = get_connection()

    return w3.eth.get_transaction_receipt(tx_hash)