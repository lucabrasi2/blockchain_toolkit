"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : UBP Domain Model
Author  : Jaramogi Diddy

Architecture Layer
------------------
Core Domain Model

Responsibilities
----------------
✓ Represent immutable domain objects
✓ Provide serialization
✓ Provide JSON conversion
✓ Provide cloning
✓ Provide consistent string representation

Not Responsible For
-------------------
✗ Business logic
✗ Validation
✗ Blockchain communication
✗ Persistence
✗ Formatting
"""

from __future__ import annotations

import json

from dataclasses import (
    asdict,
    dataclass,
    replace,
)

from typing import (
    Any,
    Type,
    TypeVar,
)

from core.logger import get_logger


logger = get_logger(__name__)

T = TypeVar("T", bound="UBPModel")


@dataclass(
    frozen=True,
    slots=True,
    kw_only=True,
)
class UBPModel:
    """
    Base class for every immutable
    domain model in UBP.

    All domain models inherit the
    following capabilities:

    • Dictionary serialization

    • JSON serialization

    • Immutable cloning

    • Readable string representation
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this model into
        a dictionary.

        Returns
        -------
        dict
            Dictionary representation.
        """

        logger.debug(
            "Serializing %s to dictionary.",
            self.__class__.__name__,
        )

        return asdict(self)

    def to_json(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        Convert this model into JSON.

        Parameters
        ----------
        indent : int
            JSON indentation.

        Returns
        -------
        str
            JSON representation.
        """

        logger.debug(
            "Serializing %s to JSON.",
            self.__class__.__name__,
        )

        return json.dumps(
            self.to_dict(),
            indent=indent,
            default=str,
        )

    @classmethod
    def from_dict(
        cls: Type[T],
        data: dict[str, Any],
    ) -> T:
        """
        Create a model from a dictionary.

        Parameters
        ----------
        data : dict

        Returns
        -------
        UBPModel
        """

        logger.debug(
            "Creating %s from dictionary.",
            cls.__name__,
        )

        return cls(**data)

    def clone(
        self: T,
        **changes: Any,
    ) -> T:
        """
        Return a copy of this model
        with updated fields.

        Example
        -------
        wallet = wallet.clone(
            ether=10.5
        )
        """

        logger.debug(
            "Cloning %s.",
            self.__class__.__name__,
        )

        return replace(
            self,
            **changes,
        )

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"({self.to_dict()})"
        )

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return self.__str__()