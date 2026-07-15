"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Network Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable blockchain network information

Not Responsible For
-------------------
✗ Provider management
✗ Blockchain communication
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
class NetworkInfo(UBPModel):
    """
    Immutable blockchain network information.
    """

    chain_id: int

    network_name: str

    provider_name: str

    client_version: str

    latest_block: int

    connected: bool