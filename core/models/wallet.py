"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Wallet Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent a blockchain wallet balance
✓ Store immutable wallet information

Not Responsible For
-------------------
✗ Blockchain communication
✗ Balance calculation
✗ Validation
✗ Formatting
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.ubp_model import UBPModel


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class WalletBalance(UBPModel):
    """
    Immutable wallet balance model.

    Attributes
    ----------
    address : str
        Wallet address.

    ether : float
        Native currency balance in Ether.

    wei : int
        Native currency balance in Wei.

    nonce : int
        Current transaction count.
    """

    address: str

    ether: float

    wei: int

    nonce: int