"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.node_validator

Purpose
-------
TRON node validation and health checking.

This module provides node health checks and node comparison
for TRON Full Nodes and public RPC endpoints.

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
        Perform a complete node validation.

        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """

        logger.info(
            f"Starting node validation for TRON: {self.rpc_url}"
        )

        result = {
            "rpc_url": self.rpc_url,
            "is_connected": False,
            "is_syncing": False,
            "node_type": "Full Node",
            "chain_id": 0,
            "network_id": None,
            "block_number": 0,
            "peer_count": 0,
            "response_time_ms": 0.0,
            "client_version": "TRON FullNode",
            "protocol_version": None,
            "archive_node": False,
            "gas_price": None,
            "health_status": "Unknown",
            "issues": [],
            "details": {},
        }

        try:

            start = time.perf_counter()

            ##################################################################
            # Connect using the requested RPC URL
            ##################################################################

            client = get_connection(
                rpc_url=self.rpc_url
            )

            latest_block = client.get_latest_block_number()

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            result["response_time_ms"] = round(
                elapsed,
                2,
            )

            if latest_block <= 0:

                result["issues"].append(
                    "Unable to retrieve latest block."
                )

                result["health_status"] = "Unhealthy 🔴"

                return result

            result["is_connected"] = True
            result["block_number"] = latest_block

            ##################################################################
            # Chain parameters
            ##################################################################

            try:

                response = requests.post(
                    f"{self.rpc_url}/wallet/getchainparameters",
                    timeout=10,
                )

                if response.status_code == 200:

                    data = response.json()

                    parameters = data.get(
                        "chainParameter",
                        [],
                    )

                    for parameter in parameters:

                        key = parameter.get("key")
                        value = parameter.get("value")

                        result["details"][key] = value

                        if key == "getEnergyFee":
                            result["details"][
                                "energy_fee"
                            ] = value

            except Exception as error:

                logger.warning(
                    f"Unable to retrieve chain parameters: {error}"
                )

            ##################################################################
            # Health assessment
            ##################################################################

            if result["response_time_ms"] > 5000:

                result["issues"].append(
                    "High response time."
                )

                result["health_status"] = "Warning 🟡"

            else:

                result["health_status"] = "Healthy 🟢"

            logger.info(
                "TRON node validation successful"
            )

        except Exception as error:

            logger.exception(
                f"TRON node validation failed: {error}"
            )

            result["issues"].append(str(error))

            result["health_status"] = "Unhealthy 🔴"

        return result


def validate_node(
    rpc_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate a single TRON node.

    Parameters
    ----------
    rpc_url : str, optional
        RPC endpoint.

    Returns
    -------
    Dict[str, Any]
        Validation report.
    """

    validator = TronNodeValidator(rpc_url)

    return validator.validate()


def compare_nodes(
    node_urls: List[str],
) -> Dict[str, Any]:
    """
    Compare multiple TRON nodes.

    Parameters
    ----------
    node_urls : List[str]
        RPC URLs.

    Returns
    -------
    Dict[str, Any]
        Comparison report.
    """

    logger.info(
        f"Comparing {len(node_urls)} TRON nodes"
    )

    results = []

    latest_blocks = {}

    for url in node_urls:

        try:

            validator = TronNodeValidator(url)

            report = validator.validate()

            results.append(report)

            if report.get("is_connected"):

                latest_blocks[url] = report.get(
                    "block_number",
                    0,
                )

        except Exception as error:

            logger.exception(
                f"Error validating node {url}: {error}"
            )

            results.append(
                {
                    "rpc_url": url,
                    "is_connected": False,
                    "health_status": "Unhealthy 🔴",
                    "error": str(error),
                }
            )

    ##########################################################################
    # Consensus
    ##########################################################################

    if latest_blocks:

        heights = list(
            latest_blocks.values()
        )

        highest = max(heights)

        lowest = min(heights)

        difference = highest - lowest

        consistent = difference <= 10

    else:

        difference = None

        consistent = False

    return {
        "nodes_checked": len(node_urls),
        "nodes_connected": sum(
            1
            for report in results
            if report.get("is_connected")
        ),
        "same_chain": True,
        "block_height_consistent": consistent,
        "chain_ids": [0],
        "latest_blocks": latest_blocks,
        "block_difference": difference,
        "results": results,
        "consensus_status": (
            "✅ Reached"
            if consistent
            else "❌ Not Reached"
        ),
    }


###############################################################################
# End of File
###############################################################################