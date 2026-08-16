"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_providers.bitcoin.test_bitcoin

Purpose
-------
Unit and integration tests for the UBP Bitcoin provider.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from providers import ProviderFactory
from providers import ProviderRegistry
from providers.base import ProviderType
from providers.bitcoin import BitcoinProvider
from providers.config import ProviderConfig


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def config() -> ProviderConfig:
    """
    Return a standard UBP Bitcoin provider configuration.
    """

    return ProviderConfig(
        provider="bitcoin",
        network="mainnet",
    )


@pytest.fixture
def provider(
    config: ProviderConfig,
) -> BitcoinProvider:
    """
    Return a Bitcoin provider instance.
    """

    return BitcoinProvider(config)


###############################################################################
# Provider Identity
###############################################################################


def test_provider_name(
    provider: BitcoinProvider,
) -> None:
    assert provider.name == "bitcoin"


def test_blockchain(
    provider: BitcoinProvider,
) -> None:
    assert provider.blockchain == "bitcoin"


def test_network(
    provider: BitcoinProvider,
) -> None:
    assert provider.network == "mainnet"


def test_provider_type(
    provider: BitcoinProvider,
) -> None:
    assert provider.provider_type == ProviderType.LOCAL


###############################################################################
# Endpoint Configuration
###############################################################################


def test_mainnet_endpoint(
    provider: BitcoinProvider,
) -> None:
    assert (
        provider.http_url
        == "http://127.0.0.1:8332"
    )


def test_testnet_endpoint(
    config: ProviderConfig,
) -> None:
    config.network = "testnet"

    provider = BitcoinProvider(config)

    assert (
        provider.http_url
        == "http://127.0.0.1:18332"
    )


def test_regtest_endpoint(
    config: ProviderConfig,
) -> None:
    config.network = "regtest"

    provider = BitcoinProvider(config)

    assert (
        provider.http_url
        == "http://127.0.0.1:18443"
    )


def test_signet_endpoint(
    config: ProviderConfig,
) -> None:
    config.network = "signet"

    provider = BitcoinProvider(config)

    assert (
        provider.http_url
        == "http://127.0.0.1:38332"
    )


def test_custom_endpoint() -> None:
    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
        http_url=(
            "http://bitcoin-node.internal:8332"
        ),
    )

    provider = BitcoinProvider(config)

    assert (
        provider.http_url
        == "http://bitcoin-node.internal:8332"
    )

    assert (
        provider.provider_type
        == ProviderType.PRIVATE
    )


def test_websocket_endpoint(
    provider: BitcoinProvider,
) -> None:
    assert provider.ws_url == ""


###############################################################################
# Configuration
###############################################################################


def test_get_config(
    provider: BitcoinProvider,
) -> None:
    result = provider.get_config()

    assert result["provider"] == "bitcoin"
    assert result["blockchain"] == "bitcoin"
    assert result["network"] == "mainnet"
    assert (
        result["provider_type"]
        == ProviderType.LOCAL.value
    )
    assert result["http_url"] == (
        "http://127.0.0.1:8332"
    )
    assert (
        result["websocket_enabled"]
        is False
    )
    assert (
        result["authentication_configured"]
        is False
    )


###############################################################################
# JSON-RPC Transport
###############################################################################


def test_rpc_call(
    provider: BitcoinProvider,
) -> None:
    response = MagicMock()

    response.json.return_value = {
        "result": {
            "chain": "main",
            "blocks": 100,
        },
        "error": None,
        "id": "ubp",
    }

    response.raise_for_status.return_value = None

    provider._session.post = MagicMock(
        return_value=response
    )

    result = provider.rpc_call(
        "getblockchaininfo"
    )

    assert result == {
        "chain": "main",
        "blocks": 100,
    }

    provider._session.post.assert_called_once_with(
        "http://127.0.0.1:8332",
        json={
            "jsonrpc": "1.0",
            "id": "ubp",
            "method": "getblockchaininfo",
            "params": [],
        },
        auth=None,
        timeout=30,
    )


def test_rpc_call_with_parameters(
    provider: BitcoinProvider,
) -> None:
    response = MagicMock()

    response.json.return_value = {
        "result": "block-hash",
        "error": None,
        "id": "ubp",
    }

    response.raise_for_status.return_value = None

    provider._session.post = MagicMock(
        return_value=response
    )

    result = provider.rpc_call(
        "getblockhash",
        [100],
    )

    assert result == "block-hash"

    provider._session.post.assert_called_once()


def test_rpc_method_must_be_string(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        TypeError,
        match="RPC method must be a string",
    ):
        provider.rpc_call(123)  # type: ignore[arg-type]


def test_rpc_method_cannot_be_empty(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        ValueError,
        match="RPC method cannot be empty",
    ):
        provider.rpc_call("")


def test_rpc_parameters_must_be_list(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        TypeError,
        match="RPC parameters must be a list",
    ):
        provider.rpc_call(
            "getblockhash",
            "invalid",  # type: ignore[arg-type]
        )


###############################################################################
# RPC Error Handling
###############################################################################


def test_rpc_error_is_raised(
    provider: BitcoinProvider,
) -> None:
    response = MagicMock()

    response.json.return_value = {
        "result": None,
        "error": {
            "code": -1,
            "message": "Bitcoin RPC failure",
        },
        "id": "ubp",
    }

    response.raise_for_status.return_value = None

    provider._session.post = MagicMock(
        return_value=response
    )

    with pytest.raises(
        RuntimeError,
        match="Bitcoin RPC error: Bitcoin RPC failure",
    ):
        provider.rpc_call(
            "getblockchaininfo"
        )


def test_invalid_rpc_response(
    provider: BitcoinProvider,
) -> None:
    response = MagicMock()

    response.json.return_value = [
        "invalid"
    ]

    response.raise_for_status.return_value = None

    provider._session.post = MagicMock(
        return_value=response
    )

    with pytest.raises(
        ValueError,
        match="invalid response",
    ):
        provider.rpc_call(
            "getblockchaininfo"
        )


def test_rpc_response_without_result(
    provider: BitcoinProvider,
) -> None:
    response = MagicMock()

    response.json.return_value = {
        "error": None,
        "id": "ubp",
    }

    response.raise_for_status.return_value = None

    provider._session.post = MagicMock(
        return_value=response
    )

    with pytest.raises(
        ValueError,
        match="does not contain a result",
    ):
        provider.rpc_call(
            "getblockchaininfo"
        )
###############################################################################
# Transaction Broadcasting
###############################################################################


def test_send_raw_transaction(
    provider: BitcoinProvider,
) -> None:
    signed_transaction = (
        "0200000001"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "00000000"
    )

    transaction_id = (
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    )

    provider.rpc_call = MagicMock(
        return_value=transaction_id
    )

    result = provider.send_raw_transaction(
        signed_transaction
    )

    assert result == transaction_id

    provider.rpc_call.assert_called_once_with(
        "sendrawtransaction",
        [
            signed_transaction,
        ],
    )


def test_send_raw_transaction_rejects_non_string(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        TypeError,
        match="signed_transaction must be a string",
    ):
        provider.send_raw_transaction(
            123  # type: ignore[arg-type]
        )


def test_send_raw_transaction_rejects_empty(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        ValueError,
        match="signed_transaction cannot be empty",
    ):
        provider.send_raw_transaction("")


def test_send_raw_transaction_rejects_whitespace(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(
        ValueError,
        match="signed_transaction cannot be empty",
    ):
        provider.send_raw_transaction("   ")


def test_send_raw_transaction_rejects_invalid_rpc_result(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value=None
    )

    with pytest.raises(
        ValueError,
        match="invalid transaction ID",
    ):
        provider.send_raw_transaction(
            "signed-transaction"
        )


def test_send_raw_transaction_rejects_empty_rpc_result(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value="   "
    )

    with pytest.raises(
        ValueError,
        match="empty transaction ID",
    ):
        provider.send_raw_transaction(
            "signed-transaction"
        )

###############################################################################
# Bitcoin Node Information
###############################################################################


def test_get_blockchain_info(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "chain": "main",
            "blocks": 100,
        }
    )

    result = provider.get_blockchain_info()

    assert result["chain"] == "main"
    assert result["blocks"] == 100

    provider.rpc_call.assert_called_once_with(
        "getblockchaininfo"
    )


def test_get_network_info(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "version": 270000,
            "connections": 8,
        }
    )

    result = provider.get_network_info()

    assert result["connections"] == 8

    provider.rpc_call.assert_called_once_with(
        "getnetworkinfo"
    )


def test_get_block_count(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value=900000
    )

    result = provider.get_block_count()

    assert result == 900000

    provider.rpc_call.assert_called_once_with(
        "getblockcount"
    )


###############################################################################
# Connection Lifecycle
###############################################################################


def test_connect_success(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "chain": "main",
            "blocks": 100,
        }
    )

    result = provider.connect()

    assert result is True
    assert provider.is_connected() is True
    assert provider.last_error is None

    provider.rpc_call.assert_called_once_with(
        "getblockchaininfo"
    )


def test_connect_failure(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        side_effect=RuntimeError(
            "Bitcoin node unavailable"
        )
    )

    result = provider.connect()

    assert result is False
    assert provider.is_connected() is False
    assert (
        provider.last_error
        == "Bitcoin node unavailable"
    )


def test_disconnect(
    provider: BitcoinProvider,
) -> None:
    provider._connected = True

    provider.disconnect()

    assert provider.is_connected() is False


###############################################################################
# Status
###############################################################################


def test_get_status(
    provider: BitcoinProvider,
) -> None:
    result = provider.get_status()

    assert result["provider"] == "bitcoin"
    assert result["blockchain"] == "bitcoin"
    assert result["network"] == "mainnet"
    assert result["connected"] is False
    assert result["last_error"] is None


###############################################################################
# Registry Integration
###############################################################################


def test_bitcoin_registered() -> None:
    assert ProviderRegistry.contains(
        "bitcoin"
    )


def test_registry_returns_bitcoin_provider() -> None:
    provider_class = ProviderRegistry.get(
        "bitcoin"
    )

    assert provider_class is BitcoinProvider


def test_registry_lists_bitcoin() -> None:
    providers = ProviderRegistry.list_providers()

    assert "bitcoin" in providers


###############################################################################
# Factory Integration
###############################################################################


def test_factory_creates_bitcoin_provider() -> None:
    factory = ProviderFactory()

    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
    )

    provider = factory.create(
        config
    )

    assert isinstance(
        provider,
        BitcoinProvider,
    )


def test_factory_created_bitcoin_identity() -> None:
    factory = ProviderFactory()

    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
    )

    provider = factory.create(
        config
    )

    assert provider.name == "bitcoin"
    assert provider.blockchain == "bitcoin"
    assert provider.network == "mainnet"


def test_factory_created_bitcoin_network() -> None:
    factory = ProviderFactory()

    config = ProviderConfig(
        provider="bitcoin",
        network="testnet",
    )

    provider = factory.create(
        config
    )

    assert isinstance(
        provider,
        BitcoinProvider,
    )

    assert provider.network == "testnet"

    assert (
        provider.http_url
        == "http://127.0.0.1:18332"
    )


###############################################################################
# Bitcoin Authentication Configuration
###############################################################################


def test_rpc_authentication_configuration() -> None:
    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
        options={
            "username": "rpcuser",
            "password": "rpcpassword",
        },
    )

    provider = BitcoinProvider(config)

    assert (
        provider.get_config()[
            "authentication_configured"
        ]
        is True
    )


###############################################################################
# End of File
###############################################################################