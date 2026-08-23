"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_asset_types

Purpose
-------
Tests for the canonical UBP asset and token-standard definitions.

Coverage
--------
- Native assets
- ERC-20
- TRC-20
- Native asset lookup
- Native asset detection
- Token-standard detection
- Unsupported blockchain handling

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)
===============================================================================
"""

import pytest

from constants.asset_types import (
    NATIVE,
    TOKEN,
    ETH,
    BTC,
    TRX,
    ERC20,
    TRC20,
    ETHEREUM,
    BITCOIN,
    TRON,
    NATIVE_ASSETS,
    TOKEN_STANDARDS,
    TOKEN_STANDARD_METADATA,
    SUPPORTED_NATIVE_ASSETS,
    SUPPORTED_TOKEN_STANDARDS,
    get_native_asset,
    is_native_asset,
    is_token_standard,
)


# =============================================================================
# Asset Type Tests
# =============================================================================


def test_asset_type_constants():
    """Verify the canonical asset-type identifiers."""

    assert NATIVE == "native"
    assert TOKEN == "token"


def test_native_asset_constants():
    """Verify supported native blockchain assets."""

    assert ETH == "ETH"
    assert BTC == "BTC"
    assert TRX == "TRX"


def test_token_standard_constants():
    """Verify supported token standards."""

    assert ERC20 == "ERC20"
    assert TRC20 == "TRC20"


# =============================================================================
# Native Asset Mapping
# =============================================================================


def test_native_asset_mapping():
    """Verify blockchain-to-native-asset mapping."""

    assert NATIVE_ASSETS[ETHEREUM] == ETH
    assert NATIVE_ASSETS[BITCOIN] == BTC
    assert NATIVE_ASSETS[TRON] == TRX


def test_get_native_asset():
    """Verify native asset lookup."""

    assert get_native_asset("ethereum") == ETH
    assert get_native_asset("bitcoin") == BTC
    assert get_native_asset("tron") == TRX


def test_get_native_asset_is_case_insensitive():
    """Verify blockchain lookup accepts mixed case."""

    assert get_native_asset("Ethereum") == ETH
    assert get_native_asset("BITCOIN") == BTC
    assert get_native_asset("TrOn") == TRX


def test_get_native_asset_rejects_unsupported_blockchain():
    """Verify unsupported blockchains raise ValueError."""

    with pytest.raises(ValueError):
        get_native_asset("unsupported")


# =============================================================================
# Native Asset Detection
# =============================================================================


def test_is_native_asset():
    """Verify native asset detection."""

    assert is_native_asset(ETH) is True
    assert is_native_asset(BTC) is True
    assert is_native_asset(TRX) is True


def test_is_native_asset_is_case_insensitive():
    """Verify native asset detection accepts lowercase symbols."""

    assert is_native_asset("eth") is True
    assert is_native_asset("btc") is True
    assert is_native_asset("trx") is True


def test_token_standards_are_not_native_assets():
    """Verify token standards are not classified as native assets."""

    assert is_native_asset(ERC20) is False
    assert is_native_asset(TRC20) is False


def test_invalid_native_asset_values():
    """Verify invalid values are rejected."""

    assert is_native_asset("USDT") is False
    assert is_native_asset("USDC") is False
    assert is_native_asset("") is False
    assert is_native_asset(None) is False


# =============================================================================
# Token Standard Mapping
# =============================================================================


def test_token_standard_mapping():
    """Verify token-standard blockchain mapping."""

    assert TOKEN_STANDARDS[ERC20] == ETHEREUM
    assert TOKEN_STANDARDS[TRC20] == TRON


def test_supported_token_standards():
    """Verify currently supported token standards."""

    assert ERC20 in SUPPORTED_TOKEN_STANDARDS
    assert TRC20 in SUPPORTED_TOKEN_STANDARDS


def test_is_token_standard():
    """Verify token-standard detection."""

    assert is_token_standard(ERC20) is True
    assert is_token_standard(TRC20) is True


def test_is_token_standard_is_case_insensitive():
    """Verify token-standard detection accepts mixed case."""

    assert is_token_standard("erc20") is True
    assert is_token_standard("trc20") is True


def test_native_assets_are_not_token_standards():
    """Verify native assets are not token standards."""

    assert is_token_standard(ETH) is False
    assert is_token_standard(BTC) is False
    assert is_token_standard(TRX) is False


def test_invalid_token_standards():
    """Verify unsupported token standards are rejected."""

    assert is_token_standard("ERC721") is False
    assert is_token_standard("ERC1155") is False
    assert is_token_standard("BEP20") is False
    assert is_token_standard("") is False
    assert is_token_standard(None) is False


# =============================================================================
# Metadata Tests
# =============================================================================


def test_erc20_metadata():
    """Verify ERC-20 standard metadata."""

    metadata = TOKEN_STANDARD_METADATA[ERC20]

    assert metadata["blockchain"] == ETHEREUM
    assert metadata["asset_type"] == TOKEN
    assert metadata["name"] == (
        "Ethereum Request for Comment 20"
    )


def test_trc20_metadata():
    """Verify TRC-20 standard metadata."""

    metadata = TOKEN_STANDARD_METADATA[TRC20]

    assert metadata["blockchain"] == TRON
    assert metadata["asset_type"] == TOKEN
    assert metadata["name"] == (
        "TRON Request for Comment 20"
    )


# =============================================================================
# Supported Native Assets
# =============================================================================


def test_supported_native_assets():
    """Verify all canonical native assets are supported."""

    assert ETH in SUPPORTED_NATIVE_ASSETS
    assert BTC in SUPPORTED_NATIVE_ASSETS
    assert TRX in SUPPORTED_NATIVE_ASSETS


def test_supported_native_asset_count():
    """Verify the current native-asset set."""

    assert SUPPORTED_NATIVE_ASSETS == {
        ETH,
        BTC,
        TRX,
    }
