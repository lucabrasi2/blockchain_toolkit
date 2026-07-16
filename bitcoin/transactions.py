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
        tx = client.get_transaction(tx_hash)
        
        if "error" in tx:
            return {"hash": tx_hash, "error": tx["error"]}
        
        vin = tx.get("vin", [])
        vout = tx.get("vout", [])
        
        inputs = []
        for inp in vin:
            if "txid" in inp:
                inputs.append(inp.get("txid"))
        
        outputs = []
        for out in vout:
            address = out.get("scriptPubKey", {}).get("address")
            if not address:
                address = out.get("scriptPubKey", {}).get("addresses", [None])[0]
            outputs.append({
                "address": address,
                "amount": out.get("value", 0),
            })
        
        return {
            "hash": tx.get("txid"),
            "block_hash": tx.get("blockhash"),
            "block_number": tx.get("height", 0),
            "confirmations": tx.get("confirmations", 0),
            "timestamp": tx.get("time"),
            "size": tx.get("size"),
            "weight": tx.get("weight"),
            "version": tx.get("version"),
            "locktime": tx.get("locktime"),
            "fee": tx.get("fee"),
            "inputs_count": len(inputs),
            "outputs_count": len(outputs),
            "inputs": inputs[:5],
            "outputs": outputs[:5],
            "total_input": sum(o.get("amount", 0) for o in outputs),
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