"""
Universal Blockchain Platform (UBP)

## Module

tests.test_providers.bitcoin.test_transaction

## Purpose

Tests for Bitcoin transaction inspection.

No real Bitcoin network calls are performed.
The Bitcoin JSON-RPC boundary is mocked.

## Version

2.0.0
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from providers.bitcoin import BitcoinProvider
from providers.config import ProviderConfig


###############################################################################
# Constants
###############################################################################

TRANSACTION_HASH = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)


###############################################################################
# Fixtures
###############################################################################

@pytest.fixture
def provider() -> BitcoinProvider:
    """
    Return a configured Bitcoin provider.
    """

    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
    )

    return BitcoinProvider(config)


###############################################################################
# Transaction Inspection
###############################################################################

def test_get_transaction(
    provider: BitcoinProvider,
) -> None:
    expected = {
        "txid": TRANSACTION_HASH,
        "hash": TRANSACTION_HASH,
        "version": 2,
        "size": 225,
        "vsize": 144,
        "weight": 576,
        "locktime": 0,
        "vin": [],
        "vout": [],
    }

    provider.rpc_call = MagicMock(
        return_value=expected
    )

    result = provider.get_transaction(
        TRANSACTION_HASH
    )

    assert result == expected

    provider.rpc_call.assert_called_once_with(
        "getrawtransaction",
        [
            TRANSACTION_HASH,
            True,
        ],
    )


def test_get_transaction_rejects_non_string(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(TypeError):
        provider.get_transaction(123)


def test_get_transaction_rejects_empty_hash(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_transaction("")


def test_get_transaction_rejects_whitespace_hash(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_transaction("   ")


def test_get_transaction_strips_hash(
    provider: BitcoinProvider,
) -> None:
    expected = {
        "txid": TRANSACTION_HASH,
    }

    provider.rpc_call = MagicMock(
        return_value=expected
    )

    result = provider.get_transaction(
        f"  {TRANSACTION_HASH}  "
    )

    assert result == expected

    provider.rpc_call.assert_called_once_with(
        "getrawtransaction",
        [
            TRANSACTION_HASH,
            True,
        ],
    )


def test_get_transaction_rejects_invalid_rpc_result(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value=None
    )

    with pytest.raises(
        ValueError,
        match="invalid transaction data",
    ):
        provider.get_transaction(
            TRANSACTION_HASH
        )


def test_get_transaction_propagates_rpc_error(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        side_effect=RuntimeError(
            "Bitcoin RPC error: transaction not found."
        )
    )

    with pytest.raises(
        RuntimeError,
        match="transaction not found",
    ):
        provider.get_transaction(
            TRANSACTION_HASH
        )
