"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
ethereum.node_validator

Purpose
-------
Enterprise node validation for Ethereum networks.

This module provides comprehensive node health checks,
performance monitoring, and diagnostics.

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

import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from web3 import Web3

from ethereum.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


class NodeValidationResult:
    """
    Node validation result container.
    """

    def __init__(self):
        self.is_connected = False
        self.is_syncing = False
        self.is_archive = False
        self.node_type = "Unknown"
        self.chain_id = 0
        self.block_number = 0
        self.peer_count = 0
        self.gas_price = 0
        self.response_time_ms = 0
        self.client_version = "Unknown"
        self.protocol_version = "Unknown"
        self.network_id = 0
        self.consensus = "Unknown"
        self.health_status = "Unknown"
        self.issues = []
        self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_connected": self.is_connected,
            "is_syncing": self.is_syncing,
            "is_archive": self.is_archive,
            "node_type": self.node_type,
            "chain_id": self.chain_id,
            "block_number": self.block_number,
            "peer_count": self.peer_count,
            "gas_price": self.gas_price,
            "response_time_ms": self.response_time_ms,
            "client_version": self.client_version,
            "protocol_version": self.protocol_version,
            "network_id": self.network_id,
            "consensus": self.consensus,
            "health_status": self.health_status,
            "issues": self.issues,
            "details": self.details,
        }


class NodeValidator:
    """
    Node validation and confirmation service.
    """

    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialize the node validator.

        Parameters
        ----------
        rpc_url : str, optional
            RPC URL to validate. If None, uses default connection.
        """
        self.rpc_url = rpc_url
        self.w3 = None
        self.result = NodeValidationResult()
        self._connected_web3 = None

    def validate(self) -> Dict[str, Any]:
        """
        Perform full node validation.
        """
        logger.info(f"Starting node validation for: {self.rpc_url or 'default'}")

        # If w3 is already set, use it
        if self.w3 is not None:
            self._connected_web3 = self.w3
            self.result.is_connected = True
            self.result.response_time_ms = 0
            logger.info("✅ Using provided Web3 connection")
        else:
            # Step 1: Check connectivity
            self._check_connectivity()

        if not self.result.is_connected:
            logger.error("Node validation failed: Not connected")
            return self.result.to_dict()

        # Step 2: Retrieve node information
        self._get_node_info()

        # Step 3: Check synchronization status
        self._check_sync_status()

        # Step 4: Detect node type
        self._detect_node_type()

        # Step 5: Measure performance
        self._measure_performance()

        # Step 6: Check peer information
        self._check_peers()

        # Step 7: Determine overall health
        self._determine_health()

        logger.info("Node validation completed successfully.")

        return self.result.to_dict()

    def _check_connectivity(self) -> None:
        """
        Check if the node is reachable.
        """
        try:
            start_time = time.time()
            
            if self.rpc_url:
                self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            else:
                self.w3 = get_connection()
            
            self._connected_web3 = self.w3
            
            # Measure response time
            if self.w3.is_connected():
                self.result.is_connected = True
                self.result.response_time_ms = round((time.time() - start_time) * 1000, 2)
                logger.info(f"✅ Node connected. Response time: {self.result.response_time_ms}ms")
            else:
                self.result.issues.append("Node is not reachable")
                logger.warning("❌ Node is not reachable")
                
        except Exception as error:
            self.result.issues.append(f"Connection error: {str(error)}")
            logger.error(f"Connection error: {error}")

    def _get_node_info(self) -> None:
        """
        Get basic node information.
        """
        try:
            # Chain ID
            self.result.chain_id = self.w3.eth.chain_id
            
            # Block number
            self.result.block_number = self.w3.eth.block_number
            
            # Gas price
            gas_price_wei = self.w3.eth.gas_price
            self.result.gas_price = self.w3.from_wei(gas_price_wei, "gwei")
            
            # Client version
            try:
                self.result.client_version = self.w3.client_version
            except Exception:
                self.result.client_version = "Unknown"
            
            # Protocol version
            try:
                self.result.protocol_version = str(self.w3.eth.protocol_version)
            except Exception:
                self.result.protocol_version = "Unknown"
            
            # Network ID
            try:
                self.result.network_id = self.w3.eth.chain_id
            except Exception:
                self.result.network_id = 0
            
            logger.info(f"Node info: Chain {self.result.chain_id}, Block {self.result.block_number}")
            
        except Exception as error:
            self.result.issues.append(f"Error getting node info: {str(error)}")
            logger.error(f"Error getting node info: {error}")

    def _check_sync_status(self) -> None:
        """
        Check if the node is fully synced.
        """
        try:
            sync_status = self.w3.eth.syncing
            
            if isinstance(sync_status, bool):
                self.result.is_syncing = sync_status
            else:
                self.result.is_syncing = True
                self.result.details["sync_progress"] = {
                    "current_block": sync_status.get("currentBlock"),
                    "highest_block": sync_status.get("highestBlock"),
                    "known_states": sync_status.get("knownStates"),
                    "pulled_states": sync_status.get("pulledStates"),
                    "starting_block": sync_status.get("startingBlock"),
                }
                
                # Calculate sync percentage
                current = sync_status.get("currentBlock", 0)
                highest = sync_status.get("highestBlock", 1)
                if highest > 0:
                    progress = round((current / highest) * 100, 2)
                    self.result.details["sync_percentage"] = progress
                    logger.info(f"Syncing: {progress}% complete")
            
            if not self.result.is_syncing:
                logger.info("✅ Node is fully synced")
                
        except Exception as error:
            self.result.issues.append(f"Error checking sync status: {str(error)}")
            logger.error(f"Error checking sync status: {error}")

    def _detect_node_type(self) -> None:
        """
        Detect the node type (full, archive, light).
        """
        try:
            # Check if it's an archive node by trying to get older state
            try:
                self.w3.eth.get_balance(
                    "0x0000000000000000000000000000000000000000",
                    block_identifier=0
                )
                self.result.is_archive = True
                self.result.node_type = "Archive Node"
                logger.info("✅ Archive node detected")
            except Exception:
                self.result.is_archive = False
                self.result.node_type = "Full Node"
                logger.info("Full node detected (not archive)")
            
            # Check if it's a light node
            try:
                self.w3.eth.get_block(0, full_transactions=True)
            except Exception:
                if self.result.node_type == "Full Node":
                    self.result.node_type = "Light Node"
                    self.result.details["light_node_detected"] = True
                    logger.info("Light node detected")
                    
        except Exception as error:
            logger.warning(f"Could not determine node type: {error}")

    def _measure_performance(self) -> None:
        """
        Measure node performance metrics.
        """
        try:
            # Measure block retrieval time
            start_time = time.time()
            self.w3.eth.get_block(self.result.block_number)
            block_time = round((time.time() - start_time) * 1000, 2)
            
            # Measure balance retrieval time
            start_time = time.time()
            self.w3.eth.get_balance("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
            balance_time = round((time.time() - start_time) * 1000, 2)
            
            self.result.details["performance"] = {
                "block_retrieval_ms": block_time,
                "balance_retrieval_ms": balance_time,
                "average_response_ms": round((block_time + balance_time) / 2, 2),
            }
            
            logger.info(f"Performance: Block {block_time}ms, Balance {balance_time}ms")
            
        except Exception as error:
            logger.warning(f"Error measuring performance: {error}")

    def _check_peers(self) -> None:
        """
        Check peer count.
        """
        try:
            try:
                self.result.peer_count = self.w3.net.peer_count
                logger.info(f"Peer count: {self.result.peer_count}")
            except Exception:
                self.result.peer_count = -1
                
        except Exception as error:
            logger.warning(f"Error checking peers: {error}")

    def _determine_health(self) -> None:
        """
        Determine overall node health status.
        """
        health_issues = []
        
        # Check connectivity
        if not self.result.is_connected:
            health_issues.append("Not connected")
            
        # Check sync status
        if self.result.is_syncing:
            health_issues.append("Node is syncing")
            
        # Check response time
        if self.result.response_time_ms > 2000:
            health_issues.append(f"High response time: {self.result.response_time_ms}ms")
            
        # Check peer count
        if self.result.peer_count > 0 and self.result.peer_count < 3:
            health_issues.append("Low peer count")
            
        # Determine overall health
        if not health_issues:
            self.result.health_status = "Healthy 🟢"
        elif len(health_issues) <= 2:
            self.result.health_status = "Degraded 🟡"
        else:
            self.result.health_status = "Unhealthy 🔴"
            
        self.result.issues = health_issues
        logger.info(f"Health status: {self.result.health_status}")


def validate_node(rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a blockchain node.

    Parameters
    ----------
    rpc_url : str, optional
        RPC URL to validate.

    Returns
    -------
    Dict[str, Any]
        Node validation report.
    """
    validator = NodeValidator(rpc_url)
    return validator.validate()


def compare_nodes(node_urls: List[str]) -> Dict[str, Any]:
    """
    Compare multiple nodes for consensus validation.

    Parameters
    ----------
    node_urls : List[str]
        List of node RPC URLs to compare.

    Returns
    -------
    Dict[str, Any]
        Comparison report.
    """
    logger.info(f"Comparing {len(node_urls)} nodes")

    results = []
    latest_blocks = {}
    chain_ids = set()

    for url in node_urls:
        try:
            logger.info(f"Validating node: {url}")

            validator = NodeValidator(url)
            result = validator.validate()

            # Always include the RPC URL in the result
            result["rpc_url"] = url

            # ---------------- DEBUG ----------------
            logger.info("=" * 70)
            logger.info(f"Validation Result for {url}")
            logger.info(result)
            logger.info("=" * 70)
            # ---------------------------------------

            results.append(result)

            if result.get("is_connected", False):
                latest_blocks[url] = result.get("block_number", 0)

                chain_id = result.get("chain_id")
                if chain_id is not None:
                    chain_ids.add(chain_id)

        except Exception as error:
            logger.exception(f"Error validating node {url}")

            results.append({
                "rpc_url": url,
                "is_connected": False,
                "health_status": "Failed",
                "block_number": 0,
                "chain_id": None,
                "error": str(error),
            })

    # Summary statistics
    nodes_connected = sum(
        1 for r in results if r.get("is_connected", False)
    )

    all_on_same_chain = (
        len(chain_ids) == 1 and nodes_connected > 0
    )

    if latest_blocks:
        block_heights = list(latest_blocks.values())
        max_block = max(block_heights)
        min_block = min(block_heights)
        block_diff = max_block - min_block
        is_consistent = block_diff < 10
    else:
        block_diff = None
        is_consistent = False

    return {
        "nodes_checked": len(node_urls),
        "nodes_connected": nodes_connected,
        "same_chain": all_on_same_chain,
        "block_height_consistent": is_consistent,
        "chain_ids": sorted(chain_ids),
        "latest_blocks": latest_blocks,
        "block_difference": block_diff,
        "results": results,
        "consensus_status": (
            "✅ Reached"
            if (all_on_same_chain and is_consistent)
            else "❌ Not Reached"
        ),
    }
###############################################################################
# End of File
###############################################################################