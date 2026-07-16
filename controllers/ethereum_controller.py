"""
Universal Blockchain Platform (UBP)

Version : 1.3.0
Module  : Ethereum Controller
Author  : Jaramogi Diddy

Controller for Ethereum-related operations.

Responsibilities:
    • Validate user input
    • Coordinate services
    • Handle exceptions
    • Call display modules

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Optional, Dict, Any

from core.logger import get_logger
from services.ethereum.wallet_service import WalletService
from services.ethereum.contract_service import ContractService
from services.ethereum.token_service import TokenService
from services.ethereum.block_service import BlockService
from services.ethereum.transaction_service import TransactionService
from services.ethereum.node_service import NodeService


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
        self.node_service = NodeService()
        logger.info("EthereumController initialized.")

    def wallet_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a wallet address.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        Dict[str, Any]
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

    def contract_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a contract address.

        Parameters
        ----------
        address : str
            Ethereum contract address.

        Returns
        -------
        Dict[str, Any]
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

    def token_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a token address.

        Parameters
        ----------
        address : str
            Ethereum token address.

        Returns
        -------
        Dict[str, Any]
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

    def block_explorer(self, block_identifier) -> Dict[str, Any]:
        """
        Explore a block.

        Parameters
        ----------
        block_identifier : int or str
            Block number or 'latest'.

        Returns
        -------
        Dict[str, Any]
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

    def transaction_analyzer(self, tx_hash: str) -> Dict[str, Any]:
        """
        Analyze a transaction.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        Dict[str, Any]
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

    def node_validator(self, rpc_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a blockchain node.

        Parameters
        ----------
        rpc_url : str, optional
            RPC URL to validate. If None, validates current node.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        try:
            logger.info(f"Validating node: {rpc_url or 'default'}")

            # Validate the node
            if rpc_url:
                report = self.node_service.validate_node(rpc_url)
            else:
                report = self.node_service.validate_current_node()

            logger.info("Node validation completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected node validator error: {error}")
            raise

    def compare_nodes(self, node_urls: list) -> Dict[str, Any]:
        """
        Compare multiple blockchain nodes.

        Parameters
        ----------
        node_urls : list
            List of node RPC URLs to compare.

        Returns
        -------
        Dict[str, Any]
            Node comparison report.
        """
        try:
            logger.info(f"Comparing {len(node_urls)} nodes")

            # Compare the nodes
            report = self.node_service.compare_nodes(node_urls)

            logger.info("Node comparison completed successfully.")
            return report

        except Exception as error:
            logger.error(f"Unexpected node comparison error: {error}")
            raise