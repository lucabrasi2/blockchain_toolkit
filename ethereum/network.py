"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Ethereum Network Intelligence
Author  : Jaramogi Diddy

Description
-----------
Provides blockchain intelligence for the active
Ethereum network.

Responsibilities
----------------
• Connection status
• Chain ID
• Network identification
• Latest block retrieval
• Client version
• Current gas price
• Network summary generation

This module intentionally contains NO business
logic.

Business logic belongs in:

    services/ethereum/network_service.py

The controller layer should never access this
module directly.
"""

from __future__ import annotations

from web3 import Web3

from ethereum.connection import get_connection

from core.logger import get_logger


logger = get_logger(__name__)
###############################################################################
# Supported Ethereum Networks
###############################################################################

NETWORK_NAMES = {

    1: "Ethereum Mainnet",

    5: "Goerli",

    11155111: "Sepolia",

    17000: "Holesky",

}
###############################################################################
# Internal Helpers
###############################################################################

def _web3() -> Web3:
    """
    Return the active Web3 connection.

    Returns
    -------
    Web3
        Active blockchain connection.
    """

    return get_connection()
###############################################################################
# Network Intelligence
###############################################################################

def is_connected() -> bool:
    """
    Determine whether the blockchain provider
    is connected.

    Returns
    -------
    bool
        True if connected.
    """

    logger.info(
        "Checking blockchain connection."
    )

    connected = (
        _web3().is_connected()
    )

    logger.info(
        "Blockchain connection check completed."
    )

    return connected


def get_chain_id() -> int:
    """
    Retrieve the blockchain Chain ID.

    Returns
    -------
    int
        Ethereum Chain ID.
    """

    logger.info(
        "Retrieving blockchain Chain ID."
    )

    chain_id = (
        _web3().eth.chain_id
    )

    logger.info(
        "Blockchain Chain ID retrieved successfully."
    )

    return chain_id


def get_network_name() -> str:
    """
    Determine the blockchain network.

    Returns
    -------
    str
        Human-readable network name.
    """

    logger.info(
        "Determining blockchain network."
    )

    chain_id = get_chain_id()

    network = NETWORK_NAMES.get(
        chain_id,
        f"Unknown ({chain_id})",
    )

    logger.info(
        "Blockchain network determined successfully."
    )

    return network
###############################################################################
# Blockchain Intelligence
###############################################################################

def get_latest_block() -> int:
    """
    Retrieve the latest block number.

    Returns
    -------
    int
        Latest Ethereum block.
    """

    logger.info(
        "Retrieving latest block."
    )

    latest_block = (
        _web3().eth.block_number
    )

    logger.info(
        "Latest block retrieved successfully."
    )

    return latest_block


def get_client_version() -> str:
    """
    Retrieve the blockchain client version.

    Returns
    -------
    str
        Ethereum client version.
    """

    logger.info(
        "Retrieving blockchain client version."
    )

    client = (
        _web3().client_version
    )

    logger.info(
        "Blockchain client version retrieved successfully."
    )

    return client


def get_gas_price() -> float:
    """
    Retrieve the current gas price.

    Returns
    -------
    float
        Current gas price in Gwei.
    """

    logger.info(
        "Retrieving current gas price."
    )

    gas_price = (
        _web3().eth.gas_price
    )

    gas_price_gwei = (
        gas_price / 1_000_000_000
    )

    logger.info(
        "Gas price retrieved successfully."
    )

    return gas_price_gwei
###############################################################################
# Network Summary
###############################################################################

def get_network_information() -> dict:
    """
    Retrieve complete Ethereum network
    information.

    Returns
    -------
    dict
        Complete network report.
    """
def get_network_information() -> dict:
    """
    Retrieve complete Ethereum network
    information.

    Returns
    -------
    dict
        Complete Ethereum network report.
    """

    logger.info(
        "Retrieving complete network information."
    )

    information = {

        "connected":
            is_connected(),

        "chain_id":
            get_chain_id(),

        "network_name":
            get_network_name(),

        "latest_block":
            get_latest_block(),

        "gas_price_gwei":
            get_gas_price(),

        "client_version":
            get_client_version(),

    }

    logger.info(
        "Complete network information retrieved successfully."
    )

    return information
    
__all__ = [

    "is_connected",

    "get_chain_id",

    "get_network_name",

    "get_latest_block",

    "get_client_version",

    "get_gas_price",

    "get_network_information",

]