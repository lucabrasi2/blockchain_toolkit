"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Connection

Purpose:
    Manage Bitcoin network connections using public API.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Any, Dict

from core.http_client import http_client
from core.logger import get_logger

logger = get_logger(__name__)


class BitcoinClient:
    """
    Bitcoin client using blockchain.info public API.
    """

    def __init__(self):
        self.base_url = "https://blockchain.info"

        logger.info(
            "✅ Bitcoin client initialized (public API)"
        )

    def get_latest_block(self) -> Dict[str, Any]:
        """
        Get the latest block.
        """

        try:

            response = http_client.get(
                f"{self.base_url}/latestblock",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            if data.get("hash"):

                return self.get_block(
                    data["hash"]
                )

            return {
                "error": "Could not fetch latest block"
            }

        except Exception as error:

            logger.error(
                f"Error getting latest block: {error}"
            )

            return {
                "error": str(error)
            }

    def get_block(
        self,
        block_identifier: Any,
    ) -> Dict[str, Any]:
        """
        Get block by height or hash.
        """

        try:

            if (
                isinstance(block_identifier, int)
                or (
                    isinstance(block_identifier, str)
                    and block_identifier.isdigit()
                )
            ):

                response = http_client.get(
                    f"{self.base_url}/block-height/{block_identifier}?format=json",
                    timeout=10,
                )

                response.raise_for_status()

                data = response.json()

                if (
                    data.get("blocks")
                    and len(data["blocks"]) > 0
                ):

                    block_hash = (
                        data["blocks"][0]["hash"]
                    )

                else:

                    return {
                        "error": (
                            f"Block {block_identifier} not found"
                        )
                    }

            else:

                block_hash = block_identifier

            response = http_client.get(
                f"{self.base_url}/rawblock/{block_hash}",
                timeout=10,
            )

            response.raise_for_status()

            block = response.json()

            return {

                "number": block.get("height"),

                "hash": block.get("hash"),

                "previous_hash": block.get("prev_block"),

                "next_hash": block.get("next_block"),

                "timestamp": block.get("time"),

                "merkle_root": block.get("mrkl_root"),

                "transaction_count": len(
                    block.get("tx", [])
                ),

                "size": block.get("size"),

                "weight": block.get("weight"),

                "version": block.get("ver"),

                "nonce": block.get("nonce"),

                "bits": block.get("bits"),

                "difficulty": block.get("difficulty"),

                "transactions": [
                    tx.get("hash")
                    for tx in block.get("tx", [])
                ],
            }

        except Exception as error:

            logger.error(
                f"Error getting block: {error}"
            )

            return {
                "error": str(error)
            }

    def get_address(
        self,
        address: str,
    ) -> Dict[str, Any]:
        """
        Get address information.
        """

        try:

            response = http_client.get(
                f"{self.base_url}/rawaddr/{address}",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:

                return {
                    "error": data["error"]
                }

            return {

                "address": address,

                "balance": (
                    data.get("final_balance", 0)
                    / 100_000_000
                ),

                "balance_satoshis": data.get(
                    "final_balance",
                    0,
                ),

                "transaction_count": data.get(
                    "n_tx",
                    0,
                ),

                "total_received": (
                    data.get("total_received", 0)
                    / 100_000_000
                ),

                "total_sent": (
                    data.get("total_sent", 0)
                    / 100_000_000
                ),
            }

        except Exception as error:

            logger.error(
                f"Error getting address: {error}"
            )

            return {
                "error": str(error)
            }

    def get_transaction(
        self,
        tx_hash: str,
    ) -> Dict[str, Any]:
        """
        Get transaction by hash.
        """

        try:

            response = http_client.get(
                f"{self.base_url}/rawtx/{tx_hash}",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:

                return {
                    "error": data["error"]
                }

            return {

                "hash": data.get("hash"),

                "block_hash": data.get("block_hash"),

                "block_height": data.get("block_height"),

                "timestamp": data.get("time"),

                "size": data.get("size"),

                "weight": data.get("weight"),

                "version": data.get("ver"),

                "lock_time": data.get("lock_time"),

                "fee": data.get("fee"),

                "inputs": data.get("inputs", []),

                "outputs": data.get("out", []),
            }

        except Exception as error:

            logger.error(
                f"Error getting transaction: {error}"
            )

            return {
                "error": str(error)
            }


def get_connection() -> BitcoinClient:
    """
    Get a Bitcoin connection.

    Returns
    -------
    BitcoinClient
        Bitcoin client instance.
    """

    return BitcoinClient()


###############################################################################
# End of File
###############################################################################