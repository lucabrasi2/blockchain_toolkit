"""
Universal Blockchain Platform (UBP)

## Module

services.tron.block_service

## Purpose

Business logic for TRON block operations.

## Responsibilities

• Retrieve TRON blocks
• Retrieve the latest TRON block
• Generate controller-friendly block reports
• Keep blockchain communication outside the controller

## Architecture

Controller
    ↓
TronBlockService
    ↓
tron.blocks

## Author

Jaramogi Diddy

## Project

Universal Blockchain Platform (UBP)

## Version

2.0 Enterprise
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from tron.blocks import (
    get_block,
)

logger = get_logger(__name__)


class TronBlockService:
    """
    TRON block business logic service.

    This service is responsible for retrieving
    and formatting TRON block information.

    The controller must not communicate directly
    with the tron.blocks module.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the TRON Block Service.
        """

        logger.info(
            "TronBlockService initialized."
        )

    ###########################################################################
    # Block Report
    ###########################################################################

    def get_block_report(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Generate a TRON block report.

        Parameters
        ----------
        block_identifier : str | int
            TRON block number, block hash,
            or supported block identifier.

        Returns
        -------
        dict[str, Any]
            Controller-friendly block report.
        """

        logger.info(
            "Generating TRON block report for: %s",
            block_identifier,
        )

        try:
            ###################################################################
            # Retrieve blockchain block
            ###################################################################

            block = get_block(
                block_identifier
            )

            ###################################################################
            # Handle blockchain-level errors
            ###################################################################

            if not isinstance(
                block,
                dict,
            ):

                logger.warning(
                    "Unexpected TRON block response."
                )

                return {
                    "identifier": block_identifier,
                    "error": (
                        "Invalid block response."
                    ),
                }

            if block.get("error"):

                logger.warning(
                    "Unable to retrieve TRON block: %s",
                    block.get("error"),
                )

                return {
                    "identifier": block_identifier,
                    "error": block.get(
                        "error"
                    ),
                }

            #######################################################################
            # Build controller-friendly report
            #######################################################################

            report = {
                "number": block.get(
                    "number",
                ),

                "hash": block.get(
                    "hash",
                ),

                "parent_hash": block.get(
                    "parent_hash",
                    block.get("previous_hash"),
                ),

                "timestamp": block.get(
                    "timestamp",
                ),

                "transaction_count": block.get(
                    "transaction_count",
                    len(
                        block.get(
                            "transactions",
                            [],
                        )
                    ),
                ),

                "size": block.get(
                    "size",
                ),

                "version": block.get(
                    "version",
                ),

                "witness": block.get(
                    "witness",
                ),

                "tx_trie": block.get(
                    "tx_trie",
                ),

                "transactions": (
                    block.get(
                        "transactions",
                        [],
                    )[:10]
                ),
            }

            logger.info(
                "TRON block report generated successfully "
                "for block %s.",
                report.get(
                    "number",
                ),
            )

            return report

        except Exception as exc:
            logger.exception(
                "Failed to generate TRON block report."
            )
            return {
                "identifier": block_identifier,
                "error": str(exc),
            }

    ###########################################################################
    # Latest Block
    ###########################################################################

    def get_latest_block_report(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest TRON block report.

        Returns
        -------
        dict[str, Any]
            Latest TRON block report.
        """

        logger.info(
            "Retrieving latest TRON block report."
        )

        return self.get_block_report(
            "latest",
        )

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}()"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TronBlockService",
]


###############################################################################
# End of File
###############################################################################