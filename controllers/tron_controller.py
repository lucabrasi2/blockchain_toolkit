"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
controllers.tron_controller

Purpose
-------
Coordinates TRON blockchain operations.

Responsibilities
----------------
- Coordinate TRON wallet operations
- Coordinate TRON contract operations
- Coordinate TRON token operations
- Coordinate TRON block operations
- Coordinate TRON transaction operations
- Coordinate TRON node operations
- Coordinate TRON energy operations

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
from services.tron.block_service import TronBlockService
from services.tron.contract_service import TronContractService
from services.tron.token_service import TronTokenService
from services.tron.transaction_service import TronTransactionService
from services.tron.wallet_service import TronWalletService


logger = get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# TRON Controller
# =============================================================================


class TronController:
    """
    Controller responsible for TRON blockchain operations.

    The controller coordinates application requests and delegates blockchain
    and business logic to the appropriate TRON services and subsystems.
    """

    # =========================================================================
    # Construction
    # =========================================================================

    def __init__(self) -> None:
        """Initialize the TRON Controller."""

        self.wallet_service = TronWalletService()
        self.contract_service = TronContractService()
        self.token_service = TronTokenService()
        self.block_service = TronBlockService()
        self.transaction_service = TronTransactionService()

        logger.info(
            "TronController initialized."
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
        Execute a delegated operation with consistent controller logging.

        Parameters
        ----------
        operation:
            Callable containing the delegated service operation.

        operation_name:
            Human-readable name of the operation.

        Returns
        -------
        T
            Result returned by the delegated operation.

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
        Inspect a TRON wallet.

        Parameters
        ----------
        address:
            TRON wallet address.

        Returns
        -------
        dict[str, Any]
            Wallet inspection report.
        """

        logger.info(
            "Inspecting TRON wallet: %s",
            address,
        )

        report = self._execute(
            lambda: self.wallet_service.get_wallet_report(
                address,
            ),
            "TRON wallet inspection",
        )

        logger.info(
            "TRON wallet inspection "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Contract Operations
    # =========================================================================

    def contract_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect a TRON contract.

        Parameters
        ----------
        address:
            TRON contract address.

        Returns
        -------
        dict[str, Any]
            Contract inspection report.
        """

        logger.info(
            "Inspecting TRON contract: %s",
            address,
        )

        report = self._execute(
            lambda: self.contract_service.get_contract_report(
                address,
            ),
            "TRON contract inspection",
        )

        logger.info(
            "TRON contract inspection "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Token Operations
    # =========================================================================

    def token_inspector(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Inspect a TRON token.

        Parameters
        ----------
        address:
            TRON token address.

        Returns
        -------
        dict[str, Any]
            Token inspection report.
        """

        logger.info(
            "Inspecting TRON token: %s",
            address,
        )

        report = self._execute(
            lambda: self.token_service.get_token_report(
                address,
            ),
            "TRON token inspection",
        )

        logger.info(
            "TRON token inspection "
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
        Explore a TRON block.

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
            "Exploring TRON block: %s",
            block_identifier,
        )

        report = self._execute(
            lambda: self.block_service.get_block_report(
                block_identifier,
            ),
            "TRON block exploration",
        )

        logger.info(
            "TRON block exploration "
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
        Analyze a TRON transaction.

        Parameters
        ----------
        tx_hash:
            TRON transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction analysis report.
        """

        logger.info(
            "Analyzing TRON transaction: %s",
            tx_hash,
        )

        report = self._execute(
            lambda: (
                self.transaction_service
                .get_transaction_report(tx_hash)
            ),
            "TRON transaction analysis",
        )

        logger.info(
            "TRON transaction analysis "
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
        Validate a TRON node.

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
            "Validating TRON node: %s",
            rpc_url or "default",
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from tron.node_validator import validate_node

            return validate_node(
                rpc_url,
            )

        report = self._execute(
            operation,
            "TRON node validation",
        )

        logger.info(
            "TRON node validation "
            "completed successfully."
        )

        return report

    def compare_nodes(
        self,
        node_urls: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple TRON nodes.

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
            "Comparing %d TRON nodes",
            len(node_urls),
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from tron.node_validator import compare_nodes

            return compare_nodes(
                node_urls,
            )

        report = self._execute(
            operation,
            "TRON node comparison",
        )

        logger.info(
            "TRON node comparison "
            "completed successfully."
        )

        return report

    # =========================================================================
    # Energy Operations
    # =========================================================================

    def energy_optimizer(
        self,
    ) -> dict[str, Any]:
        """
        Get TRON energy price information.

        Returns
        -------
        dict[str, Any]
            Energy price information.
        """

        logger.info(
            "Getting TRON energy price."
        )

        def operation() -> dict[str, Any]:
            # Local import intentionally preserved to avoid circular imports.
            from tron.gas import get_energy_optimizer

            optimizer = get_energy_optimizer()

            return optimizer.get_energy_price()

        report = self._execute(
            operation,
            "TRON energy optimization",
        )

        logger.info(
            "TRON energy price "
            "retrieved successfully."
        )

        return report


# =============================================================================
# Public Exports
# =============================================================================

__all__ = [
    "TronController",
]


# =============================================================================
# End of File
# =============================================================================