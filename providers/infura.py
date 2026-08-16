"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.infura

Purpose
-------
Enterprise implementation of the Infura blockchain provider.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

import os

from typing import Any

from core.logger import get_logger

from providers.base import (
    BaseProvider,
    ProviderType,
)
from providers.config import ProviderConfig
from providers.exceptions import (
    ProviderConfigurationError,
)

logger = get_logger(__name__)


SUPPORTED_NETWORKS = {
    "mainnet",
    "sepolia",
    "holesky",
    "polygon-mainnet",
    "polygon-amoy",
    "arbitrum-mainnet",
    "arbitrum-sepolia",
    "optimism-mainnet",
    "optimism-sepolia",
}


_PROVIDER_NAME = "infura"
_BLOCKCHAIN = "ethereum"


class InfuraProvider(BaseProvider):
    """
    Enterprise Infura provider.
    """

    def __init__(
        self,
        config: ProviderConfig | None = None,
        api_key: str | None = None,
        network: str = "mainnet",
    ) -> None:
        """
        Initialize the Infura provider.

        Parameters
        ----------
        config : ProviderConfig | None
            Provider configuration.

        api_key : str | None
            Infura API key.

        network : str
            Target blockchain network.
        """

        super().__init__()

        if config is not None:
            self._api_key = (
                config.api_key
                or os.getenv("INFURA_API_KEY", "")
            )
            self._network = config.network or "mainnet"
        else:
            self._api_key = (
                api_key
                or os.getenv("INFURA_API_KEY", "")
            )
            self._network = network.lower()

        self._http_url: str | None = None
        self._ws_url: str | None = None

        self._validate_configuration()

    @property
    def name(self) -> str:
        """
        Provider name.
        """
        return _PROVIDER_NAME

    @property
    def blockchain(self) -> str:
        """
        Supported blockchain.
        """
        return _BLOCKCHAIN

    @property
    def network(self) -> str:
        """
        Configured network.
        """
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        """
        Provider type.
        """
        return ProviderType.CLOUD

    @property
    def http_url(self) -> str:
        """
        HTTP endpoint.
        """

        if self._http_url is None:

            if not self._api_key:
                raise ProviderConfigurationError(
                    "Infura API key is required."
                )

            self._http_url = (
                f"https://{self._network}"
                f".infura.io/v3/{self._api_key}"
            )

        return self._http_url

    @property
    def ws_url(self) -> str:
        """
        WebSocket endpoint.
        """

        if self._ws_url is None:

            if not self._api_key:
                return ""

            self._ws_url = (
                f"wss://{self._network}"
                f".infura.io/ws/v3/{self._api_key}"
            )

        return self._ws_url

    def _validate_configuration(
        self,
    ) -> None:
        """
        Validate provider configuration.
        """

        logger.debug(
            "Validating Infura configuration."
        )

        if self._network not in SUPPORTED_NETWORKS:

            raise ProviderConfigurationError(
                f"Unsupported Infura network: "
                f"{self._network}"
            )

        if not self._api_key:

            raise ProviderConfigurationError(
                "Infura API key is required. "
                "Set INFURA_API_KEY "
                "in the environment."
            )

    @property
    def supports_websocket(self) -> bool:
        """
        Whether WebSocket connections are supported.
        """
        return bool(self._api_key)

    @property
    def supports_archive(self) -> bool:
        """
        Whether archive data is supported.
        """
        return False

    @property
    def supports_debug_api(self) -> bool:
        """
        Whether the debug API is supported.
        """
        return False

    @property
    def supports_trace_api(self) -> bool:
        """
        Whether the trace API is supported.
        """
        return False

    def get_config(
        self,
    ) -> dict[str, Any]:
        """
        Return provider configuration.
        """

        return {
            "provider": "Infura",
            "name": self.name,
            "network": self.network,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "api_key": self.masked_api_key,
            "capabilities": {
                "websocket": self.supports_websocket,
                "archive": self.supports_archive,
                "trace": self.supports_trace_api,
                "debug": self.supports_debug_api,
            },
        }

    @property
    def masked_api_key(self) -> str:
        """
        Return the API key in masked form.

        Returns
        -------
        str
            Masked API key.
        """

        if not self._api_key:
            return ""

        if len(self._api_key) <= 8:
            return "********"

        return (
            f"{self._api_key[:4]}"
            f"..."
            f"{self._api_key[-4:]}"
        )

    def is_available(self) -> bool:
        """
        Determine whether the provider is available.

        Returns
        -------
        bool
            True if the provider passes a health check.
        """

        try:
            return self.health_check()

        except Exception:
            logger.exception(
                "Infura provider is unavailable."
            )
            return False

    def validate(self) -> bool:
        """
        Validate the provider configuration and connectivity.

        Returns
        -------
        bool
            True if the provider is fully operational.
        """

        logger.info(
            "Validating Infura provider."
        )

        try:
            self._validate_configuration()

            if not self.health_check():

                logger.error(
                    "Health check failed."
                )

                return False

            if self.chain_id is None:

                logger.error(
                    "Unable to retrieve chain ID."
                )

                return False

            if self.latest_block is None:

                logger.error(
                    "Unable to retrieve latest block."
                )

                return False

            logger.info(
                "Infura provider validation successful."
            )

            return True

        except Exception:

            logger.exception(
                "Provider validation failed."
            )

            return False

    def __str__(self) -> str:
        """
        Return a human-readable representation.
        """

        return f"Infura [{self.network}]"

    def __repr__(self) -> str:
        """
        Return a developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"network='{self.network}', "
            f"status='{self.status.value}')"
        )

    def close(self) -> None:
        """
        Close the provider connection.
        """

        logger.info(
            "Closing Infura provider."
        )

        super().close()


###############################################################################
# End of File
###############################################################################