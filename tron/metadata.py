"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.metadata

Purpose
-------
TRON contract metadata retrieval.

This module provides metadata retrieval for TRON smart contracts.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from typing import Dict, Any, Optional
import requests

from tron.wallets import is_valid_address
from tron.contracts import is_contract, is_trc20, get_trc20_metadata
from core.logger import get_logger

logger = get_logger(__name__)


TRON_API_URL = "https://api.trongrid.io"


class TronContractMetadata:
    """
    TRON contract metadata container.
    """

    def __init__(self, address: str):
        self.address = address
        self.is_contract = False
        self.is_trc20 = False
        self.name = None
        self.symbol = None
        self.decimals = None
        self.total_supply = None
        self.owner = None
        self.standard = None
        self.chain_id = None
        self.block_number = None
        self._fetch_metadata()

    def _fetch_metadata(self):
        """Fetch contract metadata from the blockchain."""
        try:
            self.is_contract = is_contract(self.address)
            if not self.is_contract:
                return

            self.is_trc20 = is_trc20(self.address)

            if self.is_trc20:
                metadata = get_trc20_metadata(self.address)
                self.name = metadata.get("name")
                self.symbol = metadata.get("symbol")
                self.decimals = metadata.get("decimals")
                self.total_supply = metadata.get("total_supply")
                self.standard = "TRC-20"

            # Get contract info
            url = f"{TRON_API_URL}/wallet/getcontractinfo"
            response = requests.post(
                url,
                json={"contract_address": self.address},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data and data.get("origin_address"):
                    self.owner = data.get("origin_address")

            # Get chain info
            response = requests.post(f"{TRON_API_URL}/wallet/getnowblock", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.block_number = data.get("block_header", {}).get("raw_data", {}).get("number")
                self.chain_id = 0  # TRON doesn't have chain ID like Ethereum

            logger.info(f"Fetched metadata for {self.address}")

        except Exception as error:
            logger.error(f"Error fetching metadata: {error}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "address": self.address,
            "is_contract": self.is_contract,
            "is_trc20": self.is_trc20,
            "name": self.name,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "owner": self.owner,
            "standard": self.standard,
            "chain_id": self.chain_id,
            "block_number": self.block_number,
        }


def get_contract_metadata(address: str) -> TronContractMetadata:
    """
    Get contract metadata.

    Parameters
    ----------
    address : str
        TRON contract address.

    Returns
    -------
    TronContractMetadata
        Contract metadata instance.
    """
    logger.info(f"Getting metadata for {address}")
    return TronContractMetadata(address)


###############################################################################
# End of File
###############################################################################
