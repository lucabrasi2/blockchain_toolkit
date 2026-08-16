"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.config

Purpose
-------
Provider configuration models.

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

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class ProviderConfig:
    """
    Provider configuration container.

    This class holds all configuration required to instantiate
    a blockchain provider.
    """

    provider: str
    network: str = "mainnet"
    api_key: str | None = None
    http_url: str | None = None
    ws_url: str | None = None
    timeout: int = 30
    retries: int = 3
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this configuration to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of this configuration.
        """
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ProviderConfig":
        """
        Create a ProviderConfig from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Configuration data.

        Returns
        -------
        ProviderConfig
            Provider configuration instance.
        """
        return cls(**data)


###############################################################################
# End of File
###############################################################################