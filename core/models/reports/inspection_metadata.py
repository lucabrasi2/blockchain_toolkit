"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Inspection Metadata
Author  : Jaramogi Diddy

Architecture Layer
------------------
Report Model

Responsibilities
----------------
✓ Store report generation metadata
✓ Store execution metrics
✓ Store framework information

Not Responsible For
-------------------
✗ Blockchain communication
✗ Business logic
✗ Report generation
✗ Formatting
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.models.ubp_model import UBPModel


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class InspectionMetadata(UBPModel):
    """
    Immutable metadata associated with
    an inspection report.

    Attributes
    ----------
    provider_name : str
        Blockchain provider name.

    provider_version : str
        Provider implementation version.

    ubp_version : str
        Current UBP version.

    execution_time_ms : float
        Total execution time.

    generated_at : datetime
        Report generation timestamp.
    """

    provider_name: str

    provider_version: str

    ubp_version: str

    execution_time_ms: float

    generated_at: datetime