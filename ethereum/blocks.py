"""
Ethereum Block Service

Provides functions for retrieving block information.
"""

from ethereum.connection import get_connection


def get_latest_block():
    """
    Return the latest Ethereum block.

    Returns:
        AttributeDict: Latest block information.
    """

    w3 = get_connection()

    return w3.eth.get_block("latest")


def get_block_by_number(block_number: int):
    """
    Return a block using its block number.

    Args:
        block_number (int): Block height.

    Returns:
        AttributeDict: Block information.
    """

    w3 = get_connection()

    return w3.eth.get_block(block_number)
