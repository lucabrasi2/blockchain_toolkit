"""
Universal Blockchain Platform (UBP)

Version : 1.3.0
Module  : Ethereum Controller
Author  : Jaramogi Diddy

Controller for Ethereum-related operations.
"""

from core.logger import get_logger
from services.ethereum.wallet_service import WalletService
from services.ethereum.contract_service import ContractService
from services.ethereum.token_service import TokenService
from services.ethereum.block_service import BlockService
from services.ethereum.transaction_service import TransactionService


logger = get_logger(__name__)


class EthereumController:
    """
    Ethereum Controller for handling
    blockchain interactions.
    """

    def __init__(self):
        """Initialize the Ethereum Controller."""
        self.wallet_service = WalletService()
        self.contract_service = ContractService()
        self.token_service = TokenService()
        self.block_service = BlockService()
        self.transaction_service = TransactionService()
        logger.info("EthereumController initialized.")

    def wallet_inspector(self, address: str) -> dict:
        """
        Inspect a wallet address.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict
            Wallet inspection report.
        """

        try:
            logger.info(f"Inspecting wallet: {address}")

            # Get the wallet report
            report = self.wallet_service.get_wallet_report(address)

            logger.info("Wallet inspection completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected wallet inspector error: {error}")
            raise

    def contract_inspector(self, address: str) -> dict:
        """
        Inspect a contract address.

        Parameters
        ----------
        address : str
            Ethereum contract address.

        Returns
        -------
        dict
            Contract inspection report.
        """

        try:
            logger.info(f"Inspecting contract: {address}")

            # Get the contract report
            report = self.contract_service.get_contract_report(address)

            logger.info("Contract inspection completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected contract inspector error: {error}")
            raise

    def token_inspector(self, address: str) -> dict:
        """
        Inspect a token address.

        Parameters
        ----------
        address : str
            Ethereum token address.

        Returns
        -------
        dict
            Token inspection report.
        """

        try:
            logger.info(f"Inspecting token: {address}")

            # Get the token report
            report = self.token_service.get_token_report(address)

            logger.info("Token inspection completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected token inspector error: {error}")
            raise

    def block_explorer(self, block_identifier) -> dict:
        """
        Explore a block.

        Parameters
        ----------
        block_identifier : int or str
            Block number or 'latest'.

        Returns
        -------
        dict
            Block exploration report.
        """

        try:
            logger.info(f"Exploring block: {block_identifier}")

            # Get the block report
            report = self.block_service.get_block_report(block_identifier)

            logger.info("Block exploration completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected block explorer error: {error}")
            raise

    def transaction_analyzer(self, tx_hash: str) -> dict:
        """
        Analyze a transaction.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        dict
            Transaction analysis report.
        """

        try:
            logger.info(f"Analyzing transaction: {tx_hash}")

            # Get the transaction report
            report = self.transaction_service.get_transaction_report(tx_hash)

            logger.info("Transaction analysis completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected transaction analyzer error: {error}")
            raise