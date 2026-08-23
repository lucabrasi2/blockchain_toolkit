"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_bitcoin_tokens

Purpose
-------
Tests for Bitcoin asset and token utilities.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)
===============================================================================
"""

from bitcoin.tokens import (
    get_native_asset_metadata,
    get_token_metadata,
    get_total_supply,
    get_token_balance,
    is_native_asset,
    is_token,
)


# =============================================================================
# Native Asset Tests
# =============================================================================


def test_get_native_asset_metadata():
    """Verify canonical BTC metadata."""

    metadata = get_native_asset_metadata()

    assert metadata["asset"] == "BTC"
    assert metadata["symbol"] == "BTC"
    assert metadata["blockchain"] == "bitcoin"
    assert metadata["asset_type"] == "native"
    assert metadata["name"] == "Bitcoin"
    assert metadata["decimals"] == 8
    assert metadata["is_native"] is True
    assert metadata["is_token"] is False


def test_is_native_asset():
    """Verify BTC is recognized as a native asset."""

    assert is_native_asset("BTC") is True
    assert is_native_asset("btc") is True
    assert is_native_asset(" BtC ") is True


def test_other_assets_are_not_bitcoin_native_asset():
    """Verify other assets are not classified as BTC."""

    assert is_native_asset("ETH") is False
    assert is_native_asset("TRX") is False
    assert is_native_asset("ERC20") is False
    assert is_native_asset("TRC20") is False


def test_invalid_native_asset_values():
    """Verify invalid BTC asset values are rejected."""

    assert is_native_asset("") is False
    assert is_native_asset(None) is False
    assert is_native_asset(123) is False


# =============================================================================
# Compatibility Token Interface
# =============================================================================


def test_bitcoin_is_not_token():
    """Verify Bitcoin is not represented as a token."""

    assert is_token("BTC") is False
    assert is_token("some-token") is False


def test_get_token_metadata_identifies_btc_as_native():
    """Verify compatibility metadata correctly identifies BTC."""

    metadata = get_token_metadata("BTC")

    assert metadata["symbol"] == "BTC"
    assert metadata["asset"] == "BTC"
    assert metadata["asset_type"] == "native"
    assert metadata["blockchain"] == "bitcoin"
    assert metadata["decimals"] == 8
    assert metadata["is_native"] is True
    assert metadata["is_token"] is False


def test_token_supply_is_not_contract_supply():
    """Verify Bitcoin token supply interface remains empty."""

    assert get_total_supply("BTC") is None


def test_token_balance_is_not_contract_balance():
    """Verify Bitcoin token balance interface remains empty."""

    assert (
        get_token_balance(
            "BTC",
            "bc1example",
        )
        is None
    )
