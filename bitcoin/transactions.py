"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Transactions

Purpose:
    Bitcoin transaction utilities.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from bitcoin.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


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
        
        # Clean the hash - remove 0x prefix if present
        if tx_hash.startswith('0x'):
            tx_hash = tx_hash[2:]
        
        result = client.get_transaction(tx_hash)
        
        if "error" in result:
            return {"hash": tx_hash, "error": result["error"]}
        
        # Extract data from the API response
        # The blockchain.info API returns 'inputs' and 'outputs'
        inputs = result.get("inputs", [])
        outputs = result.get("outputs", [])
        
        # Format inputs
        formatted_inputs = []
        for inp in inputs:
            prev_out = inp.get("prev_out", {})
            formatted_inputs.append({
                "hash": prev_out.get("hash"),
                "index": prev_out.get("n"),
                "value": prev_out.get("value", 0) / 100_000_000,
            })
        
        # Format outputs
        formatted_outputs = []
        for out in outputs:
            formatted_outputs.append({
                "address": out.get("addr"),
                "value": out.get("value", 0) / 100_000_000,
            })
        
        # Get block height
        block_height = result.get("block_height")
        
        # Calculate confirmations
        confirmations = 0
        if block_height:
            # Use the client's latest block if available
            latest = client.get_latest_block()
            if latest and "number" in latest:
                confirmations = latest.get("number", 0) - block_height + 1
        
        return {
            "hash": result.get("hash"),
            "block_hash": result.get("block_hash"),
            "block_height": block_height,
            "confirmations": confirmations,
            "timestamp": result.get("timestamp"),
            "size": result.get("size"),
            "weight": result.get("weight"),
            "version": result.get("version"),
            "locktime": result.get("locktime"),
            "fee": result.get("fee", 0),
            "inputs_count": len(inputs),
            "outputs_count": len(outputs),
            "inputs": formatted_inputs[:5],
            "outputs": formatted_outputs[:5],
            "total_input": sum(o["value"] for o in formatted_outputs),
        }
        
    except Exception as error:
        logger.error(f"Error getting transaction: {error}")
        return {"hash": tx_hash, "error": str(error)}


def get_transaction_status(tx_hash: str) -> str:
    """
    Get Bitcoin transaction status.

    Parameters
    ----------
    tx_hash : str
        Transaction hash.

    Returns
    -------
    str
        Transaction status.
    """
    try:
        tx = get_transaction(tx_hash)
        
        if "error" in tx:
            return "Unknown"
        
        confirmations = tx.get("confirmations", 0)
        
        if confirmations >= 6:
            return "Confirmed (6+ confirmations)"
        elif confirmations >= 1:
            return f"Pending ({confirmations} confirmations)"
        else:
            return "Unconfirmed (0 confirmations)"
        
    except Exception as error:
        logger.error(f"Error getting transaction status: {error}")
        return "Unknown"


###############################################################################
# End of File
###############################################################################