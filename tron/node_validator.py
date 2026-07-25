"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.node_validator

Purpose
-------
TRON node validation and health checking.

This module provides node health checks for TRON nodes.

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
import requests

from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


class TronNodeValidator:
    """
    TRON node validation and health checking.
    """

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or TRON_API_URL

    def validate(self) -> Dict[str, Any]:
        """
        Perform full node validation.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        logger.info(f"Starting node validation for TRON: {self.rpc_url}")

        result = {
            "is_connected": False,
            "is_syncing": False,
            "node_type": "Full Node",
            "chain_id": 0,
            "block_number": 0,
            "peer_count": 0,
            "response_time_ms": 0,
            "client_version": "TRON FullNode",
            "health_status": "Unknown",
            "issues": [],
            "details": {},
        }

        try:
            start_time = time.time()

            # Check connection
            client = get_connection()
            block = client.get_latest_block_number()

            if block > 0:
                result["is_connected"] = True
                result["block_number"] = block
                result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

                # Get chain parameters
                url = f"{self.rpc_url}/wallet/getchainparameters"
                response = requests.post(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    chain_params = data.get("chainParameter", [])
                    for param in chain_params:
                        if param.get("key") == "getEnergyFee":
                            result["details"]["energy_fee"] = param.get("value")

                result["health_status"] = "Healthy 🟢"
                logger.info("TRON node validation successful")
            else:
                result["issues"].append("Unable to retrieve block number")
                result["health_status"] = "Unhealthy 🔴"

        except Exception as error:
            logger.error(f"TRON node validation failed: {error}")
            result["issues"].append(f"Connection error: {str(error)}")
            result["health_status"] = "Unhealthy 🔴"

        return result


def validate_node(rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a TRON node.

    Parameters
    ----------
    rpc_url : str, optional
        RPC URL to validate.

    Returns
    -------
    Dict[str, Any]
        Node validation report.
    """
    validator = TronNodeValidator(rpc_url)
    return validator.validate()


def compare_nodes(node_urls: List[str]) -> Dict[str, Any]:
    """
    Compare multiple TRON nodes.

    Parameters
    ----------
    node_urls : List[str]
        List of node RPC URLs to compare.

    Returns
    -------
    Dict[str, Any]
        Comparison report.
    """
    logger.info(f"Comparing {len(node_urls)} TRON nodes")

    results = []
    latest_blocks = {}

    for url in node_urls:
        try:
            validator = TronNodeValidator(url)
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

    # Check consensus
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
