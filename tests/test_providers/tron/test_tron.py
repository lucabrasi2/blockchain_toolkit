"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_providers.tron.test_tron

Purpose
-------
Tests for the native TRON provider.

No real TRON network calls are performed.
HTTP behavior is mocked.

Version
-------
2.0 Enterprise
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from providers.config import ProviderConfig
from providers.exceptions import ProviderConfigurationError
from providers.exceptions import ProviderConnectionError
from providers.tron import TronProvider


###############################################################################
# Helpers
###############################################################################


def make_config(
    network: str = "mainnet",
    **kwargs,
) -> ProviderConfig:
    """
    Build a standard TRON ProviderConfig.
    """

    return ProviderConfig(
        provider="tron",
        network=network,
        **kwargs,
    )


###############################################################################
# Construction
###############################################################################


def test_provider_constructs_from_config() -> None:
    provider = TronProvider(
        make_config()
    )

    assert provider.name == "tron"
    assert provider.blockchain == "tron"
    assert provider.network == "mainnet"


def test_provider_accepts_test_networks() -> None:
    for network in (
        "mainnet",
        "shasta",
        "nile",
    ):
        provider = TronProvider(
            make_config(network)
        )

        assert provider.network == network


def test_provider_normalizes_network() -> None:
    provider = TronProvider(
        make_config("NILE")
    )

    assert provider.network == "nile"


def test_provider_requires_config() -> None:
    with pytest.raises(TypeError):
        TronProvider(None)


def test_invalid_network_raises_configuration_error() -> None:
    with pytest.raises(
        ProviderConfigurationError
    ):
        TronProvider(
            make_config("invalid")
        )


###############################################################################
# Endpoints
###############################################################################


def test_mainnet_endpoint() -> None:
    provider = TronProvider(
        make_config("mainnet")
    )

    assert (
        provider.http_url
        == "https://api.trongrid.io"
    )


def test_shasta_endpoint() -> None:
    provider = TronProvider(
        make_config("shasta")
    )

    assert (
        provider.http_url
        == "https://api.shasta.trongrid.io"
    )


def test_nile_endpoint() -> None:
    provider = TronProvider(
        make_config("nile")
    )

    assert (
        provider.http_url
        == "https://nile.trongrid.io"
    )


def test_custom_http_endpoint() -> None:
    endpoint = (
        "https://tron.example.internal"
    )

    provider = TronProvider(
        make_config(
            http_url=endpoint
        )
    )

    assert provider.http_url == endpoint


###############################################################################
# WebSocket
###############################################################################


def test_websocket_defaults_to_disabled() -> None:
    provider = TronProvider(
        make_config()
    )

    assert provider.ws_url == ""
    assert provider.supports_websocket is False


def test_custom_websocket_endpoint_is_exposed() -> None:
    endpoint = (
        "wss://tron.example.internal"
    )

    provider = TronProvider(
        make_config(
            ws_url=endpoint
        )
    )

    assert provider.ws_url == endpoint
    assert provider.supports_websocket is True


###############################################################################
# Capabilities
###############################################################################


def test_provider_capabilities() -> None:
    provider = TronProvider(
        make_config()
    )

    assert provider.supports_archive is True
    assert provider.supports_debug_api is False
    assert provider.supports_trace_api is False


###############################################################################
# Configuration
###############################################################################


def test_get_config() -> None:
    provider = TronProvider(
        make_config()
    )

    config = provider.get_config()

    assert config["provider"] == "tron"
    assert config["blockchain"] == "tron"
    assert config["network"] == "mainnet"
    assert config["http_url"] == (
        "https://api.trongrid.io"
    )


def test_api_key_is_not_exposed() -> None:
    provider = TronProvider(
        make_config(
            api_key="1234567890abcdef"
        )
    )

    config = provider.get_config()

    assert (
        "1234567890abcdef"
        not in str(config)
    )


def test_api_key_is_masked() -> None:
    provider = TronProvider(
        make_config(
            api_key="1234567890abcdef"
        )
    )

    assert provider.masked_api_key == (
        "1234...cdef"
    )


###############################################################################
# Session
###############################################################################


def test_build_session_sets_default_headers() -> None:
    provider = TronProvider(
        make_config()
    )

    session = provider._build_session()

    assert session.headers["Accept"] == (
        "application/json"
    )

    assert session.headers["Content-Type"] == (
        "application/json"
    )

    session.close()


def test_build_session_sets_trongrid_api_key() -> None:
    provider = TronProvider(
        make_config(
            api_key="test-api-key"
        )
    )

    session = provider._build_session()

    assert (
        session.headers["TRON-PRO-API-KEY"]
        == "test-api-key"
    )

    session.close()


###############################################################################
# Connection
###############################################################################


def test_connect_success() -> None:
    provider = TronProvider(
        make_config()
    )

    response = MagicMock()
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.get.return_value = response
    session.headers = {}

    provider._build_session = MagicMock(
        return_value=session
    )

    assert provider.connect() is True

    assert provider.status.value == "ONLINE"
    assert provider.statistics.successful_connections == 1


def test_connect_failure() -> None:
    provider = TronProvider(
        make_config()
    )

    session = MagicMock()

    session.get.side_effect = (
        requests_connection_error()
    )

    provider._build_session = MagicMock(
        return_value=session
    )

    with pytest.raises(
        ProviderConnectionError
    ):
        provider.connect()

    assert provider.status.value == "OFFLINE"


def requests_connection_error() -> Exception:
    """
    Create a generic connection exception.

    Kept local so the tests don't depend on
    a live network.
    """

    return ConnectionError(
        "mock connection failure"
    )
###############################################################################
# Registry Integration
###############################################################################


def test_tron_registered() -> None:
    from providers import ProviderRegistry

    assert ProviderRegistry.contains(
        "tron"
    )


def test_registry_returns_tron_provider() -> None:
    from providers import ProviderRegistry

    provider_class = ProviderRegistry.get(
        "tron"
    )

    assert provider_class is TronProvider


###############################################################################
# Factory Integration
###############################################################################


def test_factory_creates_tron_provider() -> None:
    from providers import ProviderFactory

    factory = ProviderFactory()

    config = ProviderConfig(
        provider="tron",
        network="mainnet",
    )

    provider = factory.create(
        config
    )

    assert isinstance(
        provider,
        TronProvider,
    )


def test_factory_preserves_tron_network() -> None:
    from providers import ProviderFactory

    factory = ProviderFactory()

    config = ProviderConfig(
        provider="tron",
        network="nile",
    )

    provider = factory.create(
        config
    )

    assert provider.network == "nile"

    assert (
        provider.http_url
        == "https://nile.trongrid.io"
    )


def test_factory_preserves_tron_custom_endpoint() -> None:
    from providers import ProviderFactory

    factory = ProviderFactory()

    endpoint = (
        "https://tron.example.internal"
    )

    config = ProviderConfig(
        provider="tron",
        network="mainnet",
        http_url=endpoint,
    )

    provider = factory.create(
        config
    )

    assert provider.http_url == endpoint
