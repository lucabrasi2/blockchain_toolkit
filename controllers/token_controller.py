"""
Universal Blockchain Platform (UBP)

Version : 1.1.0
Module  : Token Controller
Author  : Jaramogi Diddy

Controller responsible for ERC-20 Token inspection.
"""

from core.logger import get_logger
from core.formatter import Formatter

from services.ethereum.token_service import (
    TokenService,
)

from exceptions.blockchain_exceptions import (
    UBPException,
)

logger = get_logger(__name__)


class TokenController:
    """
    Controller responsible for ERC-20 Token inspection.
    """

    def __init__(self):
        """
        Initialize the Token Controller.
        """

        self.token_service = TokenService()

        logger.info(
            "TokenController initialized."
        )

    def token_inspector(self):
        """
        Display an ERC-20 token report.
        """

        logger.info(
            "Token Inspector started."
        )

        contract_address = input(
            "\nEnter ERC-20 contract address:\n> "
        ).strip()

        try:

            report = (
                self.token_service
                .get_token_report(
                    contract_address
                )
            )

            print(
                Formatter.title(
                    "ERC-20 TOKEN REPORT"
                )
            )

            print(
                Formatter.field(
                    "Contract Address",
                    report["contract_address"],
                )
            )

            print(
                Formatter.field(
                    "Token Name",
                    report["name"],
                )
            )

            print(
                Formatter.field(
                    "Symbol",
                    report["symbol"],
                )
            )

            print(
                Formatter.field(
                    "Decimals",
                    report["decimals"],
                )
            )

            print(
                Formatter.field(
                    "Total Supply",
                    (
                        f"{Formatter.format_number(report['formatted_supply'])} "
                        f"{report['symbol']}"
                    ),
                )
            )

            print(
                Formatter.field(
                    "Raw Supply",
                    Formatter.format_number(
                        report["raw_supply"]
                    ),
                )
            )

            logger.info(
                "Token report displayed successfully."
            )

        except UBPException as error:

            logger.error(str(error))

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

        input("\nPress Enter to continue...")