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
from typing import Any, Dict, Optional

from providers.base import BaseProvider, ProviderType
from providers.config import ProviderConfig
from providers.exceptions import ProviderConfigurationError
from core.logger import get_logger

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


class InfuraProvider(BaseProvider):
    """
    Enterprise Infura provider.
    """

    def __init__(
        self,
        config: Optional[ProviderConfig] = None,
        api_key: Optional[str] = None,
        network: str = "mainnet",
    ) -> None:
        super().__init__()

        if config:
            self._api_key = config.api_key or os.getenv("INFURA_API_KEY", "")
            self._network = config.network or "mainnet"
        else:
            self._api_key = api_key or os.getenv("INFURA_API_KEY", "")
            self._network = network.lower()

        self._http_url: Optional[str] = None
        self._ws_url: Optional[str] = None

        self._validate_configuration()

    @property
    def name(self) -> str:
        return "infura"

    @property
    def blockchain(self) -> str:
        return "ethereum"

    @property
    def network(self) -> str:
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CLOUD

    @property
    def http_url(self) -> str:
        if self._http_url is None:
            if not self._api_key:
                raise ProviderConfigurationError("Infura API key is required.")
            self._http_url = f"https://{self._network}.infura.io/v3/{self._api_key}"
        return self._http_url

    @property
    def ws_url(self) -> str:
        if self._ws_url is None:
            if not self._api_key:
                return ""
            self._ws_url = f"wss://{self._network}.infura.io/ws/v3/{self._api_key}"
        return self._ws_url

    def _validate_configuration(self) -> None:
        logger.debug("Validating Infura configuration.")

        if self._network not in SUPPORTED_NETWORKS:
            raise ProviderConfigurationError(
                f"Unsupported Infura network: {self._network}"
            )

        if not self._api_key:
            raise ProviderConfigurationError(
                "Infura API key is required. Set INFURA_API_KEY in environment."
            )

    @property
    def supports_websocket(self) -> bool:
        return bool(self._api_key)

    @property
    def supports_archive(self) -> bool:
        return False

    @property
    def supports_debug_api(self) -> bool:
        return False

    @property
    def supports_trace_api(self) -> bool:
        return False

    def get_config(self) -> Dict[str, Any]:
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
        if not self._api_key:
            return ""
        if len(self._api_key) <= 8:
            return "********"
        return self._api_key[:4] + "..." + self._api_key[-4:]

    def is_available(self) -> bool:
        try:
            return self.health_check()
        except Exception as error:
            logger.warning(f"Infura provider unavailable: {error}")
            return False

    def validate(self) -> bool:
        logger.info("Validating Infura provider.")

        try:
            self._validate_configuration()

            if not self.health_check():
                return False

            if self.chain_id is None:
                logger.error("Unable to retrieve chain ID.")
                return False

            if self.latest_block is None:
                logger.error("Unable to retrieve latest block.")
                return False

            logger.info("Infura provider validation successful.")
            return True

        except Exception as error:
            logger.exception("Provider validation failed: %s", error)
            return False

    def __str__(self) -> str:
        return f"Infura [{self._network}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"network='{self._network}', "
            f"status='{self.status.value}')"
        )

    def close(self) -> None:
        logger.info("Closing Infura provider.")
        super().close()


###############################################################################
# End of File
###############################################################################