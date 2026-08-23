"""
===============================================================================
Universal Blockchain Platform (UBP)

Version
-------
0.9.0

Module
------
Transaction Controller

Author
------
Jaramogi Diddy

Purpose
-------
Handles Ethereum transaction exploration.

Architectural Intent
--------------------
The controller coordinates user interaction and delegates transaction
operations to TransactionService. It contains no blockchain access logic.
===============================================================================
"""

from __future__ import annotations

from core.logger import get_logger

from exceptions.blockchain_exceptions import UBPException
from services.ethereum.transaction_service import TransactionService


logger = get_logger(__name__)


class TransactionController:
    """
    Controller responsible for Ethereum transaction operations.
    """

    def __init__(self) -> None:
        """Initialize the Transaction Controller."""

        self.transaction_service = TransactionService()

        logger.info(
            "TransactionController initialized."
        )

    # =========================================================================
    # Transaction Exploration
    # =========================================================================

    def transaction_explorer(self) -> None:
        """
        Display Ethereum transaction information.

        The transaction hash is collected from the user and the transaction
        inspection is delegated to TransactionService.
        """

        logger.info(
            "Transaction Explorer started."
        )

        tx_hash = input(
            "\nEnter Ethereum transaction hash:\n> "
        ).strip()

        try:
            report = self.transaction_service.get_transaction_report(
                tx_hash,
            )

            self._display_transaction_report(
                report,
            )

            logger.info(
                "Transaction information displayed successfully."
            )

        except UBPException as error:
            logger.error(
                str(error),
            )

            print(
                f"\n❌ {error}",
            )

        except Exception as error:
            logger.exception(
                "Unexpected transaction explorer error."
            )

            print(
                f"\nUnexpected Error: {error}",
            )

        finally:
            input(
                "\nPress Enter to continue..."
            )

    # =========================================================================
    # Presentation
    # =========================================================================

    @staticmethod
    def _display_transaction_report(
        report: dict,
    ) -> None:
        """
        Display an Ethereum transaction report.

        Parameters
        ----------
        report:
            Transaction report returned by TransactionService.
        """

        print(
            "\n========== TRANSACTION REPORT ==========\n"
        )

        print(
            f"Hash              : "
            f"{report['hash']}"
        )

        print(
            f"Block Number      : "
            f"{report['block_number']}"
        )

        print(
            f"From              : "
            f"{report['from']}"
        )

        print(
            f"To                : "
            f"{report['to']}"
        )

        print(
            f"Value             : "
            f"{report['value_eth']} ETH"
        )

        print(
            f"Value (Wei)       : "
            f"{report['value_wei']}"
        )

        print(
            f"Gas Limit         : "
            f"{report['gas']}"
        )

        print(
            f"Gas Price         : "
            f"{report['gas_price']} Wei"
        )

        print(
            f"Gas Used          : "
            f"{report['gas_used']}"
        )

        print(
            f"Nonce             : "
            f"{report['nonce']}"
        )

        print(
            f"Status            : "
            f"{'Success' if report['status'] == 1 else 'Failed'}"
        )

        if report["contract_address"]:
            print(
                f"Contract Address  : "
                f"{report['contract_address']}"
            )

        print(
            f"Logs              : "
            f"{report['logs']}"
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "TransactionController",
]


# =============================================================================
# End of File
# =============================================================================