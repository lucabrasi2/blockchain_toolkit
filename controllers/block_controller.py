"""
Universal Blockchain Platform (UBP)

Version : 0.9.0
Module  : Block Controller
Author  : Jaramogi Diddy

Handles Ethereum block exploration.
"""

from core.logger import get_logger

from services.ethereum.block_service import BlockService

from exceptions.blockchain_exceptions import (
    UBPException,
)

logger = get_logger(__name__)


class BlockController:
    """
    Controller responsible for Ethereum block operations.
    """

    def __init__(self):
        """
        Initialize the Block Controller.
        """

        self.block_service = BlockService()

        logger.info("BlockController initialized.")

    def block_explorer(self):
        """
        Display Ethereum block information.
        """

        logger.info("Block Explorer started.")

        block_input = input(
            "\nEnter Ethereum block number\n"
            "(leave blank for latest block):\n> "
        ).strip()

        try:

            if block_input == "":

                report = (
                    self.block_service
                    .get_latest_block_report()
                )

            else:

                block_number = int(block_input)

                report = (
                    self.block_service
                    .get_block_report(block_number)
                )

            print("\n========== BLOCK REPORT ==========\n")

            print(f"Block Number     : {report['number']}")
            print(f"Hash             : {report['hash']}")
            print(f"Parent Hash      : {report['parent_hash']}")
            print(f"Timestamp        : {report['timestamp']}")
            print(
                f"Transactions     : "
                f"{report['transaction_count']}"
            )
            print(f"Gas Used         : {report['gas_used']}")
            print(f"Gas Limit        : {report['gas_limit']}")

            if report["base_fee"] is not None:

                print(
                    f"Base Fee         : "
                    f"{report['base_fee']} Wei"
                )

            print(f"Block Size       : {report['size']} bytes")

            logger.info(
                f"Displayed block #{report['number']}."
            )

        except ValueError:

            logger.warning(
                "Invalid block number entered."
            )

            print(
                "\n❌ Block number must be an integer."
            )

        except UBPException as error:

            logger.error(str(error))

            print(f"\n❌ {error}")

        except Exception as error:

            logger.exception(
                "Unexpected block explorer error."
            )

            print(f"\nUnexpected Error: {error}")

        input("\nPress Enter to continue...")