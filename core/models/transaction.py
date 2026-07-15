"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Transaction Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable blockchain transaction information

Not Responsible For
-------------------
✗ Blockchain communication
✗ Transaction validation
✗ Business logic
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
class TransactionReport(UBPModel):
    """
    Immutable blockchain transaction report.
    """

    transaction_hash: str

    block_number: int

    from_address: str

    to_address: str

    value: int

    gas_limit: int

    gas_used: int

    gas_price: int

    status: bool