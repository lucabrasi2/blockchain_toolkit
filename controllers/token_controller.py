"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
controllers.token_controller

Purpose
-------
Cross-chain asset and token controller for UBP.

Responsibilities
----------------
- Provide user-facing token inspection
- Support native assets
- Support ERC-20 tokens
- Support TRC-20 tokens
- Delegate blockchain operations to TokenService
- Keep presentation logic separate from blockchain logic

Architectural Intent
--------------------
The controller contains no direct blockchain access logic.

All blockchain and token operations are delegated to the cross-chain
TokenService.

Supported Native Assets
-----------------------
- ETH
- BTC
- TRX

Supported Token Standards
-------------------------
- ERC20
- TRC20

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

from typing import Any

from core.formatter import Formatter
from core.logger import get_logger

from exceptions.blockchain_exceptions import UBPException

from services.token_service import TokenService


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Token Controller
###############################################################################


class TokenController:
    """
    Cross-chain asset and token controller.

    The controller coordinates user interaction and delegates all asset/token
    operations to TokenService.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Token Controller.
        """

        self.token_service = TokenService()

        logger.info(
            "TokenController initialized."
        )

    ###########################################################################
    # Token Inspector
    ###########################################################################

    def token_inspector(self) -> None:
        """
        Display an interactive token inspection menu.

        The user can inspect:

        - Ethereum native asset
        - Bitcoin native asset
        - TRON native asset
        - ERC-20 token
        - TRC-20 token
        """

        logger.info(
            "Token Inspector started."
        )

        try:

            print(
                Formatter.title(
                    "ASSET & TOKEN INSPECTOR"
                )
            )

            print(
                "\n1. Ethereum (ETH)"
            )

            print(
                "2. Bitcoin (BTC)"
            )

            print(
                "3. TRON (TRX)"
            )

            print(
                "4. ERC-20 Token"
            )

            print(
                "5. TRC-20 Token"
            )

            print(
                "0. Back"
            )

            choice = input(
                "\nSelect an option:\n> "
            ).strip()

            ###################################################################
            # Native Ethereum
            ###################################################################

            if choice == "1":

                report = (
                    self.token_service.get_native_asset_info(
                        "ethereum"
                    )
                )

                self._display_asset_report(
                    report
                )

            ###################################################################
            # Native Bitcoin
            ###################################################################

            elif choice == "2":

                report = (
                    self.token_service.get_native_asset_info(
                        "bitcoin"
                    )
                )

                self._display_asset_report(
                    report
                )

            ###################################################################
            # Native TRON
            ###################################################################

            elif choice == "3":

                report = (
                    self.token_service.get_native_asset_info(
                        "tron"
                    )
                )

                self._display_asset_report(
                    report
                )

            ###################################################################
            # ERC-20
            ###################################################################

            elif choice == "4":

                self._inspect_erc20()

            ###################################################################
            # TRC-20
            ###################################################################

            elif choice == "5":

                self._inspect_trc20()

            ###################################################################
            # Exit
            ###################################################################

            elif choice == "0":

                logger.info(
                    "Token Inspector closed."
                )

                return

            ###################################################################
            # Invalid option
            ###################################################################

            else:

                print(
                    Formatter.error(
                        "Invalid selection."
                    )
                )

        except UBPException as error:

            logger.error(
                str(error)
            )

            print(
                Formatter.error(
                    str(error)
                )
            )

        except Exception as error:

            logger.exception(
                "Unexpected Token Inspector error."
            )

            print(
                Formatter.error(
                    f"Unexpected Error:\n{error}"
                )
            )

        finally:

            input(
                "\nPress Enter to continue..."
            )

    ###########################################################################
    # ERC-20 Inspection
    ###########################################################################

    def _inspect_erc20(self) -> None:
        """
        Inspect an ERC-20 token.
        """

        contract_address = input(
            "\nEnter ERC-20 contract address:\n> "
        ).strip()

        if not contract_address:

            print(
                Formatter.error(
                    "Token contract address is required."
                )
            )

            return

        logger.info(
            "Inspecting ERC-20 token: %s",
            contract_address,
        )

        report = (
            self.token_service.resolve_asset(
                blockchain="ethereum",
                standard="ERC20",
                address=contract_address,
            )
        )

        self._display_token_report(
            report
        )

    ###########################################################################
    # TRC-20 Inspection
    ###########################################################################

    def _inspect_trc20(self) -> None:
        """
        Inspect a TRC-20 token.
        """

        contract_address = input(
            "\nEnter TRC-20 contract address:\n> "
        ).strip()

        if not contract_address:

            print(
                Formatter.error(
                    "Token contract address is required."
                )
            )

            return

        logger.info(
            "Inspecting TRC-20 token: %s",
            contract_address,
        )

        report = (
            self.token_service.resolve_asset(
                blockchain="tron",
                standard="TRC20",
                address=contract_address,
            )
        )

        self._display_token_report(
            report
        )

    ###########################################################################
    # Native Asset Presentation
    ###########################################################################

    @staticmethod
    def _display_asset_report(
        report: dict[str, Any],
    ) -> None:
        """
        Display a normalized native asset report.
        """

        print(
            Formatter.title(
                "NATIVE ASSET REPORT"
            )
        )

        print(
            Formatter.field(
                "Asset",
                report.get(
                    "asset",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Blockchain",
                report.get(
                    "blockchain",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Asset Type",
                report.get(
                    "asset_type",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Native Asset",
                report.get(
                    "is_native",
                    False,
                ),
            )
        )

        print(
            Formatter.field(
                "Token",
                report.get(
                    "is_token",
                    False,
                ),
            )
        )

    ###########################################################################
    # Token Presentation
    ###########################################################################

    @staticmethod
    def _display_token_report(
        report: dict[str, Any],
    ) -> None:
        """
        Display a normalized token report.

        The method accepts both ERC-20 and TRC-20 reports.
        """

        print(
            Formatter.title(
                "TOKEN REPORT"
            )
        )

        print(
            Formatter.field(
                "Contract Address",
                report.get(
                    "address",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Blockchain",
                report.get(
                    "blockchain",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Token Standard",
                report.get(
                    "standard",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Token Name",
                report.get(
                    "name",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Symbol",
                report.get(
                    "symbol",
                    "Unknown",
                ),
            )
        )

        print(
            Formatter.field(
                "Decimals",
                report.get(
                    "decimals",
                    0,
                ),
            )
        )

        #######################################################################
        # Optional total supply
        #######################################################################

        if "total_supply" in report:

            total_supply = report.get(
                "total_supply"
            )

            print(
                Formatter.field(
                    "Total Supply",
                    Formatter.format_number(
                        total_supply
                    )
                    if isinstance(
                        total_supply,
                        (int, float),
                    )
                    else total_supply,
                )
            )

    ###########################################################################
    # Supported Assets
    ###########################################################################

    def show_supported_assets(self) -> None:
        """
        Display all assets and token standards currently supported by UBP.
        """

        logger.info(
            "Displaying supported UBP assets."
        )

        try:

            supported = (
                self.token_service.get_supported_assets()
            )

            print(
                Formatter.title(
                    "SUPPORTED UBP ASSETS"
                )
            )

            print(
                "\nNative Assets:"
            )

            native_assets = supported.get(
                "native_assets",
                {},
            )

            for blockchain, asset in native_assets.items():

                print(
                    Formatter.field(
                        blockchain.capitalize(),
                        asset,
                    )
                )

            print(
                "\nToken Standards:"
            )

            token_standards = supported.get(
                "token_standards",
                {},
            )

            for standard, blockchain in token_standards.items():

                print(
                    Formatter.field(
                        standard,
                        blockchain.capitalize(),
                    )
                )

        except Exception as error:

            logger.exception(
                "Unable to display supported assets."
            )

            print(
                Formatter.error(
                    f"Unable to display supported assets:\n{error}"
                )
            )

        finally:

            input(
                "\nPress Enter to continue..."
            )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TokenController",
]


###############################################################################
# End of File
###############################################################################