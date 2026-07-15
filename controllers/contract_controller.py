"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Smart Contract Controller

Architectural Intent
--------------------
The controller layer manages user interaction only.

Responsibilities:
- Receive user input
- Call ContractService
- Display formatted results
- Handle presentation errors

The controller contains NO blockchain logic.
"""


from core.logger import get_logger

from constants.contract_types import ERC20

from services.ethereum.contract_service import (
    ContractService,
)

from exceptions.blockchain_exceptions import (
    UBPException,
)

from core.formatter import Formatter


logger = get_logger(__name__)


class ContractController:
    """
    Smart Contract Inspector Controller.
    """


    def __init__(self):
        """
        Initialize controller.
        """

        logger.info(
            "Initializing ContractController."
        )

        self.contract_service = ContractService()


    def contract_inspector(self):
        """
        Launch the Smart Contract Inspector.
        """

        logger.info(
            "Smart Contract Inspector started."
        )


        address = input(
            "\nEnter Ethereum address:\n> "
        ).strip()


        try:

            report = (
                self.contract_service
                .get_contract_report(
                    address
                )
            )


            print(
                Formatter.title(
                    "SMART CONTRACT REPORT"
                )
            )


            print(
                Formatter.section(
                    "General"
                )
            )


            print(
                Formatter.field(
                    "Address",
                    report.get(
                        "address",
                        "N/A"
                    ),
                )
            )


            print(
                Formatter.field(
                    "Contract",
                    Formatter.yes_no(
                        report.get(
                            "is_contract",
                            False
                        )
                    ),
                )
            )


            print(
                Formatter.field(
                    "Classification",
                    report.get(
                        "classification",
                        "UNKNOWN"
                    ),
                )
            )


            if report.get(
                "contract_type"
            ) == ERC20:


                print(
                    Formatter.section(
                        "Asset Information"
                    )
                )


                print(
                    Formatter.field(
                        "Name",
                        report.get(
                            "name",
                            "N/A"
                        ),
                    )
                )


                print(
                    Formatter.field(
                        "Symbol",
                        report.get(
                            "symbol",
                            "N/A"
                        ),
                    )
                )


                print(
                    Formatter.field(
                        "Decimals",
                        report.get(
                            "decimals",
                            "N/A"
                        ),
                    )
                )


                print(
                    Formatter.field(
                        "Total Supply",
                        report.get(
                            "supply_formatted",
                            "N/A"
                        ),
                    )
                )


            print(
                Formatter.section(
                    "Blockchain"
                )
            )


            print(
                Formatter.field(
                    "ETH Balance",
                    Formatter.format_eth(
                        report.get(
                            "balance_eth",
                            0
                        )
                    ),
                )
            )


            print(
                Formatter.field(
                    "Nonce",
                    Formatter.format_number(
                        report.get(
                            "nonce",
                            0
                        )
                    ),
                )
            )


            print(
                Formatter.field(
                    "Bytecode Size",
                    Formatter.format_bytes(
                        report.get(
                            "bytecode_size",
                            0
                        )
                    ),
                )
            )


            logger.info(
                "Smart Contract report displayed successfully."
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
                "Unexpected Smart Contract Inspector error."
            )


            print(
                Formatter.error(
                    f"Unexpected Error:\n{error}"
                )
            )


        input(
            "\nPress Enter to continue..."
        )