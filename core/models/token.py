"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Token Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable blockchain token metadata
✓ Store token identity and supply information

Not Responsible For
-------------------
✗ Blockchain communication
✗ Price discovery
✗ Holder analysis
✗ Transfer history
✗ Business logic
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.ubp_model import UBPModel


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class TokenMetadata(UBPModel):
    """
    Immutable blockchain token metadata.

    Attributes
    ----------
    token_address : str
        Token contract address.

    name : str
        Token name.

    symbol : str
        Token ticker symbol.

    decimals : int
        Token precision.

    total_supply_raw : int
        Total supply expressed in the
        smallest blockchain unit.

    total_supply_formatted : str
        Human-readable total supply.
    """

    token_address: str

    name: str

    symbol: str

    decimals: int

    total_supply_raw: int

    total_supply_formatted: str