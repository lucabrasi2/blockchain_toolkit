"""
Universal Blockchain Platform (UBP)

Module:
    TRON Controller

Purpose:
    Handle TRON-related operations and coordinate
    between the user interface and TRON services.

Responsibilities:
    • Coordinate TRON services
    • Delegate business logic
    • Handle controller-level exceptions
    • Provide a stable interface for API, CLI and Web UI

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from core.display import print_error

from services.tron.wallet_service import TronWalletService
from services.tron.contract_service import TronContractService
from services.tron.token_service import TronTokenService

from tron.blocks import get_block
from tron.transactions import get_transaction


logger = get_logger(__name__)


class TronController:
    """
    Controller responsible for coordinating
    TRON blockchain operations.

    The controller intentionally contains very
    little business logic. All blockchain-specific
    operations are delegated to the appropriate
    service classes.
    """

    def __init__(self):
        """
        Initialize TRON services.
        """
        self.wallet_service = TronWalletService()
        self.contract_service = TronContractService()
        self.token_service = TronTokenService()

        logger.info("TronController initialized successfully.")

    def wallet_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a TRON wallet.

        Parameters
        ----------
        address : str
            TRON wallet address.

        Returns
        -------
        Dict[str, Any]
            Wallet inspection report.
        """
        logger.info(f"Inspecting TRON wallet: {address}")

        try:
            return self.wallet_service.get_wallet_report(address)

        except Exception as error:
            logger.exception(
                "Unexpected error while inspecting TRON wallet."
            )

            print_error(str(error))

            return {
                "address": address,
                "error": str(error),
            }

    def contract_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a TRON contract.

        Parameters
        ----------
        address : str
            TRON contract address.

        Returns
        -------
        Dict[str, Any]
            Contract inspection report.
        """
        logger.info(f"Inspecting TRON contract: {address}")

        try:
            return self.contract_service.get_contract_report(address)

        except Exception as error:
            logger.exception(
                "Unexpected error while inspecting TRON contract."
            )

            print_error(str(error))

            return {
                "address": address,
                "error": str(error),
            }

    def token_inspector(
        self,
        address: str,
        wallet_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Inspect a TRC-20 token.

        Parameters
        ----------
        address : str
            Token contract address.
        wallet_address : str, optional
            Wallet address for balance lookup.

        Returns
        -------
        Dict[str, Any]
            Token inspection report.
        """
        logger.info(f"Inspecting TRON token: {address}")

        try:
            return self.token_service.get_token_report(
                address=address,
                wallet_address=wallet_address,
            )

        except Exception as error:
            logger.exception(
                "Unexpected error while inspecting TRON token."
            )

            print_error(str(error))

            return {
                "address": address,
                "error": str(error),
            }

    def block_explorer(self, block_number: int) -> Dict[str, Any]:
        """
        Explore a TRON block.

        Parameters
        ----------
        block_number : int
            TRON block number.

        Returns
        -------
        Dict[str, Any]
            Block information.
        """
        logger.info(f"Exploring TRON block: {block_number}")

        try:
            return get_block(block_number)

        except Exception as error:
            logger.exception(
                "Unexpected error while exploring TRON block."
            )

            print_error(str(error))

            return {
                "number": block_number,
                "error": str(error),
            }

    def transaction_analyzer(self, tx_hash: str) -> Dict[str, Any]:
        """
        Analyze a TRON transaction.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Dict[str, Any]
            Transaction analysis report.
        """
        logger.info(f"Analyzing TRON transaction: {tx_hash}")

        try:
            return get_transaction(tx_hash)

        except Exception as error:
            logger.exception(
                "Unexpected error while analyzing TRON transaction."
            )

            print_error(str(error))

            return {
                "hash": tx_hash,
                "error": str(error),
            }  