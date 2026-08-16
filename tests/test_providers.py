"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_providers

Purpose
-------
Integration tests for the UBP provider framework.

Tests
-----
• ProviderFactory
• AlchemyProvider
• InfuraProvider
• ProviderManager
• Provider registration
• Provider configuration
• Provider health

Architecture
------------
UBP Enterprise Connectivity Framework

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
===============================================================================
"""

from __future__ import annotations

import os

import pytest

from core.logger import get_logger

from providers.factory import ProviderFactory
from providers.manager import ProviderManager
from providers.exceptions import (
    ProviderError,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Test Configuration
###############################################################################

ALCHEMY_KEY = os.getenv(
    "ALCHEMY_API_KEY",
)

INFURA_KEY = os.getenv(
    "INFURA_API_KEY",
)


###############################################################################
# Factory Fixture
###############################################################################


@pytest.fixture
def factory() -> ProviderFactory:
    """
    Provide a fresh ProviderFactory instance.

    The current UBP factory is instance-based and does
    not use class-level factory methods.
    """

    return ProviderFactory()


###############################################################################
# Factory Tests
###############################################################################


def test_supported_providers(
    factory: ProviderFactory,
) -> None:
    """
    Verify provider discovery.
    """

    providers = (
        factory.supported_providers()
    )

    assert isinstance(
        providers,
        list,
    )

    assert "alchemy" in providers
    assert "infura" in providers


def test_factory_information(
    factory: ProviderFactory,
) -> None:
    """
    Verify factory metadata.

    The current ProviderFactory exposes
    to_dict() rather than the legacy info()
    method.
    """

    info = factory.to_dict()

    assert isinstance(
        info,
        dict,
    )

    assert (
        "provider_count"
        in info
    )

    assert (
        "registered_providers"
        in info
    )

    assert (
        "alchemy"
        in info["registered_providers"]
    )

    assert (
        "infura"
        in info["registered_providers"]
    )


def test_factory_provider_support(
    factory: ProviderFactory,
) -> None:
    """
    Verify provider support detection.
    """

    assert factory.is_supported(
        "alchemy"
    )

    assert factory.is_supported(
        "infura"
    )

    assert not factory.is_supported(
        "unknown_provider"
    )
###############################################################################
# Provider Creation Tests
###############################################################################


def test_create_alchemy_provider(
    factory: ProviderFactory,
) -> None:
    """
    Verify Alchemy provider creation.

    This test requires ALCHEMY_API_KEY.
    """

    if not ALCHEMY_KEY:

        pytest.skip(
            "ALCHEMY_API_KEY is not configured."
        )

    provider = factory.create_by_name(
        "alchemy",
        api_key=ALCHEMY_KEY,
        network="mainnet",
    )

    assert provider is not None

    assert (
        provider.name
        == "alchemy"
    )

    assert (
        provider.blockchain
        == "ethereum"
    )

    assert (
        provider.network
        == "mainnet"
    )


def test_create_infura_provider(
    factory: ProviderFactory,
) -> None:
    """
    Verify Infura provider creation.

    This test requires INFURA_API_KEY.
    """

    if not INFURA_KEY:

        pytest.skip(
            "INFURA_API_KEY is not configured."
        )

    provider = factory.create_by_name(
        "infura",
        api_key=INFURA_KEY,
        network="mainnet",
    )

    assert provider is not None

    assert (
        provider.name
        == "infura"
    )

    assert (
        provider.blockchain
        == "ethereum"
    )

    assert (
        provider.network
        == "mainnet"
    )


###############################################################################
# Provider Configuration Tests
###############################################################################


def test_alchemy_configuration_without_key(
    factory: ProviderFactory,
) -> None:
    """
    Verify Alchemy provider construction without
    credentials remains possible.

    The current AlchemyProvider permits construction
    without an API key and uses the demo endpoint.
    Live connectivity is tested separately.
    """

    provider = factory.create_by_name(
        "alchemy",
        network="mainnet",
    )

    assert provider is not None

    assert (
        provider.name
        == "alchemy"
    )

    assert (
        provider.blockchain
        == "ethereum"
    )

    assert (
        provider.network
        == "mainnet"
    )
###############################################################################
# ProviderManager Tests
###############################################################################


def test_provider_manager_registration(
    factory: ProviderFactory,
) -> None:
    """
    Verify providers can be registered
    with ProviderManager.
    """

    manager = ProviderManager()

    registered = []

    if ALCHEMY_KEY:

        alchemy = factory.create_by_name(
            "alchemy",
            api_key=ALCHEMY_KEY,
            network="mainnet",
        )

        manager.register_provider(
            "alchemy",
            alchemy,
            default=True,
        )

        registered.append(
            "alchemy"
        )

    if INFURA_KEY:

        infura = factory.create_by_name(
            "infura",
            api_key=INFURA_KEY,
            network="mainnet",
        )

        manager.register_provider(
            "infura",
            infura,
        )

        registered.append(
            "infura"
        )

    providers = manager.list_providers()

    assert isinstance(
        providers,
        list,
    )

    for name in registered:

        assert name in providers


def test_active_provider_selection(
    factory: ProviderFactory,
) -> None:
    """
    Verify active provider selection.
    """

    if not ALCHEMY_KEY:

        pytest.skip(
            "ALCHEMY_API_KEY is not configured."
        )

    manager = ProviderManager()

    provider = factory.create_by_name(
        "alchemy",
        api_key=ALCHEMY_KEY,
        network="mainnet",
    )

    manager.register_provider(
        "alchemy",
        provider,
        default=True,
    )

    active = (
        manager.get_active_provider()
    )

    assert active is not None

    assert (
        active.name
        == "alchemy"
    )


###############################################################################
# Provider Health Tests
###############################################################################


def test_provider_health_check(
    factory: ProviderFactory,
) -> None:
    """
    Verify provider health monitoring.

    Requires a configured Alchemy API key
    because this test performs a live RPC check.
    """

    if not ALCHEMY_KEY:

        pytest.skip(
            "ALCHEMY_API_KEY is not configured."
        )

    provider = factory.create_by_name(
        "alchemy",
        api_key=ALCHEMY_KEY,
        network="mainnet",
    )

    status = provider.health_check()

    assert isinstance(
        status,
        bool,
    )

    assert status is True


def test_provider_metadata(
    factory: ProviderFactory,
) -> None:
    """
    Verify standardized provider metadata.
    """

    if not ALCHEMY_KEY:

        pytest.skip(
            "ALCHEMY_API_KEY is not configured."
        )

    provider = factory.create_by_name(
        "alchemy",
        api_key=ALCHEMY_KEY,
        network="mainnet",
    )

    metadata = provider.metadata

    assert (
        metadata.provider_name
        == "alchemy"
    )

    assert (
        metadata.blockchain
        == "ethereum"
    )

    assert (
        metadata.network
        == "mainnet"
    )


###############################################################################
# Test Runner
###############################################################################


if __name__ == "__main__":

    pytest.main(
        [
            __file__,
            "-v",
        ]
    )


###############################################################################
# End of File
###############################################################################