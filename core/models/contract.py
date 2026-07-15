"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Contract Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable smart contract information
✓ Describe contract classification

Not Responsible For
-------------------
✗ Blockchain communication
✗ Token metadata
✗ Wallet balances
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
class ContractReport(UBPModel):
    """
    Immutable smart contract report.

    Attributes
    ----------
    address : str
        Ethereum address.

    contract_type : str
        Internal contract type identifier.

    classification : str
        Human-readable classification.

    is_contract : bool
        Indicates whether the address is
        a deployed smart contract.

    delegated : bool
        Indicates whether the address is
        an EIP-7702 delegated account.

    bytecode_size : int
        Size of deployed bytecode in bytes.
    """

    address: str

    contract_type: str

    classification: str

    is_contract: bool

    delegated: bool

    bytecode_size: int