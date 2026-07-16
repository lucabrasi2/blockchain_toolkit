"""
Universal Blockchain Platform (UBP)

Module:
    Node Service

Purpose:
    Business logic for node validation and monitoring.

Responsibilities:
    • Validate single node
    • Compare multiple nodes
    • Monitor node health
    • Generate node reports

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, List, Optional

from core.logger import get_logger
from ethereum.node_validator import validate_node, compare_nodes
from ethereum.connection import get_connection


logger = get_logger(__name__)


class NodeService:
    """
    Node validation and monitoring service.
    """

    def __init__(self):
        """Initialize the Node Service."""
        logger.info("NodeService initialized.")

    def validate_current_node(self) -> Dict[str, Any]:
        """
        Validate the current node from connection.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        logger.info("Validating current node")
        return validate_node()

    def validate_node(self, rpc_url: str) -> Dict[str, Any]:
        """
        Validate a specific node.

        Parameters
        ----------
        rpc_url : str
            RPC URL to validate.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        logger.info(f"Validating node: {rpc_url}")
        return validate_node(rpc_url)

    def compare_nodes(self, node_urls: List[str]) -> Dict[str, Any]:
        """
        Compare multiple nodes.

        Parameters
        ----------
        node_urls : List[str]
            List of node RPC URLs.

        Returns
        -------
        Dict[str, Any]
            Comparison report.
        """
        logger.info(f"Comparing {len(node_urls)} nodes")
        return compare_nodes(node_urls)

    def get_node_health_report(self, rpc_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a node health report.

        Parameters
        ----------
        rpc_url : str, optional
            RPC URL to check.

        Returns
        -------
        Dict[str, Any]
            Health report.
        """
        if rpc_url:
            return validate_node(rpc_url)
        else:
            return validate_node()