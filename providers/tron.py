"""
providers/tron.py

Universal Blockchain Platform (UBP)

TRON REST provider implementation.
"""

from __future__ import annotations

from providers.config import ProviderConfig
from providers.rest_provider import RestProvider


class TronProvider(RestProvider):
    """
    TRON provider using the TronGrid REST API.
    """

    DEFAULT_MAINNET = "https://api.trongrid.io"
    DEFAULT_SHASTA = "https://api.shasta.trongrid.io"
    DEFAULT_NILE = "https://nile.trongrid.io"

    def __init__(self, config: ProviderConfig) -> None:
        """
        Initialize the TRON provider.
        """

        if not config.endpoint:
            network = config.network.lower()

            if network == "mainnet":
                config.endpoint = self.DEFAULT_MAINNET
            elif network == "shasta":
                config.endpoint = self.DEFAULT_SHASTA
            elif network == "nile":
                config.endpoint = self.DEFAULT_NILE
            else:
                config.endpoint = self.DEFAULT_MAINNET

        super().__init__(config)

        # TronGrid API key (optional)
        if config.api_key:
            self.headers["TRON-PRO-API-KEY"] = config.api_key

    @property
    def provider_name(self) -> str:
        """
        Return the provider name.
        """

        return "tron"

    @property
    def network(self) -> str:
        """
        Return the configured network.
        """

        return self.config.network

    def get_latest_block(self) -> dict:
        """
        Retrieve the latest TRON block.
        """

        return self._request(
            "GET",
            "/wallet/getnowblock",
        )

    def get_block(self, block_number: int) -> dict:
        """
        Retrieve a block by height.
        """

        return self._request(
            "POST",
            "/wallet/getblockbynum",
            json={
                "num": block_number,
            },
        )

    def get_account(self, address: str) -> dict:
        """
        Retrieve account information.
        """

        return self._request(
            "POST",
            "/wallet/getaccount",
            json={
                "address": address,
                "visible": True,
            },
        )

    def to_dict(self) -> dict:
        """
        Serialize provider information.
        """

        data = super().to_dict()

        data.update(
            {
                "provider": self.provider_name,
                "network": self.network,
            }
        )

        return data

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"network={self.network!r}, "
            f"connected={self.connected})"
        )
