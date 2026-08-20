"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
controllers.ethereum_controller

Purpose
-------
Ethereum controller for coordinating Ethereum blockchain operations.

Architecture Layer
------------------
Controller

Responsibilities
----------------
- Coordinate Ethereum user requests
- Delegate business logic to services
- Log controller operations
- Return inspection reports

Not Responsible For
-------------------
- Blockchain communication
- Business logic
- Report formatting
- Data persistence

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

from typing import Any, Callable, TypeVar

from core.logger import get_logger

from services.ethereum.block_service import BlockService
from services.ethereum.contract_service import ContractService
from services.ethereum.gas_service import GasService
from services.ethereum.network_service import NetworkService
from services.ethereum.node_service import NodeService
from services.ethereum.token_service import TokenService
from services.ethereum.transaction_service import TransactionService
from services.ethereum.wallet_service import WalletService


logger = get_logger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

T = TypeVar("T")


# =============================================================================
# Ethereum Controller
# =============================================================================


class EthereumController:
    """
    Controller responsible for Ethereum-related operations.

    The controller coordinates incoming requests and delegates all
    blockchain-specific business logic to the appropriate service.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """
        Initialize Ethereum services.
        """
        self.wallet_service = WalletService()
        self.contract_service = ContractService()
        self.token_service = TokenService()
        self.block_service = BlockService()
        self.transaction_service = TransactionService()
        self.node_service = NodeService()
        self.gas_service = GasService()
        self.network_service = NetworkService()

        logger.info(
            "EthereumController initialized."
        )

    # =========================================================================
    # Internal Service Execution
    # =========================================================================

    @staticmethod
    def _execute(
        operation: Callable[[], T],
        operation_name: str,
        *,
        success_message: str | None = None,
    ) -> T:
        """
        Execute a controller operation with consistent logging.

        Parameters
        ----------
        operation:
            Callable containing the service operation.

        operation_name:
            Human-readable operation name used for error logging.

        success_message:
            Optional success message.

        Returns
        -------
        T
            Result returned by the delegated service operation.

        Raises
        ------
        Exception
            Re-raises the original service exception after logging it.
        """
        try:
            result = operation()

            if success_message:
                logger.info(
                    "%s",
                    success_message,
                )

            return result

        except Exception:
            logger.exception(
                "%s failed.",
                operation_name,
            )
            raise

    # =========================================================================
    # Wallet Operations
    # =========================================================================

    def wallet_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an Ethereum wallet.

        Parameters
        ----------
        address:
            Ethereum wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet inspection report.
        """
        logger.info(
            "Inspecting Ethereum wallet: %s",
            address,
        )

        return self._execute(
            lambda: self.wallet_service.get_wallet_report(
                address,
            ),
            "Ethereum wallet inspection",
            success_message=(
                "Ethereum wallet inspection "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Contract Operations
    # =========================================================================

    def contract_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an Ethereum smart contract.

        Parameters
        ----------
        address:
            Ethereum contract address.

        Returns
        -------
        dict[str, Any]
            Contract inspection report.
        """
        logger.info(
            "Inspecting Ethereum contract: %s",
            address,
        )

        return self._execute(
            lambda: self.contract_service.get_contract_report(
                address,
            ),
            "Ethereum contract inspection",
            success_message=(
                "Ethereum contract inspection "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Token Operations
    # =========================================================================

    def token_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect an ERC-20 token.

        Parameters
        ----------
        address:
            ERC-20 token contract address.

        Returns
        -------
        dict[str, Any]
            Token inspection report.
        """
        logger.info(
            "Inspecting Ethereum token: %s",
            address,
        )

        return self._execute(
            lambda: self.token_service.get_token_report(
                address,
            ),
            "Ethereum token inspection",
            success_message=(
                "Ethereum token inspection "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Block Operations
    # =========================================================================

    def block_explorer(
        self,
        block_identifier: str | int,
    ) -> dict[str, Any]:
        """
        Explore an Ethereum block.

        Parameters
        ----------
        block_identifier:
            Block number, block hash, or ``latest``.

        Returns
        -------
        dict[str, Any]
            Block inspection report.
        """
        logger.info(
            "Exploring Ethereum block: %s",
            block_identifier,
        )

        return self._execute(
            lambda: self.block_service.get_block_report(
                block_identifier,
            ),
            "Ethereum block exploration",
            success_message=(
                "Ethereum block exploration "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Transaction Operations
    # =========================================================================

    def transaction_analyzer(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze an Ethereum transaction.

        Parameters
        ----------
        tx_hash:
            Ethereum transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction analysis report.
        """
        logger.info(
            "Analyzing Ethereum transaction: %s",
            tx_hash,
        )

        return self._execute(
            lambda: self.transaction_service.get_transaction_report(
                tx_hash,
            ),
            "Ethereum transaction analysis",
            success_message=(
                "Ethereum transaction analysis "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Node Operations
    # =========================================================================

    def node_validator(
        self,
        rpc_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate an Ethereum node.

        Parameters
        ----------
        rpc_url:
            Optional RPC endpoint.

            If omitted, the currently configured node
            is validated.

        Returns
        -------
        dict[str, Any]
            Node validation report.
        """
        logger.info(
            "Validating Ethereum node: %s",
            rpc_url or "default",
        )

        def operation() -> dict[str, Any]:
            if rpc_url is None:
                return self.node_service.validate_current_node()

            return self.node_service.validate_node(
                rpc_url,
            )

        return self._execute(
            operation,
            "Ethereum node validation",
            success_message=(
                "Ethereum node validation "
                "completed successfully."
            ),
        )

    def compare_nodes(
        self,
        node_urls: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple Ethereum nodes.

        Parameters
        ----------
        node_urls:
            RPC endpoints to compare.

        Returns
        -------
        dict[str, Any]
            Node comparison report.
        """
        logger.info(
            "Comparing %d Ethereum nodes.",
            len(node_urls),
        )

        return self._execute(
            lambda: self.node_service.compare_nodes(
                node_urls,
            ),
            "Ethereum node comparison",
            success_message=(
                "Ethereum node comparison "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Gas Operations
    # =========================================================================

    def gas_optimizer(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the current Ethereum gas optimization report.

        Returns
        -------
        dict[str, Any]
            Gas optimization report.
        """
        logger.info(
            "Retrieving Ethereum gas "
            "optimization report."
        )

        return self._execute(
            self.gas_service.get_gas_report,
            "Ethereum gas optimization",
            success_message=(
                "Ethereum gas optimization "
                "completed successfully."
            ),
        )

    # =========================================================================
    # Network Operations
    # =========================================================================

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
        logger.info(
            "Inspecting Ethereum network."
        )

        return self._execute(
            self.network_service.get_network_report,
            "Ethereum network inspection",
            success_message=(
                "Ethereum network inspection "
                "completed successfully."
            ),
        )


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "EthereumController",
]


# =============================================================================
# End of File
# =============================================================================