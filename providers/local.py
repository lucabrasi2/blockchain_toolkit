"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.local

Purpose
-------
Enterprise implementation for self-hosted blockchain nodes.

Supports
--------
• Geth
• Erigon
• Besu
• Nethermind
• Other Ethereum-compatible nodes

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
from providers.exceptions import (
    ProviderConfigurationError,
)

logger = get_logger(__name__)


###############################################################################
# Provider Constants
###############################################################################

_BLOCKCHAIN = "ethereum"
_PROVIDER_PREFIX = "local"

_DEFAULT_HTTP_URL = "http://localhost:8545"
_DEFAULT_WS_URL = "ws://localhost:8546"


class LocalProvider(BaseProvider):
    """
    Enterprise self-hosted blockchain provider.

    Supports Ethereum-compatible execution clients including
    Geth, Erigon, Besu and Nethermind.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        http_url: str | None = None,
        ws_url: str | None = None,
        network: str = "mainnet",
        node_type: str = "geth",
    ) -> None:
        """
        Initialize a local blockchain provider.

        Parameters
        ----------
        http_url : str | None
            HTTP RPC endpoint.

        ws_url : str | None
            WebSocket RPC endpoint.

        network : str
            Blockchain network.

        node_type : str
            Local execution client.
        """

        super().__init__()

        self._http_url = (
            http_url
            or os.getenv(
                "LOCAL_RPC_URL",
                _DEFAULT_HTTP_URL,
            )
        )

        self._ws_url = (
            ws_url
            or os.getenv(
                "LOCAL_WS_URL",
                _DEFAULT_WS_URL,
            )
        )

        self._network = network.lower()
        self._node_type = node_type.lower()

        self._validate_configuration()

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        """
        Provider name.
        """
        return f"{_PROVIDER_PREFIX}-{self._node_type}"

    @property
    def provider(self) -> str:
        """
        Human-readable provider name.
        """
        return f"Local ({self._node_type})"

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
        return ProviderType.LOCAL

    ###########################################################################
    # Endpoint Properties
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        HTTP RPC endpoint.
        """
        return self._http_url

    @property
    def ws_url(self) -> str:
        """
        WebSocket RPC endpoint.
        """
        return self._ws_url

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
            "Validating local node configuration."
        )

        if not self._http_url:

            raise ProviderConfigurationError(
                "Local node HTTP URL is required."
            )

    ###########################################################################
    # Provider Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """
        Whether WebSocket connectivity is available.
        """
        return bool(self._ws_url)

    @property
    def supports_archive(self) -> bool:
        """
        Local nodes support archive mode.
        """
        return True

    @property
    def supports_debug_api(self) -> bool:
        """
        Whether the debug namespace is supported.
        """
        return True

    @property
    def supports_trace_api(self) -> bool:
        """
        Whether the trace namespace is supported.
        """
        return True

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
            "node_type": self._node_type,
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
                "Local node is unavailable."
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
            "node_type": self._node_type,
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

    def validate(self) -> bool:
        """
        Perform comprehensive provider validation.

        Returns
        -------
        bool
            True if the provider is fully operational.
        """

        logger.info(
            "Validating local node provider."
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
                "Local node validation successful."
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
            "node_type": self._node_type,
            "status": self.status.value,
            "available": self.is_available(),
            "http_url": self.http_url,
            "ws_enabled": self.supports_websocket,
        }

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __str__(self) -> str:
        """
        Return a human-readable representation.
        """

        return (
            f"{self.provider} "
            f"[{self.network}]"
        )

    def __repr__(self) -> str:
        """
        Return a developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"node_type='{self._node_type}', "
            f"http_url='{self.http_url}', "
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
            "Closing local node provider."
        )

        super().close()


###############################################################################
# End of File
###############################################################################