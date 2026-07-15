"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Transaction Controller
Author  : Jaramogi Diddy

Handles Ethereum transaction exploration.
"""

from core.logger import get_logger

from services.ethereum.transaction_service import (
    TransactionService,
)

from exceptions.blockchain_exceptions import (
    UBPException,
)

logger = get_logger(__name__)


class TransactionController:
    """
    Controller responsible for Ethereum transaction operations.
    """

    def __init__(self):
        """
        Initialize the Transaction Controller.
        """

        self.transaction_service = TransactionService()

        logger.info("TransactionController initialized.")

    def transaction_explorer(self):
        """
        Display Ethereum transaction information.
        """

        logger.info("Transaction Explorer started.")

        tx_hash = input(
            "\nEnter Ethereum transaction hash:\n> "
        ).strip()

        try:

            report = (
                self.transaction_service
                .get_transaction_report(tx_hash)
            )

            print("\n========== TRANSACTION REPORT ==========\n")

            print(f"Hash              : {report['hash']}")
            print(f"Block Number      : {report['block_number']}")
            print(f"From              : {report['from']}")
            print(f"To                : {report['to']}")
            print(f"Value             : {report['value_eth']} ETH")
            print(f"Value (Wei)       : {report['value_wei']}")
            print(f"Gas Limit         : {report['gas']}")
            print(f"Gas Price         : {report['gas_price']} Wei")
            print(f"Gas Used          : {report['gas_used']}")
            print(f"Nonce             : {report['nonce']}")
            print(
                f"Status            : "
                f"{'Success' if report['status'] == 1 else 'Failed'}"
            )

            if report["contract_address"]:

                print(
                    f"Contract Address  : "
                    f"{report['contract_address']}"
                )

            print(f"Logs              : {report['logs']}")

            logger.info(
                "Transaction information displayed successfully."
            )

        except UBPException as error:

            logger.error(str(error))

            print(f"\n❌ {error}")

        except Exception as error:

            logger.exception(
                "Unexpected transaction explorer error."
            )

            print(f"\nUnexpected Error: {error}")

        input("\nPress Enter to continue...")