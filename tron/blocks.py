"""
Universal Blockchain Platform (UBP)

Module:
    TRON Blocks

Purpose:
    TRON block utilities using HTTP API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import requests
from typing import Dict, Any

from core.logger import get_logger

logger = get_logger(__name__)

TRON_API_URL = "https://api.trongrid.io"


def get_latest_block_number() -> int:
    """
    Get the latest TRON block number.
    """
    try:
        response = requests.post(
            f"{TRON_API_URL}/wallet/getnowblock",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data.get("block_header", {})
                .get("raw_data", {})
                .get("number", 0)
        )

    except Exception as error:
        logger.error(f"Error getting latest block: {error}")
        return 0


def get_block(block_identifier: int) -> Dict[str, Any]:
    """
    Get TRON block by number.
    """
    try:
        response = requests.post(
            f"{TRON_API_URL}/wallet/getblockbynum",
            json={"num": block_identifier},
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        raw_header = data.get("block_header", {}).get("raw_data", {})
        transactions = data.get("transactions", [])

        tx_hashes = [
            tx.get("txID")
            for tx in transactions
            if tx.get("txID")
        ]

        return {
            "number": raw_header.get("number"),
            "hash": data.get("blockID") or data.get("blockid"),
            "parent_hash": raw_header.get("parentHash"),
            "timestamp": raw_header.get("timestamp"),
            "version": raw_header.get("version"),
            "witness_address": raw_header.get("witness_address"),
            "transaction_count": len(tx_hashes),
            "transactions": tx_hashes,
        }

    except Exception as error:
        logger.error(f"Error getting block: {error}")

        return {
            "number": block_identifier,
            "error": str(error),
        }