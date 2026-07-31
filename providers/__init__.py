"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers

Purpose
-------
Enterprise provider system.

This package provides a unified abstraction layer for
all blockchain connectivity providers.

Architecture
------------
    ┌─────────────────────────────────────────────┐
    │           ProviderManager                   │
    │  (Orchestration, Failover, Health)         │
    └─────────────────────────────────────────────┘
                        │
    ┌─────────────────────────────────────────────┐
    │            ProviderFactory                  │
    │  (Instantiation, Configuration)            │
    └─────────────────────────────────────────────┘
                        │
    ┌─────────────────────────────────────────────┐
    │           ProviderRegistry                  │
    │  (Registration, Discovery)                 │
    └─────────────────────────────────────────────┘
                        │
    ┌─────────────────────────────────────────────┐
    │              BaseProvider                   │
    │  (Abstract Contract)                       │
    └─────────────────────────────────────────────┘

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

from providers.base import BaseProvider, ProviderStatus, ProviderType
from providers.exceptions import (
    ProviderError,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderUnavailableError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderNotFoundError,
    ProviderHealthCheckError,
    ProviderUnsupportedOperationError,
    DuplicateRegistrationError,
)
from providers.registry import ProviderRegistry
from providers.factory import ProviderFactory
from providers.manager import ProviderManager

# Register all providers
from providers.alchemy import AlchemyProvider
from providers.infura import InfuraProvider
from providers.local import LocalProvider
from providers.public import PublicProvider
from providers.tron import TronProvider

# Auto-register providers
ProviderRegistry.register("alchemy", AlchemyProvider, alias=["alch"])
ProviderRegistry.register("infura", InfuraProvider)
ProviderRegistry.register("local", LocalProvider)
ProviderRegistry.register("public", PublicProvider, alias=["publicnode"])
ProviderRegistry.register("tron", TronProvider)


__all__ = [
    # Base
    "BaseProvider",
    "ProviderStatus",
    "ProviderType",
    # Exceptions
    "ProviderError",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    "ProviderAuthenticationError",
    "ProviderUnavailableError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "ProviderNotFoundError",
    "ProviderHealthCheckError",
    "ProviderUnsupportedOperationError",
    "DuplicateRegistrationError",
    # Core
    "ProviderRegistry",
    "ProviderFactory",
    "ProviderManager",
    # Providers
    "AlchemyProvider",
    "InfuraProvider",
    "LocalProvider",
    "PublicProvider",
    "TronProvider",
]


###############################################################################
# Convenience Functions
###############################################################################

# Global factory instance
_factory: ProviderFactory = None


def get_factory() -> ProviderFactory:
    """Get the global provider factory instance."""
    global _factory
    if _factory is None:
        _factory = ProviderFactory()
    return _factory


def get_provider(name: str = None, **kwargs) -> BaseProvider:
    """
    Get a provider instance by name.

    Parameters
    ----------
    name : str, optional
        Provider name. If None, returns the first registered provider.
    **kwargs : Any
        Provider-specific configuration.

    Returns
    -------
    BaseProvider
        Provider instance.

    Raises
    ------
    ProviderNotFoundError
        If the provider is not found.
    """
    factory = get_factory()
    return factory.get_provider(name, **kwargs)


def get_web3(name: str = None):
    """
    Get a Web3 instance from a provider.

    Parameters
    ----------
    name : str, optional
        Provider name. If None, uses the default provider.

    Returns
    -------
    Web3
        Web3 instance.

    Raises
    ------
    ProviderNotFoundError
        If the provider is not found.
    """
    provider = get_provider(name)
    return provider.web3


def create_provider(provider_type: str, **kwargs) -> BaseProvider:
    """
    Create a provider instance.

    Parameters
    ----------
    provider_type : str
        Provider type.
    **kwargs : Any
        Provider-specific configuration.

    Returns
    -------
    BaseProvider
        Provider instance.
    """
    factory = get_factory()
    return factory.create_by_name(provider_type, **kwargs)


def get_default_provider() -> BaseProvider:
    """
    Get the default provider.

    Returns
    -------
    BaseProvider
        Default provider instance.
    """
    return get_provider()


###############################################################################
# End of File
###############################################################################