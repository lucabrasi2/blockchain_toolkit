"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Ethereum Network
Author  : Jaramogi Diddy

Provides Ethereum network information.
"""

from providers.factory import ProviderFactory
from core.logger import get_logger

logger = get_logger(__name__)


def _get_web3():
    """
    Return the active Web3 instance.
    """

    provider = ProviderFactory.get_provider()

    return provider.get_web3()


def get_network_information():
    """
    Retrieve Ethereum network information.
    """

    logger.info("Retrieving Ethereum network information.")

    w3 = _get_web3()

    return {
        "connected": w3.is_connected(),
        "chain_id": w3.eth.chain_id,
        "latest_block": w3.eth.block_number,
        "gas_price_gwei": float(
            w3.from_wei(
                w3.eth.gas_price,
                "gwei",
            )
        ),
        "client_version": w3.client_version,
    }