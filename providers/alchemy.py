"""
Universal Blockchain Platform (UBP)

Module:
    Alchemy Provider

Purpose:
    Alchemy blockchain provider implementation.

Responsibilities:
    • Provide Alchemy RPC endpoints
    • Handle Alchemy API keys
    • Manage Alchemy connections
    • Support HTTP and WebSocket

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
from typing import Optional, Dict, Any

from core.logger import get_logger
from providers.base import BaseProvider


logger = get_logger(__name__)


class AlchemyProvider(BaseProvider):
    """
    Alchemy blockchain provider.
    """

    def __init__(self, api_key: Optional[str] = None, network: str = "mainnet"):
        """
        Initialize the Alchemy provider.

        Parameters
        ----------
        api_key : str, optional
            Alchemy API key.
        network : str, optional
            Network to connect to.
        """
        self.api_key = api_key or os.getenv("ALCHEMY_API_KEY", "")
        self.network = network
        self._http_url = None
        self._ws_url = None

    @property
    def name(self) -> str:
        """Provider name."""
        return "alchemy"

    @property
    def http_url(self) -> str:
        """HTTP RPC URL."""
        if not self._http_url:
            self._http_url = f"https://{self.network}.g.alchemy.com/v2/{self.api_key}"
        return self._http_url

    @property
    def ws_url(self) -> str:
        """WebSocket RPC URL."""
        if not self._ws_url:
            self._ws_url = f"wss://{self.network}.g.alchemy.com/v2/{self.api_key}"
        return self._ws_url

    def get_config(self) -> Dict[str, Any]:
        """
        Get provider configuration.

        Returns
        -------
        Dict[str, Any]
            Provider configuration.
        """
        return {
            "name": self.name,
            "network": self.network,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "api_key": self.api_key[:8] + "..." if self.api_key else "",
        }

    def is_available(self) -> bool:
        """
        Check if the provider is available.

        Returns
        -------
        bool
            True if the provider is available.
        """
        return bool(self.api_key) and self.api_key != "YOUR_ALCHEMY_API_KEY"