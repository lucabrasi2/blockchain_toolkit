"""
providers/base.py

Universal Blockchain Platform (UBP)

Defines the abstract BaseProvider class used by all provider
implementations.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from providers.config import ProviderConfig


class BaseProvider(ABC):
    """
    Abstract base class for all providers.

    This class manages provider configuration, lifecycle,
    statistics, and common functionality.

    Protocol-specific implementations belong in subclasses.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """
        Initialize the provider.
        """

        self._config = config

        # -----------------------------------------------------
        # Connection
        # -----------------------------------------------------

        self._connection: Optional[Any] = None

        self._connected: bool = False

        # -----------------------------------------------------
        # Provider State
        # -----------------------------------------------------

        self._enabled: bool = config.enabled

        self._created_at: datetime = datetime.utcnow()

        self._last_connected_at: Optional[datetime] = None

        self._last_disconnected_at: Optional[datetime] = None

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        self._successful_connections: int = 0

        self._failed_connections: int = 0

        self._successful_requests: int = 0

        self._failed_requests: int = 0

        self._last_success: Optional[datetime] = None

        self._last_failure: Optional[datetime] = None

        self._last_latency: Optional[float] = None

        self._total_latency: float = 0.0

        self._latency_samples: int = 0
            # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def config(self) -> ProviderConfig:
        """Return the provider configuration."""
        return self._config

    @property
    def connection(self) -> Optional[Any]:
        """Return the underlying provider connection."""
        return self._connection

    @property
    def connected(self) -> bool:
        """Return True if the provider is connected."""
        return self._connected

    @property
    def enabled(self) -> bool:
        """Return True if the provider is enabled."""
        return self._enabled

    @property
    def created_at(self) -> datetime:
        """Return the provider creation time."""
        return self._created_at

    @property
    def last_connected_at(self) -> Optional[datetime]:
        """Return the last successful connection time."""
        return self._last_connected_at

    @property
    def last_disconnected_at(self) -> Optional[datetime]:
        """Return the last disconnect time."""
        return self._last_disconnected_at

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    @property
    def successful_connections(self) -> int:
        return self._successful_connections

    @property
    def failed_connections(self) -> int:
        return self._failed_connections

    @property
    def successful_requests(self) -> int:
        return self._successful_requests

    @property
    def failed_requests(self) -> int:
        return self._failed_requests

    @property
    def last_success(self) -> Optional[datetime]:
        return self._last_success

    @property
    def last_failure(self) -> Optional[datetime]:
        return self._last_failure

    @property
    def last_latency(self) -> Optional[float]:
        return self._last_latency

    @property
    def average_latency(self) -> float:
        """
        Return the average request latency.
        """

        if self._latency_samples == 0:
            return 0.0

        return self._total_latency / self._latency_samples

    # ---------------------------------------------------------
    # State Management
    # ---------------------------------------------------------

    def enable(self) -> None:
        """Enable this provider."""
        self._enabled = True

    def disable(self) -> None:
        """Disable this provider."""
        self._enabled = False

    def is_available(self) -> bool:
        """
        Return True if the provider is enabled and connected.
        """

        return self._enabled and self._connected

    # ---------------------------------------------------------
    # Statistics Helpers
    # ---------------------------------------------------------

    def _record_connection_success(self) -> None:
        self._successful_connections += 1
        self._last_connected_at = datetime.utcnow()

    def _record_connection_failure(self) -> None:
        self._failed_connections += 1
        self._last_failure = datetime.utcnow()

    def _record_request_success(self, latency: float) -> None:
        self._successful_requests += 1
        self._last_success = datetime.utcnow()
        self._last_latency = latency
        self._total_latency += latency
        self._latency_samples += 1

    def _record_request_failure(self) -> None:
        self._failed_requests += 1
        self._last_failure = datetime.utcnow()

    # ---------------------------------------------------------
    # Context Manager
    # ---------------------------------------------------------

    def __enter__(self) -> "BaseProvider":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
        # ---------------------------------------------------------
    # Utility Methods
    # ---------------------------------------------------------

    def reconnect(self) -> None:
        """
        Reconnect the provider.
        """

        self.disconnect()
        self.connect()

    def refresh(self) -> None:
        """
        Refresh the provider connection.
        """

        self.reconnect()

    def to_dict(self) -> Dict[str, Any]:
        """
        Return provider information as a dictionary.
        """

        return {
            "provider": self.config.provider,
            "network": self.config.network,
            "connected": self.connected,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_connected_at": (
                self.last_connected_at.isoformat()
                if self.last_connected_at
                else None
            ),
            "last_disconnected_at": (
                self.last_disconnected_at.isoformat()
                if self.last_disconnected_at
                else None
            ),
            "successful_connections": self.successful_connections,
            "failed_connections": self.failed_connections,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "last_latency": self.last_latency,
            "average_latency": self.average_latency,
        }

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"provider={self.config.provider!r}, "
            f"network={self.config.network!r}, "
            f"connected={self.connected}, "
            f"enabled={self.enabled})"
        )

    # ---------------------------------------------------------
    # Abstract Interface
    # ---------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the provider connection.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check whether the provider is healthy.

        Returns
        -------
        bool
            True if the provider is healthy.
        """
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> float:
        """
        Measure provider latency.

        Returns
        -------
        float
            Latency in seconds.
        """
        raise NotImplementedError