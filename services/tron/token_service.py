"""
Universal Blockchain Platform (UBP)

Module:
    TRON Token Service

Purpose:
    Business logic for TRON token operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from tron.contracts import is_trc20, get_trc20_metadata, get_trc20_balance
from tron.wallets import is_valid_address

logger = get_logger(__name__)


class TronTokenService:
    """
    TRON token business logic service.
    """

    def __init__(self):
        logger.info("TronTokenService initialized.")

    def get_token_report(self, address: str, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a token report.

        Parameters
        ----------
        address : str
            TRC-20 token address.
        wallet_address : str, optional
            Wallet address to check balance for.

        Returns
        -------
        Dict[str, Any]
            Token report.
        """
        logger.info(f"Generating token report for {address}")

        if not is_valid_address(address):
            return {
                "address": address,
                "error": "Invalid TRON address",
                "is_valid": False,
            }

        is_trc20_token = is_trc20(address)

        if not is_trc20_token:
            return {
                "address": address,
                "is_token": False,
                "error": "Not a TRC-20 token",
            }

        metadata = get_trc20_metadata(address)

        report = {
            "address": address,
            "is_token": True,
            "name": metadata.get("name", "Unknown"),
            "symbol": metadata.get("symbol", "Unknown"),
            "decimals": metadata.get("decimals", 18),
            "total_supply": metadata.get("total_supply", 0),
        }

        if wallet_address:
            balance = get_trc20_balance(address, wallet_address)
            report["balance"] = balance

        return report
