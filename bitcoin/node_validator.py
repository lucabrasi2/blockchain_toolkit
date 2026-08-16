"""
Universal Blockchain Platform (UBP)
Module: Bitcoin Node Validator
Purpose: Bitcoin node validation and health checking
Author: UBP Engineering Team
Version: 2.0.0
"""
from typing import Dict, Any, Optional, List
import time
import requests
from core.logger import get_logger
from bitcoin.connection import get_connection

logger = get_logger(__name__)


class BitcoinNodeValidator:
    """
    Bitcoin node validation and health checking.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialize the Bitcoin node validator.
        
        Parameters
        ----------
        rpc_url : str, optional
            RPC URL to validate.
        """
        self.rpc_url = rpc_url
    
    def validate(self) -> Dict[str, Any]:
        """
        Perform a complete node validation.
        
        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        result = {
            "rpc_url": self.rpc_url or "default",
            "is_connected": False,
            "is_syncing": False,
            "node_type": "Unknown",
            "chain_id": 0,
            "network_id": None,
            "block_number": 0,
            "peer_count": 0,
            "response_time_ms": 0.0,
            "client_version": "Unknown",
            "protocol_version": None,
            "archive_node": False,
            "gas_price": None,
            "health_status": "Unknown",
            "issues": [],
            "details": {},
        }
        
        try:
            start = time.perf_counter()
            
            # Get connection
            client = get_connection(self.rpc_url)
            
            # Check connection
            if client.is_connected():
                result["is_connected"] = True
                
                # Get blockchain info
                try:
                    info = client.get_blockchain_info()
                    if info and "error" not in info:
                        result["block_number"] = info.get("blocks", 0)
                        result["node_type"] = "Full Node"
                    else:
                        result["issues"].append("Could not fetch blockchain info")
                except Exception as e:
                    result["issues"].append(f"Blockchain info error: {e}")
                
                # Get network info
                try:
                    network_info = client.get_network_info()
                    if network_info:
                        result["peer_count"] = network_info.get("connections", 0)
                        result["client_version"] = str(network_info.get("version", "Unknown"))
                        result["protocol_version"] = network_info.get("protocolversion")
                except Exception as e:
                    result["issues"].append(f"Network info error: {e}")
                
                # Get latest block
                try:
                    latest = client.get_latest_block()
                    if latest and "error" not in latest:
                        result["block_number"] = latest.get("number", result["block_number"])
                except Exception as e:
                    result["issues"].append(f"Latest block error: {e}")
                
                # Calculate response time
                elapsed = (time.perf_counter() - start) * 1000
                result["response_time_ms"] = round(elapsed, 2)
                
                # Determine health
                issues_count = len(result["issues"])
                if issues_count == 0:
                    result["health_status"] = "Healthy"
                elif issues_count <= 2:
                    result["health_status"] = "Degraded"
                else:
                    result["health_status"] = "Unhealthy"
                    
                logger.info("Bitcoin node validation successful")
            else:
                result["is_connected"] = False
                result["issues"].append("Node is not reachable")
                result["health_status"] = "Unhealthy"
                
        except Exception as e:
            result["is_connected"] = False
            result["issues"].append(str(e))
            result["health_status"] = "Unhealthy"
            logger.error(f"Bitcoin node validation error: {e}")
        
        return result


def validate_node(rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a single Bitcoin node.
    
    Parameters
    ----------
    rpc_url : str, optional
        RPC endpoint.
        
    Returns
    -------
    Dict[str, Any]
        Validation report.
    """
    validator = BitcoinNodeValidator(rpc_url)
    return validator.validate()


def compare_nodes(node_urls: List[str]) -> Dict[str, Any]:
    """
    Compare multiple Bitcoin nodes.
    
    Parameters
    ----------
    node_urls : List[str]
        RPC URLs.
        
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
            report = validator.validate()
            results.append(report)
            if report.get("is_connected"):
                latest_blocks[url] = report.get("block_number", 0)
        except Exception as e:
            logger.error(f"Error validating node {url}: {e}")
            results.append({
                "rpc_url": url,
                "is_connected": False,
                "health_status": "Unhealthy",
                "error": str(e),
            })
    
    # Determine consensus
    if latest_blocks:
        heights = list(latest_blocks.values())
        highest = max(heights)
        lowest = min(heights)
        difference = highest - lowest
        consistent = difference <= 10
    else:
        difference = None
        consistent = False
    
    return {
        "nodes_checked": len(node_urls),
        "nodes_connected": sum(1 for r in results if r.get("is_connected")),
        "same_chain": True,
        "block_height_consistent": consistent,
        "chain_ids": [0],
        "latest_blocks": latest_blocks,
        "block_difference": difference,
        "results": results,
        "consensus_status": "Reached" if consistent else "Not Reached",
    }