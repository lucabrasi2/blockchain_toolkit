"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
controllers.bitcoin_controller

Purpose
-------
Coordinates Bitcoin blockchain operations.

Responsibilities
----------------
- Coordinate Bitcoin wallet operations
- Coordinate Bitcoin block operations
- Coordinate Bitcoin transaction operations
- Coordinate Bitcoin node operations
- Coordinate Bitcoin fee operations
- Provide Bitcoin connection status

Author
------
UBP Engineering Team

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
===============================================================================
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from core.logger import get_logger

from exceptions.blockchain_exceptions import UBPException
from services.bitcoin.block_service import BitcoinBlockService
from services.bitcoin.transaction_service import BitcoinTransactionService
from services.bitcoin.wallet_service import BitcoinWalletService


logger = get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# Bitcoin Controller
# =============================================================================


class BitcoinController:
    """
    Controller responsible for Bitcoin blockchain operations.

    The controller coordinates requests and delegates blockchain-specific
    business logic to the appropriate service or Bitcoin subsystem.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the Bitcoin Controller."""
        self.wallet_service = BitcoinWalletService()
        self.block_service = BitcoinBlockService()
        self.transaction_service = BitcoinTransactionService()

        logger.info(
            "BitcoinController initialized."
        )

    # =========================================================================
    # Internal Execution Helper
    # =========================================================================

    @staticmethod
    def _execute(
        operation: Callable[[], T],
        operation_name: str,
    ) -> T:
        """
        Execute an operation with consistent controller-level logging.

        Parameters
        ----------
        operation:
            Callable containing the delegated operation.

        operation_name:
            Human-readable operation name.

        Returns
        -------
        T
            Result returned by the operation.

        Raises
        ------
        Exception
            Re-raises the original exception after logging.
        """
        try:
            return operation()

        except UBPException:
            logger.exception(
                "%s failed.",
                operation_name,
            )
            raise

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
        Inspect a Bitcoin wallet.

        Parameters
        ----------
        address:
            Bitcoin wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet inspection report.
        """
        logger.info(
            "Inspecting Bitcoin wallet: %s",
            address,
        )

        report = self._execute(
            lambda: self.wallet_service.get_wallet_report(
                address,
            ),
            "Bitcoin wallet inspection",
        )

        logger.info(
            "Bitcoin wallet inspection "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Block Operations
    # =========================================================================

    def block_explorer(
        self,
        block_identifier: Any,
    ) -> dict[str, Any]:
        """
        Explore a Bitcoin block.

        Parameters
        ----------
        block_identifier:
            Block number or block identifier such as ``latest``.

        Returns
        -------
        dict[str, Any]
            Block exploration report.
        """
        logger.info(
            "Exploring Bitcoin block: %s",
            block_identifier,
        )

        report = self._execute(
            lambda: self.block_service.get_block_report(
                block_identifier,
            ),
            "Bitcoin block exploration",
        )

        logger.info(
            "Bitcoin block exploration "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Transaction Operations
    # =========================================================================

    def transaction_analyzer(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze a Bitcoin transaction.

        Parameters
        ----------
        tx_hash:
            Bitcoin transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction analysis report.
        """
        logger.info(
            "Analyzing Bitcoin transaction: %s",
            tx_hash,
        )

        report = self._execute(
            lambda: (
                self.transaction_service
                .get_transaction_report(tx_hash)
            ),
            "Bitcoin transaction analysis",
        )

        logger.info(
            "Bitcoin transaction analysis "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Node Operations
    # =========================================================================

    def node_validator(
        self,
        rpc_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate a Bitcoin node.

        Parameters
        ----------
        rpc_url:
            RPC URL to validate. If ``None``, the default node is validated.

        Returns
        -------
        dict[str, Any]
            Node validation report.
        """

        logger.info(
            "Validating Bitcoin node: %s",
            rpc_url or "default",
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from bitcoin.node_validator import validate_node

            return validate_node(
                rpc_url,
            )

        report = self._execute(
            operation,
            "Bitcoin node validation",
        )

        logger.info(
            "Bitcoin node validation "
            "completed successfully."
        )

        return report

    def compare_nodes(
        self,
        node_urls: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple Bitcoin nodes.

        Parameters
        ----------
        node_urls:
            List of RPC URLs to compare.

        Returns
        -------
        dict[str, Any]
            Node comparison report.
        """
        logger.info(
            "Comparing %d Bitcoin nodes",
            len(node_urls),
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from bitcoin.node_validator import compare_nodes

            return compare_nodes(
                node_urls,
            )

        report = self._execute(
            operation,
            "Bitcoin node comparison",
        )

        logger.info(
            "Bitcoin node comparison "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Fee Operations
    # =========================================================================

    def fee_optimizer(
        self,
    ) -> dict[str, Any]:
        """
        Get Bitcoin fee estimates.

        Returns
        -------
        dict[str, Any]
            Fee estimates such as slow, standard, and fast.
        """

        logger.info(
            "Getting Bitcoin fee estimates."
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from bitcoin.gas import get_fee_optimizer

            optimizer = get_fee_optimizer()

            return optimizer.get_fee_estimate()

        report = self._execute(
            operation,
            "Bitcoin fee optimization",
        )

        logger.info(
            "Bitcoin fee estimates "
            "retrieved successfully."
        )

        return report

    # =========================================================================
    # Utility Operations
    # =========================================================================

    def get_connection_status(
        self,
    ) -> dict[str, Any]:
        """
        Get Bitcoin connection status.

        Returns
        -------
        dict[str, Any]
            Connection status information.
        """
        try:
            # Local import intentionally preserved to avoid circular imports.
            from bitcoin.connection import get_connection

            get_connection()

            return {
                "connected": True,
                "blockchain": "bitcoin",
                "network": "mainnet",
            }

        except Exception as error:
            logger.warning(
                "Bitcoin connection status check failed: %s",
                error,
            )

            return {
                "connected": False,
                "error": str(error),
            }


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "BitcoinController",
]


# =============================================================================
# End of File
# =============================================================================