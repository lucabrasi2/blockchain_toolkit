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

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass(slots=True)
class ProviderConfig:
    """
    Provider configuration container.

    This class holds all configuration needed to instantiate
    a blockchain provider.
    """

    provider: str
    network: str = "mainnet"
    api_key: Optional[str] = None
    http_url: Optional[str] = None
    ws_url: Optional[str] = None
    timeout: int = 30
    retries: int = 3
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns
        -------
        Dict[str, Any]
            Configuration as a dictionary.
        """
        return {
            "provider": self.provider,
            "network": self.network,
            "api_key": self.api_key,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "timeout": self.timeout,
            "retries": self.retries,
            "enabled": self.enabled,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProviderConfig:
        """
        Create a ProviderConfig from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
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