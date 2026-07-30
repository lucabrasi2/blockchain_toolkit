"""
providers/config.py

Universal Blockchain Platform (UBP)

Defines the ProviderConfig class, the single configuration model
used throughout the provider subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class ProviderConfig:
    """
    Configuration object shared by all providers.

    Every provider implementation (Alchemy, Infura, TRON, etc.)
    receives an instance of this class.

    This class is protocol-agnostic and contains no networking logic.
    """

    # ------------------------------------------------------------------
    # Provider Identity
    # ------------------------------------------------------------------

    provider: str
    network: str

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    endpoint: Optional[str] = None
    websocket_endpoint: Optional[str] = None

    timeout: int = 30
    retries: int = 3

    # ------------------------------------------------------------------
    # Optional Configuration
    # ------------------------------------------------------------------

    enabled: bool = True

    options: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)
        # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Validate configuration immediately after initialization.
        """

        self.provider = self.provider.strip().lower()
        self.network = self.network.strip().lower()

        if not self.provider:
            raise ValueError("Provider name cannot be empty.")

        if not self.network:
            raise ValueError("Network name cannot be empty.")

        if self.timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        if self.retries < 0:
            raise ValueError("Retries cannot be negative.")

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def has_api_key(self) -> bool:
        """Return True if an API key is configured."""
        return bool(self.api_key)

    @property
    def has_api_secret(self) -> bool:
        """Return True if an API secret is configured."""
        return bool(self.api_secret)

    @property
    def has_access_token(self) -> bool:
        """Return True if an access token is configured."""
        return bool(self.access_token)

    @property
    def has_endpoint(self) -> bool:
        """Return True if a custom endpoint has been supplied."""
        return bool(self.endpoint)

    @property
    def has_websocket(self) -> bool:
        """Return True if a websocket endpoint has been supplied."""
        return bool(self.websocket_endpoint)

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def copy(self, **updates: Any) -> "ProviderConfig":
        """
        Return a new ProviderConfig with optional field overrides.
        """

        data = self.to_dict()
        data.update(updates)

        return ProviderConfig(**data)
        # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this configuration to a dictionary.
        """

        return {
            "provider": self.provider,
            "network": self.network,
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "access_token": self.access_token,
            "endpoint": self.endpoint,
            "websocket_endpoint": self.websocket_endpoint,
            "timeout": self.timeout,
            "retries": self.retries,
            "enabled": self.enabled,
            "options": dict(self.options),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderConfig":
        """
        Create a ProviderConfig from a dictionary.
        """

        return cls(**data)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a safe string representation.

        Sensitive authentication values are intentionally omitted.
        """

        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider!r}, "
            f"network={self.network!r}, "
            f"endpoint={self.endpoint!r}, "
            f"websocket_endpoint={self.websocket_endpoint!r}, "
            f"timeout={self.timeout}, "
            f"retries={self.retries}, "
            f"enabled={self.enabled})"
        )

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """
        Return True if this provider is enabled.
        """

        return self.enabled

    def enable(self) -> None:
        """
        Enable this provider.
        """

        self.enabled = True

    def disable(self) -> None:
        """
        Disable this provider.
        """

        self.enabled = False