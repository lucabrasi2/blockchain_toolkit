"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Inspection Report
Author  : Jaramogi Diddy

Architecture Layer
------------------
Report Model

Responsibilities
----------------
✓ Represent the complete result of a blockchain inspection
✓ Compose multiple immutable domain models
✓ Provide a single return object for inspection services

Not Responsible For
-------------------
✗ Blockchain communication
✗ Business logic
✗ Validation
✗ Formatting
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.models.ubp_model import UBPModel

from core.models.contract import ContractReport
from core.models.wallet import WalletBalance
from core.models.token import TokenMetadata
from core.models.network import NetworkInfo

from core.models.reports.inspection_metadata import (
    InspectionMetadata,
)


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class InspectionReport(UBPModel):
    """
    Complete immutable blockchain
    inspection report.

    Attributes
    ----------
    report_id : str
        Unique report identifier.

    metadata : InspectionMetadata
        Report metadata.

    network : NetworkInfo
        Network information.

    contract : ContractReport
        Contract information.

    wallet : WalletBalance
        Wallet information.

    token : TokenMetadata | None
        Token metadata when applicable.
    """

    report_id: str

    metadata: InspectionMetadata

    network: NetworkInfo

    contract: ContractReport

    wallet: WalletBalance

    token: Optional[TokenMetadata] = None
