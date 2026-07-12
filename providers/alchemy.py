"""
Alchemy Provider

Provides a Web3 connection using Alchemy.
"""

from web3 import Web3

from config.settings import (
    ALCHEMY_HTTP_URL,
    validate_settings,
)

from providers.base import BaseProvider

from exceptions.blockchain_exceptions import (
    ProviderConnectionError,
    ConfigurationError,
)


class AlchemyProvider(BaseProvider):
    """
    Ethereum provider using Alchemy.
    """

    def __init__(self):
        validate_settings()

        self._web3 = None

    def connect(self):
        """
        Establish a Web3 connection.
        """

        try:
            self._web3 = Web3(
                Web3.HTTPProvider(ALCHEMY_HTTP_URL)
            )

            if not self._web3.is_connected():
                raise ProviderConnectionError(
                    "Unable to connect to the Alchemy provider."
                )

            return self._web3

        except Exception as error:
            raise ConfigurationError(str(error))

    def is_connected(self):
        """
        Check provider connectivity.
        """

        if self._web3 is None:
            return False

        return self._web3.is_connected()

    def get_web3(self):
        """
        Return the active Web3 connection.
        """

        if self._web3 is None:
            self.connect()

        return self._web3