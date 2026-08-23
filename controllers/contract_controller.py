"""
===============================================================================
Universal Blockchain Platform (UBP)

Version
-------
2.0.0

Module
------
Smart Contract Controller

Architectural Intent
--------------------
The controller layer manages user interaction only.

Responsibilities
----------------
- Receive user input
- Call ContractService
- Display formatted results
- Handle presentation errors

The controller contains NO blockchain logic.
===============================================================================
"""

from __future__ import annotations

from core.formatter import Formatter
from core.logger import get_logger

from constants.contract_types import ERC20
from exceptions.blockchain_exceptions import UBPException
from services.ethereum.contract_service import ContractService


logger = get_logger(__name__)


class ContractController:
    """
    Smart Contract Inspector Controller.

    This controller is responsible only for coordinating user interaction,
    delegating contract analysis to ContractService, and presenting the
    resulting report.
    """

    def __init__(self) -> None:
        """Initialize the Smart Contract Controller."""

        logger.info(
            "Initializing ContractController."
        )

        self.contract_service = ContractService()

    # =========================================================================
    # Public Operations
    # =========================================================================

    def contract_inspector(self) -> None:
        """
        Launch the Smart Contract Inspector.

        The controller collects the Ethereum address, delegates inspection
        to ContractService, and displays the resulting report.
        """

        logger.info(
            "Smart Contract Inspector started."
        )

        address = input(
            "\nEnter Ethereum address:\n> "
        ).strip()

        try:
            report = self.contract_service.get_contract_report(
                address,
            )

            self._display_report(
                report,
            )

            logger.info(
                "Smart Contract report displayed successfully."
            )

        except UBPException as error:
            logger.error(
                str(error),
            )

            print(
                Formatter.error(
                    str(error),
                ),
            )

        except Exception as error:
            logger.exception(
                "Unexpected Smart Contract Inspector error."
            )

            print(
                Formatter.error(
                    f"Unexpected Error:\n{error}",
                ),
            )

        finally:
            input(
                "\nPress Enter to continue..."
            )

    # =========================================================================
    # Presentation
    # =========================================================================

    def _display_report(
        self,
        report: dict,
    ) -> None:
        """
        Display a formatted smart contract report.

        Parameters
        ----------
        report:
            Contract report returned by ContractService.
        """

        print(
            Formatter.title(
                "SMART CONTRACT REPORT",
            ),
        )

        self._display_general_section(
            report,
        )

        if report.get("contract_type") == ERC20:
            self._display_asset_section(
                report,
            )

        self._display_blockchain_section(
            report,
        )

    def _display_general_section(
        self,
        report: dict,
    ) -> None:
        """Display general contract information."""

        print(
            Formatter.section(
                "General",
            ),
        )

        print(
            Formatter.field(
                "Address",
                report.get(
                    "address",
                    "N/A",
                ),
            ),
        )

        print(
            Formatter.field(
                "Contract",
                Formatter.yes_no(
                    report.get(
                        "is_contract",
                        False,
                    ),
                ),
            ),
        )

        print(
            Formatter.field(
                "Classification",
                report.get(
                    "classification",
                    "UNKNOWN",
                ),
            ),
        )

    def _display_asset_section(
        self,
        report: dict,
    ) -> None:
        """Display ERC20 asset information."""

        print(
            Formatter.section(
                "Asset Information",
            ),
        )

        print(
            Formatter.field(
                "Name",
                report.get(
                    "name",
                    "N/A",
                ),
            ),
        )

        print(
            Formatter.field(
                "Symbol",
                report.get(
                    "symbol",
                    "N/A",
                ),
            ),
        )

        print(
            Formatter.field(
                "Decimals",
                report.get(
                    "decimals",
                    "N/A",
                ),
            ),
        )

        print(
            Formatter.field(
                "Total Supply",
                report.get(
                    "supply_formatted",
                    "N/A",
                ),
            ),
        )

    def _display_blockchain_section(
        self,
        report: dict,
    ) -> None:
        """Display blockchain-level contract information."""

        print(
            Formatter.section(
                "Blockchain",
            ),
        )

        print(
            Formatter.field(
                "ETH Balance",
                Formatter.format_eth(
                    report.get(
                        "balance_eth",
                        0,
                    ),
                ),
            ),
        )

        print(
            Formatter.field(
                "Nonce",
                Formatter.format_number(
                    report.get(
                        "nonce",
                        0,
                    ),
                ),
            ),
        )

        print(
            Formatter.field(
                "Bytecode Size",
                Formatter.format_bytes(
                    report.get(
                        "bytecode_size",
                        0,
                    ),
                ),
            ),
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "ContractController",
]


# =============================================================================
# End of File
# =============================================================================