"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.tron.provider

Purpose
-------
TRON blockchain provider implementation.

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
from typing import Dict, Any, Optional

from providers.base import BaseProvider
from providers.exceptions import ProviderConfigurationError
from core.logger import get_logger

logger = get_logger(__name__)


class TronProvider(BaseProvider):
    """
    TRON blockchain provider.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        network: str = "mainnet",
    ) -> None:
        super().__init__()

        self._api_key = api_key or os.getenv("TRON_API_KEY", "")
        self._network = network.lower()
        self._http_url: Optional[str] = None
        self._ws_url: Optional[str] = None

        self._validate_configuration()

    @property
    def name(self) -> str:
        return "tron"

    @property
    def blockchain(self) -> str:
        return "tron"

    @property
    def network(self) -> str:
        return self._network

    @property
    def provider_type(self):
        from providers.base import ProviderType
        return ProviderType.CLOUD

    @property
    def http_url(self) -> str:
        if self._http_url is None:
            if self._network == "mainnet":
                self._http_url = "https://api.trongrid.io"
            elif self._network == "shasta":
                self._http_url = "https://api.shasta.trongrid.io"
            elif self._network == "nile":
                self._http_url = "https://nile.trongrid.io"
            else:
                self._http_url = "https://api.trongrid.io"
        return self._http_url

    @property
    def ws_url(self) -> str:
        return ""

    def _validate_configuration(self) -> None:
        """Validate provider configuration."""
        logger.debug("Validating TRON configuration.")

        valid_networks = ["mainnet", "shasta", "nile"]
        if self._network not in valid_networks:
            raise ProviderConfigurationError(
                f"Unsupported TRON network: {self._network}. "
                f"Available: {valid_networks}"
            )

    @property
    def supports_websocket(self) -> bool:
        return False

    @property
    def supports_archive(self) -> bool:
        return True

    @property
    def supports_debug_api(self) -> bool:
        return False

    @property
    def supports_trace_api(self) -> bool:
        return False

    def get_config(self) -> Dict[str, Any]:
        return {
            "provider": "TRON",
            "name": self.name,
            "network": self.network,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
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
            logger.warning(f"TRON provider unavailable: {error}")
            return False

    def validate(self) -> bool:
        logger.info("Validating TRON provider.")

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

            logger.info("TRON provider validation successful.")
            return True

        except Exception as error:
            logger.exception(f"Provider validation failed: {error}")
            return False

    def __str__(self) -> str:
        return f"TRON [{self._network}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"network='{self._network}', "
            f"status='{self.status.value}')"
        )

    def close(self) -> None:
        logger.info("Closing TRON provider.")
        super().close()


###############################################################################
# End of File
###############################################################################
