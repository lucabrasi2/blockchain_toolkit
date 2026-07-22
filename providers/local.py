"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.local

Purpose
-------
Enterprise implementation for self-hosted nodes.

Supports:
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
from typing import Any, Dict, Optional

from providers.base import BaseProvider, ProviderType
from providers.exceptions import ProviderConfigurationError
from core.logger import get_logger

logger = get_logger(__name__)


class LocalProvider(BaseProvider):
    """
    Enterprise self-hosted node provider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        http_url: Optional[str] = None,
        ws_url: Optional[str] = None,
        network: str = "mainnet",
        node_type: str = "geth",
    ) -> None:
        super().__init__()

        self._http_url = (
            http_url
            or
            os.getenv("LOCAL_RPC_URL", "http://localhost:8545")
        )

        self._ws_url = (
            ws_url
            or
            os.getenv("LOCAL_WS_URL", "ws://localhost:8546")
        )

        self._network = network.lower()
        self._node_type = node_type.lower()

        self._validate_configuration()

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        return f"local-{self._node_type}"

    @property
    def blockchain(self) -> str:
        return "ethereum"

    @property
    def network(self) -> str:
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LOCAL

    ###########################################################################
    # Endpoint Properties
    ###########################################################################

    @property
    def http_url(self) -> str:
        return self._http_url

    @property
    def ws_url(self) -> str:
        return self._ws_url

    ###########################################################################
    # Configuration Validation
    ###########################################################################

    def _validate_configuration(self) -> None:
        """Validate provider configuration."""
        logger.debug("Validating local node configuration.")

        if not self._http_url:
            raise ProviderConfigurationError(
                "Local node HTTP URL is required."
            )

    ###########################################################################
    # Provider Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """Whether WebSocket connectivity is available."""
        return bool(self._ws_url)

    @property
    def supports_archive(self) -> bool:
        """Whether archive data is supported."""
        return True

    @property
    def supports_debug_api(self) -> bool:
        """Whether debug namespace is available."""
        return True

    @property
    def supports_trace_api(self) -> bool:
        """Whether trace namespace is available."""
        return True

    ###########################################################################
    # Metadata
    ###########################################################################

    @property
    def provider(self) -> str:
        """Provider identifier."""
        return f"Local ({self._node_type})"

    ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(self) -> Dict[str, Any]:
        """Return normalized provider configuration."""
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
        """Determine whether the provider is available."""
        try:
            return self.health_check()
        except Exception as error:
            logger.warning("Local node unavailable: %s", error)
            return False

    def diagnostics(self) -> Dict[str, Any]:
        """Return enterprise diagnostics."""
        return {
            "provider": self.provider,
            "network": self.network,
            "node_type": self._node_type,
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
        logger.info("Validating local node.")

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

            logger.info("Local node validation successful.")
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
        return f"{self.provider} [{self._network}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"node_type='{self._node_type}', "
            f"http_url='{self.http_url}', "
            f"status='{self.status.value}')"
        )

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """Release provider resources."""
        logger.info("Closing local node provider.")
        super().close()


###############################################################################
# End of File
###############################################################################