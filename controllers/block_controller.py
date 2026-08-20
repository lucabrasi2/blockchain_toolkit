"""
===============================================================================
Universal Blockchain Platform (UBP)

Version
-------
0.9.0

Module
------
Block Controller

Purpose
-------
Handles Ethereum block exploration.

Author
------
Jaramogi Diddy
===============================================================================
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from exceptions.blockchain_exceptions import UBPException
from services.ethereum.block_service import BlockService


logger = get_logger(__name__)


# =============================================================================
# Block Controller
# =============================================================================


class BlockController:
    """
    Controller responsible for Ethereum block operations.

    The controller handles user interaction and delegates Ethereum block
    retrieval to ``BlockService``.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the Block Controller."""
        self.block_service = BlockService()

        logger.info(
            "BlockController initialized."
        )

    # =========================================================================
    # Block Input
    # =========================================================================

    @staticmethod
    def _get_block_input() -> str:
        """
        Prompt the user for an Ethereum block number.

        Returns
        -------
        str
            User-provided block input with surrounding whitespace removed.
        """
        return input(
            "\nEnter Ethereum block number\n"
            "(leave blank for latest block):\n> "
        ).strip()

    # =========================================================================
    # Block Retrieval
    # =========================================================================

    def _get_block_report(
        self,
        block_input: str,
    ) -> dict[str, Any]:
        """
        Retrieve the requested Ethereum block report.

        Parameters
        ----------
        block_input:
            User-provided block input.

        Returns
        -------
        dict[str, Any]
            Ethereum block report.

        Raises
        ------
        ValueError
            If the supplied block number is not an integer.
        """
        if not block_input:
            return self.block_service.get_latest_block_report()

        block_number = int(block_input)

        return self.block_service.get_block_report(
            block_number
        )

    # =========================================================================
    # Block Display
    # =========================================================================

    @staticmethod
    def _display_block_report(
        report: dict[str, Any],
    ) -> None:
        """
        Display an Ethereum block report.

        Parameters
        ----------
        report:
            Block report returned by ``BlockService``.
        """
        print(
            "\n========== BLOCK REPORT ==========\n"
        )

        print(
            f"Block Number     : {report['number']}"
        )

        print(
            f"Hash             : {report['hash']}"
        )

        print(
            f"Parent Hash      : {report['parent_hash']}"
        )

        print(
            f"Timestamp        : {report['timestamp']}"
        )

        print(
            "Transactions     : "
            f"{report['transaction_count']}"
        )

        print(
            f"Gas Used         : {report['gas_used']}"
        )

        print(
            f"Gas Limit        : {report['gas_limit']}"
        )

        if report["base_fee"] is not None:
            print(
                "Base Fee         : "
                f"{report['base_fee']} Wei"
            )

        print(
            f"Block Size       : {report['size']} bytes"
        )

    # =========================================================================
    # Block Explorer
    # =========================================================================

    def block_explorer(self) -> None:
        """
        Display Ethereum block information.

        The user may enter a block number or leave the input blank to
        retrieve the latest block.
        """
        logger.info(
            "Block Explorer started."
        )

        try:
            block_input = self._get_block_input()

            report = self._get_block_report(
                block_input
            )

            self._display_block_report(
                report
            )

            logger.info(
                "Displayed block #%s.",
                report["number"],
            )

        except ValueError:
            logger.warning(
                "Invalid block number entered."
            )

            print(
                "\n❌ Block number must be an integer."
            )

        except UBPException as error:
            logger.error(
                "%s",
                error,
            )

            print(
                f"\n❌ {error}"
            )

        except Exception as error:
            logger.exception(
                "Unexpected block explorer error."
            )

            print(
                f"\nUnexpected Error: {error}"
            )

        input(
            "\nPress Enter to continue..."
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "BlockController",
]


# =============================================================================
# End of File
# =============================================================================