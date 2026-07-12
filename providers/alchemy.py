"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Alchemy Provider
Author  : jaramogi Diddy

Provides Ethereum connectivity through the Alchemy API.
"""

from web3 import Web3

from config.settings import (
    ALCHEMY_HTTP_URL,
    validate_settings,
)

from providers.base import BaseProvider

from exceptions.blockchain_exceptions import (
    BlockchainConnectionError,
)

from core.logger import get_logger


logger = get_logger(__name__)


class AlchemyProvider(BaseProvider):
    """
    Ethereum provider backed by Alchemy.
    """

    def __init__(self):
        """
        Initialize the provider.
        """
        validate_settings()

        self._web3 = None

    def connect(self) -> None:
        """
        Establish a connection to Alchemy.
        """

        logger.info("Connecting to Alchemy provider...")

        self._web3 = Web3(
            Web3.HTTPProvider(ALCHEMY_HTTP_URL)
        )

        if not self._web3.is_connected():

            logger.error("Alchemy connection failed.")

            raise BlockchainConnectionError(
                "Unable to connect to the Alchemy provider."
            )

        logger.info("Connected to Alchemy successfully.")

    def is_connected(self) -> bool:
        """
        Check whether the provider is connected.
        """

        if self._web3 is None:
            return False

        return self._web3.is_connected()

    def get_web3(self) -> Web3:
        """
        Return the active Web3 instance.
        """

        if self._web3 is None:
            self.connect()

        return self._web3