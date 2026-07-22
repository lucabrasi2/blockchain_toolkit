"""
Universal Blockchain Platform (UBP)

Module:
    Bitcoin Wallet Service

Purpose:
    Business logic for Bitcoin wallet operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.logger import get_logger
from bitcoin.wallets import get_btc_balance, is_valid_address, get_address_info

logger = get_logger(__name__)


class BitcoinWalletService:
    """
    Bitcoin wallet business logic service.
    """

    def __init__(self):
        logger.info("BitcoinWalletService initialized.")

    def get_wallet_report(self, address: str) -> Dict[str, Any]:
        """
        Generate a complete wallet report.

        Parameters
        ----------
        address : str
            Bitcoin wallet address.

        Returns
        -------
        Dict[str, Any]
            Wallet report.
        """
        logger.info(f"Generating wallet report for {address}")

        if not is_valid_address(address):
            return {
                "address": address,
                "error": "Invalid Bitcoin address",
                "is_valid": False,
            }

        balance = get_btc_balance(address)
        address_info = get_address_info(address)

        return {
            "address": address,
            "balance_btc": balance.get("btc", 0),
            "balance_satoshis": balance.get("satoshis", 0),
            "is_contract": False,
            "classification": "Bitcoin Address",
            "transaction_count": balance.get("transaction_count", 0),
            "total_received": balance.get("total_received", 0),
            "total_sent": balance.get("total_sent", 0),
            "is_valid": address_info.get("isvalid", True),
            "is_script": address_info.get("isscript", False),
            "is_witness": address.startswith('bc1'),
            "script_type": "Witness" if address.startswith('bc1') else "Legacy",
        }