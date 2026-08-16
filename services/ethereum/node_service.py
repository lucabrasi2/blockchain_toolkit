"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.node_service

Purpose
-------
Business logic for Ethereum node validation and monitoring.

Responsibilities
----------------
• Validate the current node
• Validate custom nodes
• Compare multiple nodes
• Generate node health reports

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

from typing import Any

from core.logger import get_logger

from ethereum.node_validator import (
    compare_nodes as _compare_nodes,
    validate_node as _validate_node,
)

logger = get_logger(__name__)


class NodeService:
    """
    Ethereum node validation and monitoring service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Node Service.
        """

        logger.info(
            "NodeService initialized."
        )

    ###########################################################################
    # Current Node Validation
    ###########################################################################

    def validate_current_node(
        self,
    ) -> dict[str, Any]:
        """
        Validate the currently configured node.

        Returns
        -------
        dict[str, Any]
            Node validation report.
        """

        logger.info(
            "Validating current node."
        )

        try:

            report = _validate_node()

            logger.info(
                "Current node validated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to validate current node."
            )

            raise

    ###########################################################################
    # Custom Node Validation
    ###########################################################################

    def validate_node(
        self,
        rpc_url: str,
    ) -> dict[str, Any]:
        """
        Validate a specific RPC node.

        Parameters
        ----------
        rpc_url : str
            RPC endpoint to validate.

        Returns
        -------
        dict[str, Any]
            Node validation report.
        """

        logger.info(
            "Validating node: %s",
            rpc_url,
        )

        try:

            report = _validate_node(
                rpc_url,
            )

            logger.info(
                "Node validated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to validate node: %s",
                rpc_url,
            )

            raise

    ###########################################################################
    # Node Comparison
    ###########################################################################

    def compare_nodes(
        self,
        node_urls: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple Ethereum nodes.

        Parameters
        ----------
        node_urls : list[str]
            List of RPC endpoints.

        Returns
        -------
        dict[str, Any]
            Node comparison report.
        """

        logger.info(
            "Comparing %s nodes.",
            len(node_urls),
        )

        try:

            report = _compare_nodes(
                node_urls,
            )

            logger.info(
                "Node comparison completed successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to compare nodes."
            )

            raise

    ###########################################################################
    # Node Health Report
    ###########################################################################

    def get_node_health_report(
        self,
        rpc_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a node health report.

        Parameters
        ----------
        rpc_url : str | None
            Optional RPC endpoint.

        Returns
        -------
        dict[str, Any]
            Node health report.
        """

        logger.info(
            "Generating node health report."
        )

        try:

            if rpc_url is None:

                report = _validate_node()

            else:

                report = _validate_node(
                    rpc_url,
                )

            logger.info(
                "Node health report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate node health report."
            )

            raise


###############################################################################
# End of File
###############################################################################