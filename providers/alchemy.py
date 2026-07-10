"""
Alchemy Provider.
"""

from web3 import Web3

from providers.base import BaseProvider

from config.settings import (
    ALCHEMY_HTTP_URL,
    validate_settings,
)


class AlchemyProvider(BaseProvider):

    def __init__(self):

        validate_settings()

        self.w3 = Web3(
            Web3.HTTPProvider(ALCHEMY_HTTP_URL)
        )

    def connect(self):

        return self.w3

    def is_connected(self):

        return self.w3.is_connected()

    def get_web3(self):

        return self.w3