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

    ProviderManager
    (Orchestration, Failover, Health)
            |
    ProviderFactory
    (Instantiation, Configuration)
            |
    ProviderRegistry
    (Registration, Discovery)
            |
    BaseProvider
    (Abstract Contract)

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

from core.logger import get_logger

from providers.base import (
    BaseProvider,
    ProviderStatus,
    ProviderType,
)

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

from providers.alchemy import AlchemyProvider
from providers.infura import InfuraProvider
from providers.local import LocalProvider
from providers.public import PublicProvider
from providers.tron import TronProvider
from providers.bitcoin import BitcoinProvider


logger = get_logger(__name__)


###############################################################################
# Provider Registration
###############################################################################

if not ProviderRegistry.contains("alchemy"):
    ProviderRegistry.register(
        "alchemy",
        AlchemyProvider,
        alias=["alch"],
    )

if not ProviderRegistry.contains("infura"):
    ProviderRegistry.register(
        "infura",
        InfuraProvider,
    )

if not ProviderRegistry.contains("local"):
    ProviderRegistry.register(
        "local",
        LocalProvider,
    )

if not ProviderRegistry.contains("public"):
    ProviderRegistry.register(
        "public",
        PublicProvider,
        alias=["publicnode"],
    )

if not ProviderRegistry.contains("tron"):
    ProviderRegistry.register(
        "tron",
        TronProvider,
    )

if not ProviderRegistry.contains("bitcoin"):
    ProviderRegistry.register(
        "bitcoin",
        BitcoinProvider,
    )


###############################################################################
# Public API
###############################################################################

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
    "BitcoinProvider",

]


###############################################################################
# Global Provider Factory
###############################################################################

_factory: ProviderFactory | None = None

_provider_cache: dict[str, BaseProvider] = {}


###############################################################################
# Factory Helpers
###############################################################################

def get_factory() -> ProviderFactory:
    """
    Return the global provider factory.
    """

    global _factory

    if _factory is None:

        logger.info(
            "Creating global ProviderFactory."
        )

        _factory = ProviderFactory()

    return _factory


###############################################################################
# Provider Helpers
###############################################################################

def get_provider(
    name: str | None = None,
    **kwargs,
) -> BaseProvider:
    """
    Return a provider instance.

    Cached providers are reused.
    """

    global _provider_cache

    factory = get_factory()

    if name is None:

        providers = factory.supported_providers()

        if not providers:

            raise ProviderNotFoundError(
                "No providers registered."
            )

        name = providers[0]

    name = name.strip().lower()

    if name in _provider_cache:

        logger.debug(
            "Returning cached provider '%s'.",
            name,
        )

        return _provider_cache[name]

    logger.info(
        "Creating provider '%s'.",
        name,
    )

    provider = factory.create_by_name(
        name,
        **kwargs,
    )

    _provider_cache[name] = provider

    return provider


def get_web3(
    name: str | None = None,
):
    """
    Return the provider's Web3 instance.
    """

    provider = get_provider(name)

    return provider.web3


def create_provider(
    provider_type: str,
    **kwargs,
) -> BaseProvider:
    """
    Create a provider without caching.
    """

    logger.info(
        "Creating provider '%s'.",
        provider_type,
    )

    return get_factory().create_by_name(
        provider_type,
        **kwargs,
    )


def get_default_provider() -> BaseProvider:
    """
    Return the default provider.
    """

    return get_provider()


###############################################################################
# End of File
###############################################################################