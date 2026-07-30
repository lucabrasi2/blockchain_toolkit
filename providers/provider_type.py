"""
providers/provider_type.py

Universal Blockchain Platform (UBP)

Defines the supported provider protocol categories used by the
provider subsystem.
"""

from __future__ import annotations

from enum import Enum


class ProviderType(str, Enum):
    """
    Provider protocol categories.

    These values describe how a provider communicates with a
    blockchain or external service rather than identifying a
    specific vendor.
    """

    # ---------------------------------------------------------
    # Generic Protocols
    # ---------------------------------------------------------

    WEB3 = "web3"

    REST = "rest"

    WEBSOCKET = "websocket"

    # ---------------------------------------------------------
    # Native Blockchain Protocols
    # ---------------------------------------------------------

    BITCOIN_RPC = "bitcoin_rpc"

    XRPL = "xrpl"

    # ---------------------------------------------------------
    # Extensibility
    # ---------------------------------------------------------

    CUSTOM = "custom"
        # ---------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """
        Return all provider type values.

        Example:
            ("web3", "rest", "websocket", ...)
        """

        return tuple(member.value for member in cls)

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """
        Return all provider type names.

        Example:
            ("WEB3", "REST", ...)
        """

        return tuple(member.name for member in cls)

    @classmethod
    def has_value(cls, value: str) -> bool:
        """
        Determine whether a provider type exists.

        Parameters
        ----------
        value:
            Provider type value.

        Returns
        -------
        bool
        """

        return value.lower() in cls.values()

    @classmethod
    def from_value(cls, value: str) -> "ProviderType":
        """
        Convert a string into a ProviderType.

        Raises
        ------
        ValueError
            If the provider type is unknown.
        """

        normalized = value.strip().lower()

        for member in cls:
            if member.value == normalized:
                return member

        raise ValueError(f"Unsupported provider type: '{value}'")
        # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        """
        Serialize this provider type.

        Returns
        -------
        dict
            Dictionary representation of the provider type.
        """

        return {
            "name": self.name,
            "value": self.value,
        }

    def __str__(self) -> str:
        """
        Return the provider type value.
        """

        return self.value

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"value={self.value!r})"
        )
