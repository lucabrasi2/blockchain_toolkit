"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Block Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable blockchain block information

Not Responsible For
-------------------
✗ Blockchain communication
✗ Consensus logic
✗ Validation
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.ubp_model import UBPModel


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class BlockReport(UBPModel):
    """
    Immutable blockchain block report.
    """

    block_number: int

    block_hash: str

    parent_hash: str

    timestamp: int

    transaction_count: int

    gas_used: int

    gas_limit: int

    miner: str