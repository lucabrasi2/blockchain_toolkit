"""
Universal Blockchain Platform (UBP)

Module:
    TRON Wallet Service

Purpose:
    Business logic for TRON wallet operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.logger import get_logger
from tron.wallets import get_trx_balance, is_valid_address, get_account_info
from tron.contracts import is_contract

logger = get_logger(__name__)


class TronWalletService:
    """
    TRON wallet business logic service.
    """

    def __init__(self):
        logger.info("TronWalletService initialized.")

    def get_wallet_report(self, address: str) -> Dict[str, Any]:
        """
        Generate a complete wallet report.

        Parameters
        ----------
        address : str
            TRON wallet address.

        Returns
        -------
        Dict[str, Any]
            Wallet report.
        """
        logger.info(f"Generating wallet report for {address}")

        if not is_valid_address(address):
            return {
                "address": address,
                "error": "Invalid TRON address",
                "is_valid": False,
            }

        balance = get_trx_balance(address)
        is_contract_address = is_contract(address)
        account_info = get_account_info(address)

        return {
            "address": address,
            "balance_trx": balance.get("trx", 0),
            "balance_sun": balance.get("sun", 0),
            "is_contract": is_contract_address,
            "classification": "Contract" if is_contract_address else "EOA",
            "energy": account_info.get("energy", 0),
            "bandwidth": account_info.get("bandwidth", 0),
            "create_time": account_info.get("create_time"),
        }
