"""
===============================================================================
Universal Blockchain Platform (UBP)

Version
-------
0.9.0

Module
------
Network Controller

Author
------
Jaramogi Diddy

Purpose
-------
Handles Ethereum network information requests.

Architectural Intent
--------------------
The controller coordinates user interaction and delegates network operations
to NetworkService. It contains no blockchain access logic.
===============================================================================
"""

from __future__ import annotations

from core.logger import get_logger

from exceptions.blockchain_exceptions import UBPException
from services.ethereum.network_service import NetworkService


logger = get_logger(__name__)


class NetworkController:
    """
    Controller for Ethereum network operations.
    """

    def __init__(self) -> None:
        """Initialize the Network Controller."""

        self.network_service = NetworkService()

        logger.info(
            "NetworkController initialized."
        )

    # =========================================================================
    # Network Information
    # =========================================================================

    def network_information(self) -> None:
        """
        Display Ethereum network information.

        Network data is retrieved through NetworkService and formatted for
        interactive terminal presentation.
        """

        logger.info(
            "Displaying network information."
        )

        try:
            report = self.network_service.get_network_report()

            self._display_network_report(
                report,
            )

            logger.info(
                "Network information displayed."
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
                "Unexpected network error."
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
    def _display_network_report(
        report: dict,
    ) -> None:
        """
        Display the Ethereum network report.

        Parameters
        ----------
        report:
            Network report returned by NetworkService.
        """

        print(
            "\n========== ETHEREUM NETWORK ==========\n"
        )

        print(
            f"Connected      : "
            f"{report['connected']}"
        )

        print(
            f"Chain ID       : "
            f"{report['chain_id']}"
        )

        print(
            f"Latest Block   : "
            f"{report['latest_block']}"
        )

        print(
            f"Gas Price      : "
            f"{report['gas_price_gwei']:.2f} Gwei"
        )

        print(
            f"Client Version : "
            f"{report['client_version']}"
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "NetworkController",
]


# =============================================================================
# End of File
# =============================================================================