"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Transactions

Purpose:
    Bitcoin transaction utilities.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.1.0
"""

from typing import Dict, Any

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


SATOSHI = 100_000_000


def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    Get Bitcoin transaction by hash.

    Parameters
    ----------
    tx_hash : str
        Transaction hash.

    Returns
    -------
    Dict[str, Any]
        Transaction information.
    """

    try:
        client = get_connection()

        # Remove optional 0x prefix
        if tx_hash.startswith("0x"):
            tx_hash = tx_hash[2:]

        result = client.get_transaction(tx_hash)

        if not result:
            return {
                "hash": tx_hash,
                "error": "Transaction not found",
            }

        if "error" in result:
            return {
                "hash": tx_hash,
                "error": result["error"],
            }

        #######################################################################
        # Inputs
        #######################################################################

        raw_inputs = result.get("inputs", [])
        formatted_inputs = []

        for inp in raw_inputs:

            prev_out = inp.get("prev_out", {})

            formatted_inputs.append(
                {
                    "address": (
                        prev_out.get("addr")
                        or prev_out.get("address")
                        or prev_out.get("scriptpubkey_address")
                        or "Unknown"
                    ),
                    "hash": prev_out.get("hash"),
                    "index": prev_out.get("n"),
                    "value": prev_out.get("value", 0) / SATOSHI,
                }
            )

        #######################################################################
        # Outputs
        #######################################################################

        raw_outputs = result.get("outputs", [])

        # Some APIs use "out"
        if not raw_outputs:
            raw_outputs = result.get("out", [])

        formatted_outputs = []

        for out in raw_outputs:

            formatted_outputs.append(
                {
                    "address": (
                        out.get("addr")
                        or out.get("address")
                        or out.get("scriptpubkey_address")
                        or "Unknown"
                    ),
                    "value": out.get("value", 0) / SATOSHI,
                }
            )

        #######################################################################
        # Block information
        #######################################################################

        block_height = (
            result.get("block_height")
            or result.get("height")
            or result.get("block_number")
        )

        block_hash = (
            result.get("block_hash")
            or result.get("blockhash")
        )

        #######################################################################
        # Confirmations
        #######################################################################

        confirmations = result.get("confirmations", 0)

        if confirmations == 0 and block_height is not None:

            try:

                latest = client.get_latest_block()

                latest_height = (
                    latest.get("number")
                    or latest.get("height")
                    or latest.get("block_height")
                )

                if latest_height is not None:
                    confirmations = latest_height - block_height + 1

            except Exception:
                pass

        #######################################################################
        # Totals
        #######################################################################

        total_input = sum(
            item["value"] for item in formatted_inputs
        )

        total_output = sum(
            item["value"] for item in formatted_outputs
        )

        #######################################################################
        # Report
        #######################################################################

        return {

            "hash": result.get("hash", tx_hash),

            # Support both names for compatibility
            "block_number": block_height,
            "block_height": block_height,

            "block_hash": block_hash,

            "confirmations": confirmations,

            "timestamp": (
                result.get("timestamp")
                or result.get("time")
            ),

            "size": result.get("size"),

            "weight": result.get("weight"),

            "version": result.get("version") or result.get("ver"),

            "locktime": result.get("locktime") or result.get("lock_time"),

            "fee": result.get("fee", 0),

            "inputs_count": len(raw_inputs),

            "outputs_count": len(raw_outputs),

            "inputs": formatted_inputs[:5],

            "outputs": formatted_outputs[:5],

            "total_input": total_input,

            "total_output": total_output,
        }

    except Exception as error:

        logger.error(
            f"Error getting transaction: {error}"
        )

        return {
            "hash": tx_hash,
            "error": str(error),
        }


def get_transaction_status(tx_hash: str) -> str:
    """
    Get Bitcoin transaction status.
    """

    try:

        tx = get_transaction(tx_hash)

        if "error" in tx:
            return "Unknown"

        confirmations = tx.get("confirmations", 0)

        if confirmations >= 6:
            return "Confirmed (6+ confirmations)"

        if confirmations >= 1:
            return f"Pending ({confirmations} confirmations)"

        return "Unconfirmed (0 confirmations)"

    except Exception as error:

        logger.error(
            f"Error getting transaction status: {error}"
        )

        return "Unknown"


###############################################################################
# End of File
###############################################################################