"""
Universal Blockchain Platform (UBP)

Module:
    TRON Contract Service

Purpose:
    Business logic for TRON contract operations.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.logger import get_logger
from tron.contracts import is_contract, is_trc20, get_trc20_metadata
from tron.wallets import is_valid_address

logger = get_logger(__name__)


class TronContractService:
    """
    TRON contract business logic service.
    """

    def __init__(self):
        logger.info("TronContractService initialized.")

    def get_contract_report(self, address: str) -> Dict[str, Any]:
        """
        Generate a complete contract report.

        Parameters
        ----------
        address : str
            TRON contract address.

        Returns
        -------
        Dict[str, Any]
            Contract report.
        """
        logger.info(f"Generating contract report for {address}")

        if not is_valid_address(address):
            return {
                "address": address,
                "error": "Invalid TRON address",
                "is_valid": False,
            }

        is_contract_address = is_contract(address)
        is_trc20_token = is_trc20(address) if is_contract_address else False

        report = {
            "address": address,
            "is_contract": is_contract_address,
            "classification": "TRC-20 Token" if is_trc20_token else "Contract" if is_contract_address else "EOA",
        }

        if is_trc20_token:
            metadata = get_trc20_metadata(address)
            report.update({
                "name": metadata.get("name", "Unknown"),
                "symbol": metadata.get("symbol", "Unknown"),
                "decimals": metadata.get("decimals", 18),
                "total_supply": metadata.get("total_supply", 0),
            })

        return report
