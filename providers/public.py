"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.public

Purpose
-------
Enterprise implementation for public RPC endpoints.

Supports:
    • Cloudflare Ethereum Gateway
    • Ankr Public RPC
    • PublicNode
    • Other public endpoints

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

from typing import Any, Dict, Optional

from providers.base import BaseProvider, ProviderType
from providers.exceptions import ProviderConfigurationError
from core.logger import get_logger

logger = get_logger(__name__)


###############################################################################
# Public Endpoint Registry
###############################################################################

PUBLIC_ENDPOINTS = {
    "cloudflare": "https://cloudflare-eth.com",
    "ankr": "https://rpc.ankr.com/eth",
    "publicnode": "https://ethereum.publicnode.com",
    "blast": "https://eth-mainnet.public.blastapi.io",
}


class PublicProvider(BaseProvider):
    """
    Enterprise public RPC provider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        endpoint: str = "cloudflare",
        network: str = "mainnet",
    ) -> None:
        super().__init__()

        self._endpoint_key = endpoint.lower()
        self._network = network.lower()
        self._http_url: Optional[str] = None

        self._validate_configuration()

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        return f"public-{self._endpoint_key}"

    @property
    def blockchain(self) -> str:
        return "ethereum"

    @property
    def network(self) -> str:
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.PUBLIC

    ###########################################################################
    # Endpoint Properties
    ###########################################################################

    @property
    def http_url(self) -> str:
        if self._http_url is None:
            self._http_url = PUBLIC_ENDPOINTS.get(
                self._endpoint_key,
                PUBLIC_ENDPOINTS["cloudflare"]
            )
        return self._http_url

    @property
    def ws_url(self) -> str:
        return ""  # Public endpoints typically don't support WebSocket

    ###########################################################################
    # Configuration Validation
    ###########################################################################

    def _validate_configuration(self) -> None:
        """Validate provider configuration."""
        logger.debug("Validating public provider configuration.")

        if self._endpoint_key not in PUBLIC_ENDPOINTS:
            raise ProviderConfigurationError(
                f"Unsupported public endpoint: {self._endpoint_key}. "
                f"Available: {list(PUBLIC_ENDPOINTS.keys())}"
            )

    ###########################################################################
    # Provider Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """Whether WebSocket connectivity is available."""
        return False

    @property
    def supports_archive(self) -> bool:
        """Whether archive data is supported."""
        return False

    @property
    def supports_debug_api(self) -> bool:
        """Whether debug namespace is available."""
        return False

    @property
    def supports_trace_api(self) -> bool:
        """Whether trace namespace is available."""
        return False

    ###########################################################################
    # Metadata
    ###########################################################################

    @property
    def provider(self) -> str:
        """Provider identifier."""
        return f"Public ({self._endpoint_key})"

    ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(self) -> Dict[str, Any]:
        """Return normalized provider configuration."""
        return {
            "provider": self.provider,
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

    ###########################################################################
    # Diagnostics
    ###########################################################################

    def is_available(self) -> bool:
        """Determine whether the provider is available."""
        try:
            return self.health_check()
        except Exception as error:
            logger.warning("Public provider unavailable: %s", error)
            return False

    def diagnostics(self) -> Dict[str, Any]:
        """Return enterprise diagnostics."""
        return {
            "provider": self.provider,
            "network": self.network,
            "endpoint": self._endpoint_key,
            "status": self.status.value,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "client_version": self.client_version,
            "latency_ms": self.statistics.last_latency_ms,
            "average_latency_ms": self.statistics.average_latency,
            "successful_connections": self.statistics.successful_connections,
            "failed_connections": self.statistics.failed_connections,
            "requests": self.statistics.requests,
            "failed_requests": self.statistics.failed_requests,
        }

    ###########################################################################
    # Enterprise Validation
    ###########################################################################

    def validate(self) -> bool:
        """Perform a comprehensive provider validation."""
        logger.info("Validating public provider.")

        try:
            self._validate_configuration()

            if not self.health_check():
                return False

            if self.chain_id is None:
                logger.error("Unable to retrieve chain ID.")
                return False

            logger.info("Public provider validation successful.")
            return True

        except Exception as error:
            logger.exception("Provider validation failed: %s", error)
            return False

    ###########################################################################
    # Provider Information
    ###########################################################################

    def provider_summary(self) -> Dict[str, Any]:
        """Return a concise provider summary."""
        return {
            "provider": self.provider,
            "network": self.network,
            "endpoint": self._endpoint_key,
            "status": self.status.value,
            "available": self.is_available(),
            "http_url": self.http_url,
            "ws_enabled": self.supports_websocket,
        }

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __str__(self) -> str:
        return f"{self.provider} [{self._network}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"endpoint='{self._endpoint_key}', "
            f"status='{self.status.value}')"
        )

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """Release provider resources."""
        logger.info("Closing public provider.")
        super().close()


###############################################################################
# End of File
###############################################################################
