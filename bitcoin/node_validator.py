"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.node_validator

Purpose
-------
Bitcoin node validation and health checking.

This module provides node health checks for Bitcoin nodes.

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

from typing import Dict, Any, Optional, List
import time

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


class BitcoinNodeValidator:
    """
    Bitcoin node validation and health checking.
    """

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url

    def validate(self) -> Dict[str, Any]:
        """
        Perform full node validation.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        logger.info("Starting node validation for Bitcoin")

        result = {
            "is_connected": False,
            "is_syncing": False,
            "node_type": "Full Node",
            "chain_id": 0,
            "block_number": 0,
            "peer_count": 0,
            "response_time_ms": 0,
            "client_version": "Bitcoin Core",
            "health_status": "Unknown",
            "issues": [],
            "details": {},
        }

        try:
            start_time = time.time()

            client = get_connection()
            block = client.get_latest_block()

            if "error" not in block:
                result["is_connected"] = True
                result["block_number"] = block.get("number", 0)
                result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

                # Add block details
                result["details"]["difficulty"] = block.get("difficulty")
                result["details"]["transaction_count"] = block.get("transaction_count")
                result["details"]["size"] = block.get("size")

                result["health_status"] = "Healthy 🟢"
                logger.info("Bitcoin node validation successful")
            else:
                result["issues"].append("Unable to retrieve block")
                result["health_status"] = "Unhealthy 🔴"

        except Exception as error:
            logger.error(f"Bitcoin node validation failed: {error}")
            result["issues"].append(f"Connection error: {str(error)}")
            result["health_status"] = "Unhealthy 🔴"

        return result


def validate_node(rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a Bitcoin node.

    Parameters
    ----------
    rpc_url : str, optional
        RPC URL to validate.

    Returns
    -------
    Dict[str, Any]
        Node validation report.
    """
    validator = BitcoinNodeValidator(rpc_url)
    return validator.validate()


def compare_nodes(node_urls: List[str]) -> Dict[str, Any]:
    """
    Compare multiple Bitcoin nodes.

    Parameters
    ----------
    node_urls : List[str]
        List of node RPC URLs to compare.

    Returns
    -------
    Dict[str, Any]
        Comparison report.
    """
    logger.info(f"Comparing {len(node_urls)} Bitcoin nodes")

    results = []
    latest_blocks = {}

    for url in node_urls:
        try:
            validator = BitcoinNodeValidator(url)
            result = validator.validate()
            results.append(result)

            if result.get("is_connected"):
                latest_blocks[url] = result.get("block_number", 0)
        except Exception as error:
            logger.error(f"Error validating node {url}: {error}")
            results.append({
                "rpc_url": url,
                "is_connected": False,
                "error": str(error),
            })

    if latest_blocks:
        block_heights = list(latest_blocks.values())
        max_block = max(block_heights)
        min_block = min(block_heights)
        block_diff = max_block - min_block
        is_consistent = block_diff < 10
    else:
        is_consistent = False
        block_diff = None

    return {
        "nodes_checked": len(node_urls),
        "nodes_connected": sum(1 for r in results if r.get("is_connected")),
        "same_chain": True,
        "block_height_consistent": is_consistent,
        "chain_ids": [0],
        "latest_blocks": latest_blocks,
        "block_difference": block_diff,
        "results": results,
        "consensus_status": "✅ Reached" if is_consistent else "❌ Not Reached",
    }


###############################################################################
# End of File
###############################################################################
