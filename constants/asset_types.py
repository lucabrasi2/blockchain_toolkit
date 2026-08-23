"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
constants.asset_types

Purpose
-------
Canonical asset and token-standard definitions for UBP.

Responsibilities
----------------
- Define native blockchain assets
- Define supported token standards
- Provide stable asset-type identifiers
- Support future token-standard extensions

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


# =============================================================================
# Asset Types
# =============================================================================

NATIVE = "native"
TOKEN = "token"


# =============================================================================
# Native Assets
# =============================================================================

ETH = "ETH"
BTC = "BTC"
TRX = "TRX"


# =============================================================================
# Token Standards
# =============================================================================

ERC20 = "ERC20"
TRC20 = "TRC20"


# =============================================================================
# Blockchain Identifiers
# =============================================================================

ETHEREUM = "ethereum"
BITCOIN = "bitcoin"
TRON = "tron"


# =============================================================================
# Supported Native Assets
# =============================================================================

NATIVE_ASSETS = {
    ETHEREUM: ETH,
    BITCOIN: BTC,
    TRON: TRX,
}


# =============================================================================
# Supported Token Standards
# =============================================================================

TOKEN_STANDARDS = {
    ERC20: ETHEREUM,
    TRC20: TRON,
}


# =============================================================================
# Standard Metadata
# =============================================================================

TOKEN_STANDARD_METADATA = {
    ERC20: {
        "blockchain": ETHEREUM,
        "asset_type": TOKEN,
        "name": "Ethereum Request for Comment 20",
    },

    TRC20: {
        "blockchain": TRON,
        "asset_type": TOKEN,
        "name": "TRON Request for Comment 20",
    },
}


# =============================================================================
# Supported Assets
# =============================================================================

SUPPORTED_NATIVE_ASSETS = {
    ETH,
    BTC,
    TRX,
}


SUPPORTED_TOKEN_STANDARDS = {
    ERC20,
    TRC20,
}


# =============================================================================
# Helpers
# =============================================================================

def get_native_asset(
    blockchain: str,
) -> str:
    """
    Return the canonical native asset for a blockchain.

    Parameters
    ----------
    blockchain:
        Blockchain identifier.

    Returns
    -------
    str
        Native asset symbol.

    Raises
    ------
    ValueError
        If the blockchain is unsupported.
    """

    blockchain = blockchain.strip().lower()

    try:
        return NATIVE_ASSETS[blockchain]

    except KeyError as error:
        raise ValueError(
            f"Unsupported blockchain: {blockchain}"
        ) from error


def is_native_asset(
    asset: str,
) -> bool:
    """
    Determine whether an asset is a supported native asset.
    """

    if not isinstance(asset, str):
        return False

    return asset.upper() in SUPPORTED_NATIVE_ASSETS


def is_token_standard(
    standard: str,
) -> bool:
    """
    Determine whether a token standard is supported.
    """

    if not isinstance(standard, str):
        return False

    return standard.upper() in SUPPORTED_TOKEN_STANDARDS


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "NATIVE",
    "TOKEN",

    "ETH",
    "BTC",
    "TRX",

    "ERC20",
    "TRC20",

    "ETHEREUM",
    "BITCOIN",
    "TRON",

    "NATIVE_ASSETS",
    "TOKEN_STANDARDS",
    "TOKEN_STANDARD_METADATA",

    "SUPPORTED_NATIVE_ASSETS",
    "SUPPORTED_TOKEN_STANDARDS",

    "get_native_asset",
    "is_native_asset",
    "is_token_standard",
]


###############################################################################
# End of File
###############################################################################
