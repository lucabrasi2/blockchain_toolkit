"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Block Service

Purpose:
    Business logic for Bitcoin block operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.logger import get_logger
from bitcoin.blocks import get_block, get_latest_block

logger = get_logger(__name__)


class BitcoinBlockService:
    """
    Bitcoin block business logic service.
    """

    def __init__(self):
        logger.info("BitcoinBlockService initialized.")

    def get_block_report(self, block_identifier) -> Dict[str, Any]:
        """
        Generate a block report.

        Parameters
        ----------
        block_identifier : int or str
            Block height or hash.

        Returns
        -------
        Dict[str, Any]
            Block report.
        """
        logger.info(f"Getting block report for: {block_identifier}")

        if block_identifier == "latest":
            block = get_latest_block()
        else:
            block = get_block(block_identifier)

        if "error" in block:
            return {
                "error": block["error"],
                "number": None,
            }

        return {
            "number": block.get("number"),
            "hash": block.get("hash"),
            "previous_hash": block.get("previous_hash"),
            "next_hash": block.get("next_hash"),
            "timestamp": block.get("timestamp"),
            "transaction_count": block.get("transaction_count", 0),
            "size": block.get("size"),
            "weight": block.get("weight"),
            "difficulty": block.get("difficulty"),
            "version": block.get("version"),
            "nonce": block.get("nonce"),
            "bits": block.get("bits"),
            "merkle_root": block.get("merkle_root"),
            "transactions": block.get("transactions", [])[:10],
        }