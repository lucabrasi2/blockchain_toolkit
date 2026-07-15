"""
Universal Blockchain Platform (UBP)

Module:
    Base Provider

Purpose:
    Base class for all blockchain providers.

Responsibilities:
    • Define provider interface
    • Provide common functionality
    • Handle provider configuration

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from web3 import Web3
from core.logger import get_logger


logger = get_logger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for blockchain providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def http_url(self) -> str:
        """HTTP RPC URL."""
        pass

    @property
    @abstractmethod
    def ws_url(self) -> str:
        """WebSocket RPC URL."""
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass

    def get_web3_provider(self):
        """
        Get Web3 HTTP provider.

        Returns
        -------
        Web3.HTTPProvider
            Web3 HTTP provider instance.
        """
        try:
            return Web3.HTTPProvider(self.http_url)
        except Exception as error:
            logger.error(f"Error creating Web3 provider: {error}")
            return None

    def get_web3(self) -> Optional[Web3]:
        """
        Get Web3 instance.

        Returns
        -------
        Optional[Web3]
            Web3 instance or None if failed.
        """
        try:
            provider = self.get_web3_provider()
            if provider:
                w3 = Web3(provider)
                if w3.is_connected():
                    return w3
            return None
        except Exception as error:
            logger.error(f"Error creating Web3 instance: {error}")
            return None

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name}, http_url={self.http_url})"