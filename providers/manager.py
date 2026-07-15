"""
Universal Blockchain Platform (UBP)

Module:
    Provider Manager

Purpose:
    Manage blockchain providers and connections.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
from typing import Optional, Dict, Any, List
from web3 import Web3

from core.logger import get_logger
from providers.base import BaseProvider


logger = get_logger(__name__)


class SimpleProvider(BaseProvider):
    """
    Simple HTTP provider for direct RPC connections.
    """

    def __init__(self, rpc_url: str, name: str = "http"):
        self._name = name
        self._http_url = rpc_url
        self._ws_url = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def http_url(self) -> str:
        return self._http_url

    @property
    def ws_url(self) -> str:
        return self._ws_url or ""

    def get_config(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
        }

    def is_available(self) -> bool:
        return bool(self.http_url)


class ProviderManager:
    """
    Manager for blockchain providers.
    """

    _instance = None
    _providers: Dict[str, BaseProvider] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the provider manager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._default_provider = None
            self._active_provider = None
            logger.info("ProviderManager initialized.")
            self._create_default_providers()

    def _create_default_providers(self) -> None:
        """Create and register default providers."""
        
        # Try Alchemy HTTP URL first
        alchemy_http = os.getenv("ALCHEMY_HTTP_URL")
        if alchemy_http and "YOUR_ALCHEMY_API_KEY" not in alchemy_http:
            try:
                provider = SimpleProvider(alchemy_http, name="alchemy")
                self.register_provider("alchemy", provider, default=True)
                logger.info(f"✅ Alchemy provider registered as default")
                
                # Test the connection
                w3 = Web3(Web3.HTTPProvider(alchemy_http))
                if w3.is_connected():
                    logger.info(f"✅ Alchemy connection successful. Chain ID: {w3.eth.chain_id}")
                else:
                    logger.warning("⚠️ Alchemy connection failed during test")
                    
            except Exception as error:
                logger.error(f"Failed to create Alchemy provider: {error}")

        # Fallback to public RPC if Alchemy not available
        if not self._providers:
            rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://cloudflare-eth.com")
            try:
                provider = SimpleProvider(rpc_url, name="default")
                self.register_provider("default", provider, default=True)
                logger.info(f"Default provider registered with URL: {rpc_url}")
            except Exception as error:
                logger.error(f"Failed to create default provider: {error}")

    def register_provider(
        self,
        name: str,
        provider: BaseProvider,
        default: bool = False
    ) -> None:
        """
        Register a provider.
        """
        self._providers[name] = provider
        if default:
            self._default_provider = name
            self._active_provider = name
        logger.info(f"Registered provider: {name}")

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        """
        Get a provider by name.
        """
        if name is None:
            name = self._active_provider or self._default_provider

        if name is None:
            raise ValueError("No provider available")

        if name not in self._providers:
            raise ValueError(f"Provider not found: {name}")

        return self._providers[name]

    def get_active_provider(self) -> BaseProvider:
        """Get the active provider."""
        return self.get_provider()

    def set_active_provider(self, name: str) -> None:
        """Set the active provider."""
        if name not in self._providers:
            raise ValueError(f"Provider not found: {name}")
        self._active_provider = name
        logger.info(f"Active provider set to: {name}")

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self._providers.keys())

    def get_provider_config(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get provider configuration."""
        provider = self.get_provider(name)
        return provider.get_config()


# Singleton instance
_provider_manager = None


def get_provider_manager() -> ProviderManager:
    """Get the provider manager instance."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


def get_provider(name: Optional[str] = None) -> BaseProvider:
    """Get a provider instance."""
    manager = get_provider_manager()
    return manager.get_provider(name)


def get_web3(name: Optional[str] = None) -> Optional[Web3]:
    """Get a Web3 instance."""
    try:
        provider = get_provider(name)
        return provider.get_web3()
    except Exception as error:
        logger.error(f"Error getting Web3: {error}")
        return None