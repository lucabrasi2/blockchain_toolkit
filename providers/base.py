"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.base

Purpose
-------
Enterprise abstraction layer for all blockchain connectivity providers.

This module defines the contract that every blockchain provider must implement,
regardless of blockchain or infrastructure vendor.

Supported examples include:
    • Alchemy
    • Infura
    • QuickNode
    • Chainstack
    • Ankr
    • GetBlock
    • Blast
    • Tenderly
    • Self-hosted Geth
    • Self-hosted Erigon
    • Self-hosted Besu
    • Bitcoin Core
    • Bitcoin Knots
    • ElectrumX
    • TRON FullNode
    • Solana RPC
    • XRPL
    • Hyperledger Fabric

This module intentionally contains NO blockchain-specific business logic.

Business logic belongs inside the appropriate service layer.

Architecture
------------
UBP Enterprise Connectivity Framework

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

import time
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Optional

from web3 import Web3

from core.logger import get_logger

logger = get_logger(__name__)


###############################################################################
# Enumerations
###############################################################################


class ProviderStatus(str, Enum):
    """
    Provider health status.
    """

    UNKNOWN = "UNKNOWN"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"


class ProviderType(str, Enum):
    """
    Infrastructure type.
    """

    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    ENTERPRISE = "ENTERPRISE"


###############################################################################
# Provider Statistics
###############################################################################


@dataclass(slots=True)
class ProviderStatistics:
    """
    Runtime statistics for provider health.

    These statistics are maintained automatically
    by BaseProvider.
    """

    successful_connections: int = 0
    failed_connections: int = 0
    reconnect_attempts: int = 0
    requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    last_latency_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    uptime_started: Optional[datetime] = None

    @property
    def average_latency(self) -> float:
        """
        Return average latency.
        """
        if self.successful_connections == 0:
            return 0.0

        return (
            self.total_latency_ms /
            self.successful_connections
        )


###############################################################################
# Provider Metadata
###############################################################################


@dataclass(slots=True)
class ProviderMetadata:
    """
    Immutable provider metadata.
    """

    provider_name: str
    blockchain: str
    network: str
    provider_type: ProviderType
    supports_http: bool = True
    supports_websocket: bool = True
    supports_batch_requests: bool = True
    supports_subscriptions: bool = True
    supports_archive: bool = False
    supports_tracing: bool = False
    supports_debug_api: bool = False


###############################################################################
# Base Provider
###############################################################################


class BaseProvider(ABC):
    """
    Enterprise base class for every UBP provider.

    Responsibilities
    ----------------

    * Connection lifecycle
    * Health monitoring
    * Latency measurement
    * Runtime statistics
    * Metadata exposure
    * Connection caching

    Child classes provide ONLY endpoint construction.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:

        self._web3: Optional[Web3] = None
        self._status = ProviderStatus.UNKNOWN
        self._statistics = ProviderStatistics()
        self._connected_since: Optional[datetime] = None
        self._last_health_check: Optional[datetime] = None

        logger.debug(
            "%s initialized.",
            self.__class__.__name__,
        )

    ###########################################################################
    # Required Provider Properties
    ###########################################################################

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def blockchain(self) -> str:
        """
        Blockchain supported.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def network(self) -> str:
        """
        Network name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """
        Infrastructure type.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def http_url(self) -> str:
        """
        HTTP endpoint.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def ws_url(self) -> str:
        """
        WebSocket endpoint.
        """
        raise NotImplementedError

    ###########################################################################
    # Provider Configuration
    ###########################################################################

    @abstractmethod
    def get_config(self) -> dict[str, Any]:
        """
        Return provider configuration.

        Child implementations may extend this.
        """
        raise NotImplementedError

    ###########################################################################
    # Metadata
    ###########################################################################

    @property
    def metadata(self) -> ProviderMetadata:
        """
        Standard provider metadata.
        """
        return ProviderMetadata(
            provider_name=self.name,
            blockchain=self.blockchain,
            network=self.network,
            provider_type=self.provider_type,
            supports_http=True,
            supports_websocket=bool(self.ws_url),
        )

    ###########################################################################
    # Connection Management
    ###########################################################################

    def connect(self) -> Web3:
        """
        Create or reuse a Web3 connection.
        """
        if (
            self._web3 is not None
            and
            self._web3.is_connected()
        ):
            return self._web3

        logger.info(
            "Connecting to %s...",
            self.name,
        )

        start = time.perf_counter()

        provider = Web3.HTTPProvider(self.http_url)
        web3 = Web3(provider)

        try:
            connected = web3.is_connected()
        except Exception as error:
            logger.exception("Connection raised an exception: %s", error)
            self._statistics.failed_connections += 1
            self._statistics.last_failure = datetime.utcnow()
            self._status = ProviderStatus.OFFLINE
            raise ConnectionError(f"Unable to connect to {self.name}") from error

        if not connected:
            logger.error("Connection failed using URL: %s", self.http_url)
            self._statistics.failed_connections += 1
            self._statistics.last_failure = datetime.utcnow()
            self._status = ProviderStatus.OFFLINE
            raise ConnectionError(f"Unable to connect to {self.name}")

        latency = (time.perf_counter() - start) * 1000

        self._statistics.successful_connections += 1
        self._statistics.last_latency_ms = latency
        self._statistics.total_latency_ms += latency
        self._statistics.last_success = datetime.utcnow()
        self._connected_since = datetime.utcnow()
        self._statistics.uptime_started = self._connected_since
        self._status = ProviderStatus.ONLINE
        self._web3 = web3

        logger.info(
            "%s connected (%.2f ms)",
            self.name,
            latency,
        )

        return self._web3

    ###########################################################################
    # Connection Lifecycle
    ###########################################################################

    def disconnect(self) -> None:
        """
        Disconnect the provider.

        Web3 itself has no explicit disconnect API for HTTP providers,
        therefore disconnecting simply releases the cached instance.
        """
        logger.info("Disconnecting provider %s.", self.name)
        self._web3 = None
        self._status = ProviderStatus.UNKNOWN
        self._connected_since = None

    def reconnect(self) -> Web3:
        """
        Force a fresh connection.

        Returns
        -------
        Web3
            Active Web3 instance.
        """
        logger.info("Reconnecting provider %s.", self.name)
        self._statistics.reconnect_attempts += 1
        self.disconnect()
        return self.connect()

    def refresh(self) -> Web3:
        """
        Refresh the current connection.

        Alias of reconnect() for readability.
        """
        return self.reconnect()

    ###########################################################################
    # Web3 Access
    ###########################################################################

    @property
    def web3(self) -> Web3:
        """
        Return an active Web3 instance.

        Automatically connects if necessary.
        """
        if self._web3 is None:
            self.connect()
        return self._web3

    ###########################################################################
    # Health Monitoring
    ###########################################################################

    def health_check(self) -> bool:
        """
        Perform a complete provider health check.

        Returns
        -------
        bool
            True if healthy.
        """
        logger.debug("Running provider health check.")
        self._last_health_check = datetime.utcnow()

        try:
            connected = self.web3.is_connected()
            if not connected:
                self._status = ProviderStatus.OFFLINE
                return False

            # Execute a lightweight RPC request.
            self.web3.eth.block_number
            self._status = ProviderStatus.ONLINE
            return True

        except Exception as error:
            logger.exception("Health check failed: %s", error)
            self._status = ProviderStatus.OFFLINE
            return False

    def is_available(self) -> bool:
        """
        Determine whether this provider is currently usable.
        """
        return self.health_check()

    ###########################################################################
    # Diagnostics
    ###########################################################################

    @property
    def chain_id(self) -> Optional[int]:
        """
        Connected chain ID.
        """
        try:
            return self.web3.eth.chain_id
        except Exception:
            return None

    @property
    def latest_block(self) -> Optional[int]:
        """
        Latest block number.
        """
        try:
            return self.web3.eth.block_number
        except Exception:
            return None

    @property
    def client_version(self) -> Optional[str]:
        """
        Ethereum client version.
        """
        try:
            return self.web3.client_version
        except Exception:
            return None

    @property
    def is_syncing(self) -> bool:
        """
        Sync status.
        """
        try:
            syncing = self.web3.eth.syncing
            return bool(syncing)
        except Exception:
            return False

    ###########################################################################
    # Statistics
    ###########################################################################

    @property
    def statistics(self) -> ProviderStatistics:
        """
        Runtime statistics.
        """
        return self._statistics

    @property
    def status(self) -> ProviderStatus:
        """
        Provider status.
        """
        return self._status

    @property
    def uptime_seconds(self) -> float:
        """
        Provider uptime.

        Returns
        -------
        float
            Seconds connected.
        """
        if self._connected_since is None:
            return 0.0

        return (
            datetime.utcnow() -
            self._connected_since
        ).total_seconds()

    ###########################################################################
    # Request Accounting
    ###########################################################################

    def record_request(self, successful: bool = True) -> None:
        """
        Record provider request statistics.
        """
        self._statistics.requests += 1
        if not successful:
            self._statistics.failed_requests += 1

    @property
    def success_rate(self) -> float:
        """
        Provider request success rate.
        """
        requests = self._statistics.requests
        if requests == 0:
            return 100.0

        failures = self._statistics.failed_requests
        return ((requests - failures) / requests) * 100.0

    ###########################################################################
    # Provider Information
    ###########################################################################

    def get_provider_info(self) -> dict[str, Any]:
        """
        Enterprise provider information.

        This method intentionally returns a
        normalized structure used throughout UBP.
        """
        return {
            "name": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider_type": self.provider_type.value,
            "status": self.status.value,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "client_version": self.client_version,
            "syncing": self.is_syncing,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "uptime_seconds": self.uptime_seconds,
            "statistics": {
                "successful_connections": self.statistics.successful_connections,
                "failed_connections": self.statistics.failed_connections,
                "reconnect_attempts": self.statistics.reconnect_attempts,
                "requests": self.statistics.requests,
                "failed_requests": self.statistics.failed_requests,
                "average_latency_ms": self.statistics.average_latency,
                "last_latency_ms": self.statistics.last_latency_ms,
            },
        }

    ###########################################################################
    # Diagnostics Utilities
    ###########################################################################

    def ping(self) -> float:
        """
        Measure provider latency.

        Returns
        -------
        float
            Round-trip latency in milliseconds.

        Raises
        ------
        ConnectionError
            If the provider cannot be reached.
        """
        logger.debug("Pinging provider %s.", self.name)

        start = time.perf_counter()
        self.web3.eth.block_number
        latency = (time.perf_counter() - start) * 1000

        self._statistics.last_latency_ms = latency
        self._statistics.total_latency_ms += latency

        return latency

    def validate_endpoint(self) -> bool:
        """
        Validate the configured RPC endpoint.

        Returns
        -------
        bool
            True if reachable.
        """
        try:
            return self.health_check()
        except Exception:
            return False

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize provider information.

        Returns
        -------
        dict
            Provider representation.
        """
        return self.get_provider_info()

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __str__(self) -> str:
        """
        Human-readable provider.
        """
        return f"{self.name} ({self.network})"

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"blockchain='{self.blockchain}', "
            f"network='{self.network}', "
            f"status='{self.status.value}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseProvider):
            return False

        return (
            self.name == other.name
            and
            self.blockchain == other.blockchain
            and
            self.network == other.network
        )

    def __hash__(self) -> int:
        return hash((self.name, self.blockchain, self.network))

    ###########################################################################
    # Extension Hooks
    ###########################################################################

    def before_request(self) -> None:
        """
        Hook executed immediately before an RPC request.

        Child providers may override this for:
        • rate limiting
        • authentication refresh
        • metrics
        • tracing
        • request signing

        Default implementation intentionally performs no action.
        """
        return

    def after_request(self, successful: bool = True) -> None:
        """
        Hook executed after every RPC request.
        """
        self.record_request(successful)

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """
        Release provider resources.
        """
        logger.info("Closing provider %s.", self.name)
        self.disconnect()

    def __enter__(self) -> BaseProvider:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


###############################################################################
# End of File
###############################################################################