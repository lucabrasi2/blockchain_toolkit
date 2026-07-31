"""
core/bootstrap.py

Universal Blockchain Platform (UBP)

Application bootstrapper.

Responsible for initializing the platform and wiring together
core components.
"""

from __future__ import annotations

from providers.alchemy import AlchemyProvider
from providers.factory import ProviderFactory
from providers.infura import InfuraProvider
from providers.manager import ProviderManager
from providers.registry import ProviderRegistry
from providers.tron import TronProvider


def create_provider_registry() -> ProviderRegistry:
    """
    Create and populate the provider registry.
    """

    registry = ProviderRegistry()

    registry.register("alchemy", AlchemyProvider)
    registry.register("infura", InfuraProvider)
    registry.register("tron", TronProvider)

    return registry


def create_provider_factory(
    registry: ProviderRegistry,
) -> ProviderFactory:
    """
    Create the provider factory.
    """

    return ProviderFactory(registry)


def create_provider_manager(
    factory: ProviderFactory,
) -> ProviderManager:
    """
    Create the provider manager.
    """

    return ProviderManager(factory)


def bootstrap() -> ProviderManager:
    """
    Bootstrap the provider subsystem.

    Returns
    -------
    ProviderManager
        Fully initialized provider manager.
    """

    registry = create_provider_registry()

    factory = create_provider_factory(registry)

    manager = create_provider_manager(factory)

    return manager