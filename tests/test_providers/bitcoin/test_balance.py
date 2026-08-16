"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_providers.bitcoin.test_balance

Purpose
-------
Tests for BitcoinProvider balance and UTXO capabilities.

No real Bitcoin network calls are performed.
The Bitcoin JSON-RPC boundary is mocked.

Version
-------
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

VALID_ADDRESS = (
    "bc1qexamplebitcoinwalletaddress"
)

BEST_BLOCK = (
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
)

TXID_1 = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)

TXID_2 = (
    "cccccccccccccccccccccccccccccccc"
    "cccccccccccccccccccccccccccccccc"
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
# Address UTXOs
###############################################################################

def test_get_address_utxos(
    provider: BitcoinProvider,
) -> None:
    expected = [
        {
            "txid": TXID_1,
            "vout": 0,
            "scriptPubKey": {
                "desc": f"addr({VALID_ADDRESS})",
                "hex": "0014example",
                "address": VALID_ADDRESS,
                "type": "witness_v0_keyhash",
            },
            "amount": 0.5,
            "height": 850000,
            "coinbase": False,
        }
    ]

    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "searched_items": 100,
            "bestblock": BEST_BLOCK,
            "unspents": expected,
            "total_amount": 0.5,
        }
    )

    result = provider.get_address_utxos(
        VALID_ADDRESS
    )

    assert result == expected

    provider.rpc_call.assert_called_once_with(
        "scantxoutset",
        [
            "start",
            [
                f"addr({VALID_ADDRESS})"
            ],
        ],
    )


def test_get_address_utxos_returns_empty_list(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "searched_items": 100,
            "bestblock": BEST_BLOCK,
            "unspents": [],
            "total_amount": 0,
        }
    )

    result = provider.get_address_utxos(
        VALID_ADDRESS
    )

    assert result == []


def test_get_address_utxos_rejects_non_string(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(TypeError):
        provider.get_address_utxos(123)


def test_get_address_utxos_rejects_empty_address(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_address_utxos("")


def test_get_address_utxos_rejects_whitespace_address(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_address_utxos("   ")


def test_get_address_utxos_rejects_invalid_rpc_result(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value="invalid"
    )

    with pytest.raises(ValueError):
        provider.get_address_utxos(
            VALID_ADDRESS
        )


def test_get_address_utxos_rejects_unsuccessful_scan(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": False,
            "unspents": [],
        }
    )

    with pytest.raises(RuntimeError):
        provider.get_address_utxos(
            VALID_ADDRESS
        )


def test_get_address_utxos_rejects_invalid_unspents(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": "invalid",
        }
    )

    with pytest.raises(ValueError):
        provider.get_address_utxos(
            VALID_ADDRESS
        )


def test_get_address_utxos_rejects_invalid_utxo_record(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": [
                "invalid"
            ],
        }
    )

    with pytest.raises(ValueError):
        provider.get_address_utxos(
            VALID_ADDRESS
        )


###############################################################################
# Address Balance
###############################################################################

def test_get_address_balance(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "searched_items": 100,
            "bestblock": BEST_BLOCK,
            "height": 850000,
            "unspents": [
                {
                    "txid": TXID_1,
                    "vout": 0,
                    "amount": 0.5,
                    "height": 849900,
                    "coinbase": False,
                }
            ],
            "total_amount": 0.5,
        }
    )

    result = provider.get_address_balance(
        VALID_ADDRESS
    )

    assert result["address"] == VALID_ADDRESS
    assert result["asset"] == "BTC"
    assert result["balance_btc"] == 0.5
    assert result["balance_sats"] == 50_000_000
    assert result["utxo_count"] == 1
    assert result["height"] == 850000
    assert result["best_block"] == BEST_BLOCK
    assert len(result["utxos"]) == 1


def test_get_address_balance_converts_btc_to_satoshis(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "height": 100,
            "bestblock": BEST_BLOCK,
            "unspents": [
                {
                    "txid": TXID_1,
                    "vout": 0,
                    "amount": 0.00000001,
                }
            ],
        }
    )

    result = provider.get_address_balance(
        VALID_ADDRESS
    )

    assert result["balance_btc"] == 0.00000001
    assert result["balance_sats"] == 1
    assert result["utxos"][0]["amount_sats"] == 1


def test_get_address_balance_handles_multiple_utxos(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "height": 200,
            "bestblock": BEST_BLOCK,
            "unspents": [
                {
                    "txid": TXID_1,
                    "vout": 0,
                    "amount": 0.25,
                },
                {
                    "txid": TXID_2,
                    "vout": 1,
                    "amount": 0.75,
                },
            ],
        }
    )

    result = provider.get_address_balance(
        VALID_ADDRESS
    )

    assert result["balance_btc"] == 1.0
    assert result["balance_sats"] == 100_000_000
    assert result["utxo_count"] == 2
    assert result["utxos"][0]["amount_sats"] == 25_000_000
    assert result["utxos"][1]["amount_sats"] == 75_000_000


def test_get_address_balance_zero_balance(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "height": 300,
            "bestblock": BEST_BLOCK,
            "unspents": [],
        }
    )

    result = provider.get_address_balance(
        VALID_ADDRESS
    )

    assert result["balance_btc"] == 0.0
    assert result["balance_sats"] == 0
    assert result["utxo_count"] == 0
    assert result["utxos"] == []


def test_get_address_balance_rejects_non_string(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(TypeError):
        provider.get_address_balance(123)


def test_get_address_balance_rejects_empty_address(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_address_balance("")


def test_get_address_balance_rejects_whitespace_address(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(ValueError):
        provider.get_address_balance("   ")


def test_get_address_balance_rejects_invalid_rpc_result(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value="invalid"
    )

    with pytest.raises(ValueError):
        provider.get_address_balance(
            VALID_ADDRESS
        )


def test_get_address_balance_rejects_unsuccessful_scan(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": False,
            "unspents": [],
        }
    )

    with pytest.raises(RuntimeError):
        provider.get_address_balance(
            VALID_ADDRESS
        )


def test_get_address_balance_rejects_invalid_unspents(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": {},
        }
    )

    with pytest.raises(ValueError):
        provider.get_address_balance(
            VALID_ADDRESS
        )


def test_get_address_balance_rejects_invalid_utxo_record(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": [
                "invalid"
            ],
        }
    )

    with pytest.raises(ValueError):
        provider.get_address_balance(
            VALID_ADDRESS
        )


def test_get_address_balance_rejects_invalid_amount_type(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": [
                {
                    "txid": TXID_1,
                    "vout": 0,
                    "amount": None,
                }
            ],
        }
    )

    with pytest.raises(ValueError):
        provider.get_address_balance(
            VALID_ADDRESS
        )


###############################################################################
# RPC Boundary
###############################################################################

def test_get_address_balance_uses_scantxoutset(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "height": 400,
            "bestblock": BEST_BLOCK,
            "unspents": [],
        }
    )

    provider.get_address_balance(
        VALID_ADDRESS
    )

    provider.rpc_call.assert_called_once_with(
        "scantxoutset",
        [
            "start",
            [
                f"addr({VALID_ADDRESS})"
            ],
        ],
    )


def test_get_address_utxos_uses_scantxoutset(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": [],
        }
    )

    provider.get_address_utxos(
        VALID_ADDRESS
    )

    provider.rpc_call.assert_called_once_with(
        "scantxoutset",
        [
            "start",
            [
                f"addr({VALID_ADDRESS})"
            ],
        ],
    )


###############################################################################
# Address Normalization
###############################################################################

def test_address_is_stripped_before_rpc_call(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "unspents": [],
        }
    )

    provider.get_address_utxos(
        f"  {VALID_ADDRESS}  "
    )

    provider.rpc_call.assert_called_once_with(
        "scantxoutset",
        [
            "start",
            [
                f"addr({VALID_ADDRESS})"
            ],
        ],
    )


def test_balance_address_is_stripped(
    provider: BitcoinProvider,
) -> None:
    provider.rpc_call = MagicMock(
        return_value={
            "success": True,
            "height": 500,
            "bestblock": BEST_BLOCK,
            "unspents": [],
        }
    )

    result = provider.get_address_balance(
        f"  {VALID_ADDRESS}  "
    )

    assert result["address"] == VALID_ADDRESS
