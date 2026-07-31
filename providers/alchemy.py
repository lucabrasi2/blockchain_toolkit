"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.alchemy

Purpose
-------
Enterprise implementation of the Alchemy blockchain provider.

Responsibilities
----------------
• Build Alchemy RPC endpoints
• Validate configuration
• Expose provider metadata
• Provide Web3 connectivity
• Report provider capabilities
• Integrate with ProviderManager

This module intentionally contains NO blockchain business logic.

Business logic belongs in:

    services/

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


###############################################################################
# Supported Networks
###############################################################################

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
    "base-mainnet",
    "base-sepolia",
    "zksync-mainnet",
    "zksync-sepolia",
}

# Network mapping for Alchemy URLs
ALCHEMY_NETWORK_MAP = {
    "mainnet": "eth-mainnet",
    "sepolia": "eth-sepolia",
    "holesky": "eth-holesky",
    "polygon-mainnet": "polygon-mainnet",
    "polygon-amoy": "polygon-amoy",
    "arbitrum-mainnet": "arb-mainnet",
    "arbitrum-sepolia": "arb-sepolia",
    "optimism-mainnet": "opt-mainnet",
    "optimism-sepolia": "opt-sepolia",
    "base-mainnet": "base-mainnet",
    "base-sepolia": "base-sepolia",
    "zksync-mainnet": "zksync-mainnet",
    "zksync-sepolia": "zksync-sepolia",
}


###############################################################################
# Alchemy Provider
###############################################################################


class AlchemyProvider(BaseProvider):
    """
    Enterprise Alchemy provider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: Optional[ProviderConfig] = None,
        api_key: Optional[str] = None,
        network: str = "mainnet",
    ) -> None:
        super().__init__()

        # If config is provided, use it
        if config:
            self._api_key = config.api_key or os.getenv("ALCHEMY_API_KEY", "")
            self._network = config.network or "mainnet"
        else:
            self._api_key = api_key or os.getenv("ALCHEMY_API_KEY", "")
            self._network = network.lower()

        # Get Alchemy network name for URL
        self._alchemy_network = ALCHEMY_NETWORK_MAP.get(self._network, "eth-mainnet")

        self._http_url: Optional[str] = None
        self._ws_url: Optional[str] = None

        self._validate_configuration()

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        return "alchemy"

    @property
    def blockchain(self) -> str:
        return "ethereum"

    @property
    def network(self) -> str:
        return self._network

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CLOUD

    ###########################################################################
    # Endpoint Construction
    ###########################################################################

    @property
    def http_url(self) -> str:
        if self._http_url is None:
            key = self._api_key if self._api_key else "demo"
            self._http_url = f"https://{self._alchemy_network}.g.alchemy.com/v2/{key}"
        return self._http_url

    @property
    def ws_url(self) -> str:
        if self._ws_url is None:
            if not self._api_key:
                return ""
            self._ws_url = f"wss://{self._alchemy_network}.g.alchemy.com/v2/{self._api_key}"
        return self._ws_url

    ###########################################################################
    # Configuration Validation
    ###########################################################################

    def _validate_configuration(self) -> None:
        """Validate provider configuration."""
        logger.debug("Validating Alchemy configuration.")

        if self._network not in SUPPORTED_NETWORKS:
            raise ProviderConfigurationError(
                f"Unsupported Alchemy network: {self._network}"
            )

    ###########################################################################
    # Provider Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """Whether WebSocket connectivity is available."""
        return bool(self._api_key)

    @property
    def supports_archive(self) -> bool:
        """Whether archive data is supported."""
        return True

    @property
    def supports_debug_api(self) -> bool:
        """Whether debug namespace may be available."""
        return True

    @property
    def supports_trace_api(self) -> bool:
        """Whether trace namespace may be available."""
        return True

    ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(self) -> Dict[str, Any]:
        """Return normalized provider configuration."""
        return {
            "provider": "Alchemy",
            "name": self.name,
            "network": self.network,
            "alchemy_network": self._alchemy_network,
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

    ###########################################################################
    # Metadata
    ###########################################################################

    @property
    def masked_api_key(self) -> str:
        """Secure API key representation."""
        if not self._api_key:
            return ""
        if len(self._api_key) <= 8:
            return "********"
        return self._api_key[:4] + "..." + self._api_key[-4:]

    ###########################################################################
    # Diagnostics
    ###########################################################################

    def is_available(self) -> bool:
        """Determine whether the provider is available."""
        try:
            return self.health_check()
        except Exception as error:
            logger.warning(f"Alchemy provider unavailable: {error}")
            return False

    def diagnostics(self) -> Dict[str, Any]:
        """Return enterprise diagnostics."""
        return {
            "provider": "Alchemy",
            "network": self.network,
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
        logger.info("Validating Alchemy provider.")

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

            logger.info("Alchemy provider validation successful.")
            return True

        except Exception as error:
            logger.exception("Provider validation failed: %s", error)
            return False

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __str__(self) -> str:
        return f"Alchemy [{self._network}]"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"network='{self._network}', "
            f"status='{self.status.value}')"
        )

    ###########################################################################
    # Extension Hooks
    ###########################################################################

    def before_request(self) -> None:
        """Executed immediately before every RPC request."""
        logger.debug("Executing pre-request hook.")

    def after_request(self, successful: bool = True) -> None:
        """Executed after every RPC request."""
        super().after_request(successful)
        logger.debug("Executing post-request hook.")

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """Release provider resources."""
        logger.info("Closing Alchemy provider.")
        super().close()


###############################################################################
# End of File
###############################################################################