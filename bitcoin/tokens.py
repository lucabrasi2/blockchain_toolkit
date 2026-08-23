"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.tokens

Purpose
-------
Bitcoin asset and token utilities.

Responsibilities
----------------
- Identify BTC as the Bitcoin native asset
- Provide canonical BTC asset metadata
- Preserve the existing token utility interface
- Provide an extensible foundation for future Bitcoin token protocols

Architectural Intent
--------------------
Bitcoin is a native-asset blockchain. BTC is therefore represented as a
native asset rather than as an ERC-20/TRC-20-style token.

Future Bitcoin token protocols can be added through the token-standard
interface without changing the native BTC representation.

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

from typing import Any

from constants.asset_types import (
    BITCOIN,
    BTC,
    NATIVE,
)

from core.logger import get_logger


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Bitcoin Asset Metadata
###############################################################################


def get_native_asset_metadata() -> dict[str, Any]:
    """
    Return canonical metadata for the Bitcoin native asset.

    Returns
    -------
    dict[str, Any]
        Normalized Bitcoin asset metadata.
    """

    return {
        "asset": BTC,
        "symbol": BTC,
        "blockchain": BITCOIN,
        "asset_type": NATIVE,
        "name": "Bitcoin",
        "decimals": 8,
        "is_native": True,
        "is_token": False,
    }


###############################################################################
# Asset Detection
###############################################################################


def is_native_asset(
    asset: str,
) -> bool:
    """
    Determine whether an asset represents native BTC.

    Parameters
    ----------
    asset:
        Asset identifier or symbol.

    Returns
    -------
    bool
        True when the asset is BTC.
    """

    if not isinstance(asset, str):
        return False

    return asset.strip().upper() == BTC


def is_token(
    address: str,
) -> bool:
    """
    Determine whether an address represents a Bitcoin token.

    Bitcoin does not currently expose ERC-20/TRC-20-style token semantics
    through this module.

    This function intentionally remains available for API compatibility
    and future Bitcoin token-standard extensions.

    Parameters
    ----------
    address:
        Token or asset identifier.

    Returns
    -------
    bool
        False for the current Bitcoin implementation.
    """

    logger.debug(
        "Bitcoin token detection requested for %s.",
        address,
    )

    return False


###############################################################################
# Token Metadata Compatibility Interface
###############################################################################


def get_token_metadata(
    address: str,
) -> dict[str, Any]:
    """
    Return Bitcoin token metadata.

    Bitcoin's native BTC asset is not a token. Therefore this function
    preserves the existing token API while clearly identifying BTC as
    a native asset.

    Parameters
    ----------
    address:
        Token address or identifier.

    Returns
    -------
    dict[str, Any]
        Normalized asset metadata.
    """

    return {
        "address": address,
        "name": "Bitcoin",
        "symbol": BTC,
        "decimals": 8,
        "asset": BTC,
        "asset_type": NATIVE,
        "blockchain": BITCOIN,
        "is_native": True,
        "is_token": False,
        "message": (
            "BTC is the native Bitcoin asset, "
            "not a token standard."
        ),
    }


###############################################################################
# Token Supply Compatibility Interface
###############################################################################


def get_total_supply(
    address: str,
) -> None:
    """
    Return token supply information.

    Bitcoin's native supply is blockchain-level data rather than token
    contract data, so this token-specific function does not retrieve it.

    Parameters
    ----------
    address:
        Token address or identifier.

    Returns
    -------
    None
        No token contract supply is available.
    """

    return None


###############################################################################
# Token Balance Compatibility Interface
###############################################################################


def get_token_balance(
    token_address: str,
    wallet_address: str,
) -> None:
    """
    Return a token balance.

    BTC balance retrieval belongs to the Bitcoin wallet/balance layer,
    not the token-contract layer.

    Parameters
    ----------
    token_address:
        Token identifier.
    wallet_address:
        Bitcoin wallet address.

    Returns
    -------
    None
        No Bitcoin token balance is retrieved here.
    """

    return None


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "get_native_asset_metadata",
    "is_native_asset",
    "get_token_metadata",
    "get_total_supply",
    "get_token_balance",
    "is_token",
]


###############################################################################
# End of File
###############################################################################