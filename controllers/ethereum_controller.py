"""
Universal Blockchain Platform (UBP)

## Module

controllers.ethereum_controller

## Purpose

Ethereum controller for coordinating Ethereum
blockchain operations.

## Architecture Layer

Controller

## Responsibilities

• Coordinate Ethereum user requests
• Delegate business logic to services
• Log controller operations
• Return inspection reports

## Not Responsible For

• Blockchain communication
• Business logic
• Report formatting
• Data persistence

## Author

Jaramogi Diddy

## Project

Universal Blockchain Platform (UBP)

## Version

2.0 Enterprise
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from services.ethereum.block_service import (
    BlockService,
)

from services.ethereum.contract_service import (
    ContractService,
)

from services.ethereum.gas_service import (
    GasService,
)

from services.ethereum.network_service import (
    NetworkService,
)

from services.ethereum.node_service import (
    NodeService,
)

from services.ethereum.token_service import (
    TokenService,
)

from services.ethereum.transaction_service import (
    TransactionService,
)

from services.ethereum.wallet_service import (
    WalletService,
)


logger = get_logger(__name__)


class EthereumController:
    """
    Controller responsible for Ethereum-related operations.

    The controller coordinates user requests and
    delegates all business logic to the appropriate
    service layer.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize Ethereum services.
        """

        self.wallet_service = WalletService()

        self.contract_service = ContractService()

        self.token_service = TokenService()

        self.block_service = BlockService()

        self.transaction_service = (
            TransactionService()
        )

        self.node_service = NodeService()

        self.gas_service = GasService()

        self.network_service = NetworkService()

        logger.info(
            "EthereumController initialized."
        )

    ###########################################################################
    # Wallet Operations
    ###########################################################################

    def wallet_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an Ethereum wallet.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet inspection report.
        """

        try:

            logger.info(
                "Inspecting Ethereum wallet: %s",
                address,
            )

            report = (
                self.wallet_service
                .get_wallet_report(
                    address,
                )
            )

            logger.info(
                "Ethereum wallet inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum wallet inspection failed."
            )

            raise

    ###########################################################################
    # Contract Operations
    ###########################################################################

    def contract_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an Ethereum smart contract.

        Parameters
        ----------
        address : str
            Ethereum contract address.

        Returns
        -------
        dict[str, Any]
            Contract inspection report.
        """

        try:

            logger.info(
                "Inspecting Ethereum contract: %s",
                address,
            )

            report = (
                self.contract_service
                .get_contract_report(
                    address,
                )
            )

            logger.info(
                "Ethereum contract inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum contract inspection failed."
            )

            raise

    ###########################################################################
    # Token Operations
    ###########################################################################

    def token_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an ERC-20 token.

        Parameters
        ----------
        address : str
            ERC-20 token contract address.

        Returns
        -------
        dict[str, Any]
            Token inspection report.
        """

        try:

            logger.info(
                "Inspecting Ethereum token: %s",
                address,
            )

            report = (
                self.token_service
                .get_token_report(
                    address,
                )
            )

            logger.info(
                "Ethereum token inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum token inspection failed."
            )

            raise
        ###########################################################################
    # Block Operations
    ###########################################################################

    def block_explorer(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Explore an Ethereum block.

        Parameters
        ----------
        block_identifier : str | int
            Block number, block hash,
            or "latest".

        Returns
        -------
        dict[str, Any]
            Block inspection report.
        """

        try:

            logger.info(
                "Exploring Ethereum block: %s",
                block_identifier,
            )

            report = (
                self.block_service
                .get_block_report(
                    block_identifier,
                )
            )

            logger.info(
                "Ethereum block exploration "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum block exploration failed."
            )

            raise

    ###########################################################################
    # Transaction Operations
    ###########################################################################

    def transaction_analyzer(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze an Ethereum transaction.

        Parameters
        ----------
        tx_hash : str
            Ethereum transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction analysis report.
        """

        try:

            logger.info(
                "Analyzing Ethereum transaction: %s",
                tx_hash,
            )

            report = (
                self.transaction_service
                .get_transaction_report(
                    tx_hash,
                )
            )

            logger.info(
                "Ethereum transaction analysis "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum transaction analysis failed."
            )

            raise

    ###########################################################################
    # Node Operations
    ###########################################################################

    def node_validator(
        self,
        rpc_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate an Ethereum node.

        Parameters
        ----------
        rpc_url : str | None
            Optional RPC endpoint.

            If omitted, the currently configured
            node is validated.

        Returns
        -------
        dict[str, Any]
            Node validation report.
        """

        try:

            logger.info(
                "Validating Ethereum node: %s",
                rpc_url or "default",
            )

            if rpc_url is None:

                report = (
                    self.node_service
                    .validate_current_node()
                )

            else:

                report = (
                    self.node_service
                    .validate_node(
                        rpc_url,
                    )
                )

            logger.info(
                "Ethereum node validation "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum node validation failed."
            )

            raise

    def compare_nodes(
        self,
        node_urls: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple Ethereum nodes.

        Parameters
        ----------
        node_urls : list[str]
            RPC endpoints to compare.

        Returns
        -------
        dict[str, Any]
            Node comparison report.
        """

        try:

            logger.info(
                "Comparing %d Ethereum nodes.",
                len(node_urls),
            )

            report = (
                self.node_service
                .compare_nodes(
                    node_urls,
                )
            )

            logger.info(
                "Ethereum node comparison "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum node comparison failed."
            )

            raise

    ###########################################################################
    # Gas Operations
    ###########################################################################

    def gas_optimizer(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the current Ethereum gas
        optimization report.

        Returns
        -------
        dict[str, Any]
            Gas optimization report.
        """

        try:

            logger.info(
                "Retrieving Ethereum gas "
                "optimization report."
            )

            report = (
                self.gas_service
                .get_gas_report()
            )

            logger.info(
                "Ethereum gas optimization "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum gas optimization failed."
            )

            raise

    ###########################################################################
    # Network Operations
    ###########################################################################

    def network_inspector(
        self,
    ) -> dict[str, Any]:
        """
        Inspect Ethereum network information.

        Returns
        -------
        dict[str, Any]
            Ethereum network report.
        """

        try:

            logger.info(
                "Inspecting Ethereum network."
            )

            report = (
                self.network_service
                .get_network_report()
            )

            logger.info(
                "Ethereum network inspection "
                "completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Ethereum network inspection failed."
            )

            raise