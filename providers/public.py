"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.public

Purpose
-------
Enterprise implementation for public RPC endpoints.

Supports
--------
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

from typing import Any

from core.logger import get_logger

from providers.base import (
    BaseProvider,
    ProviderType,
)
from providers.exceptions import (
    ProviderConfigurationError,
)

logger = get_logger(__name__)


###############################################################################
# Provider Constants
###############################################################################

_BLOCKCHAIN = "ethereum"
_PROVIDER_PREFIX = "public"
_DEFAULT_ENDPOINT = "cloudflare"


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
        endpoint: str = _DEFAULT_ENDPOINT,
        network: str = "mainnet",
    ) -> None:
        """
        Initialize a public RPC provider.

        Parameters
        ----------
        endpoint : str
            Public RPC endpoint.

        network : str
            Blockchain network.
        """

        super().__init__()

        self._endpoint_key = endpoint.lower()
        self._network = network.lower()

        self._http_url: str | None = None

        self._validate_configuration()

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        """
        Provider name.
        """
        return f"{_PROVIDER_PREFIX}-{self._endpoint_key}"

    @property
    def provider(self) -> str:
        """
        Human-readable provider name.
        """
        return f"Public ({self._endpoint_key})"

    @property
    def blockchain(self) -> str:
        """
        Supported blockchain.
        """
        return _BLOCKCHAIN

    @property
    def network(self) -> str:
        """
        Configured blockchain network.
        """
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        """
        Provider type.
        """
        return ProviderType.PUBLIC

    ###########################################################################
    # Endpoint Properties
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        HTTP RPC endpoint.
        """

        if self._http_url is None:

            self._http_url = PUBLIC_ENDPOINTS.get(
                self._endpoint_key,
                PUBLIC_ENDPOINTS[_DEFAULT_ENDPOINT],
            )

        return self._http_url

    @property
    def ws_url(self) -> str:
        """
        WebSocket endpoint.

        Public providers do not expose WebSocket
        endpoints through this implementation.
        """

        return ""

    ###########################################################################
    # Configuration Validation
    ###########################################################################

    def _validate_configuration(
        self,
    ) -> None:
        """
        Validate provider configuration.
        """

        logger.debug(
            "Validating public provider configuration."
        )

        if self._endpoint_key not in PUBLIC_ENDPOINTS:

            raise ProviderConfigurationError(
                f"Unsupported public endpoint: "
                f"{self._endpoint_key}. "
                f"Available: "
                f"{list(PUBLIC_ENDPOINTS.keys())}"
            )

    ###########################################################################
    # Provider Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """
        Whether WebSocket connectivity is available.
        """
        return False

    @property
    def supports_archive(self) -> bool:
        """
        Whether archive data is supported.
        """
        return False

    @property
    def supports_debug_api(self) -> bool:
        """
        Whether the debug namespace is supported.
        """
        return False

    @property
    def supports_trace_api(self) -> bool:
        """
        Whether the trace namespace is supported.
        """
        return False

    ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(
        self,
    ) -> dict[str, Any]:
        """
        Return normalized provider configuration.

        Returns
        -------
        dict[str, Any]
            Provider configuration.
        """

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

    def is_available(
        self,
    ) -> bool:
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

            logger.warning(
                "Public provider unavailable."
            )

            return False

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return enterprise diagnostics.

        Returns
        -------
        dict[str, Any]
            Provider diagnostics.
        """

        return {
            "provider": self.provider,
            "network": self.network,
            "endpoint": self._endpoint_key,
            "status": self.status.value,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "client_version": self.client_version,
            "latency_ms": self.statistics.last_latency_ms,
            "average_latency_ms": (
                self.statistics.average_latency
            ),
            "successful_connections": (
                self.statistics.successful_connections
            ),
            "failed_connections": (
                self.statistics.failed_connections
            ),
            "requests": self.statistics.requests,
            "failed_requests": (
                self.statistics.failed_requests
            ),
        }

    ###########################################################################
    # Enterprise Validation
    ###########################################################################

    def validate(
        self,
    ) -> bool:
        """
        Perform comprehensive provider validation.

        Returns
        -------
        bool
            True if the provider is fully operational.
        """

        logger.info(
            "Validating public provider."
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

            logger.info(
                "Public provider validation successful."
            )

            return True

        except Exception:

            logger.exception(
                "Provider validation failed."
            )

            return False

    ###########################################################################
    # Provider Information
    ###########################################################################

    def provider_summary(
        self,
    ) -> dict[str, Any]:
        """
        Return a concise provider summary.

        Returns
        -------
        dict[str, Any]
            Provider summary.
        """

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

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation.
        """

        return (
            f"{self.provider} "
            f"[{self.network}]"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"endpoint='{self._endpoint_key}', "
            f"status='{self.status.value}')"
        )

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(
        self,
    ) -> None:
        """
        Release provider resources.
        """

        logger.info(
            "Closing public provider."
        )

        super().close()


###############################################################################
# End of File
###############################################################################
