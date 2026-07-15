"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Ethereum Contract Metadata

Author  : Jaramogi Diddy

Description
-----------
Provides metadata retrieval for Ethereum smart contracts.

Responsibilities
----------------
• Fetch contract name and symbol
• Get token decimals
• Retrieve total supply
• Get owner information
• Fetch contract version
• Get metadata from various standards
"""

from __future__ import annotations

from typing import Any, Optional, Dict

from web3 import Web3
from web3.contract import Contract

from ethereum.connection import get_connection
from ethereum.wallets import is_valid_address
from ethereum.abi import (
    ERC20_ABI,
    ERC721_ABI,
    ERC1155_ABI,
    OWNER_ABI,
    METADATA_ABI,
)

from constants.contract_types import (
    ERC20,
    ERC721,
    ERC1155,
    CONTRACT,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

from core.logger import get_logger


logger = get_logger(__name__)


###############################################################################
# Internal Helpers
###############################################################################


def _get_web3() -> Web3:
    """Return the active Web3 connection."""
    return get_connection()


def _validate_address(address: str) -> None:
    """Validate an Ethereum address."""
    if not is_valid_address(address):
        raise InvalidWalletAddressError(f"Invalid address: {address}")


def _get_contract(address: str, abi: list[dict[str, Any]]) -> Contract:
    """Create a Web3 contract instance."""
    _validate_address(address)
    w3 = _get_web3()
    return w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=abi,
    )


def _safe_call(function, default=None):
    """Execute a blockchain call safely."""
    try:
        return function.call()
    except Exception:
        return default


###############################################################################
# Contract Metadata Classes
###############################################################################


class ContractMetadata:
    """
    Base contract metadata container.
    """
    
    def __init__(self):
        self.address: str = ""
        self.contract_type: str = CONTRACT
        self.name: Optional[str] = None
        self.symbol: Optional[str] = None
        self.decimals: Optional[int] = None
        self.total_supply: Optional[int] = None
        self.owner: Optional[str] = None
        self.version: Optional[str] = None
        self.standard: Optional[str] = None
        self.chain_id: Optional[int] = None
        self.block_number: Optional[int] = None
        self.timestamp: Optional[int] = None
        
    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return {
            "address": self.address,
            "contract_type": self.contract_type,
            "name": self.name,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "owner": self.owner,
            "version": self.version,
            "standard": self.standard,
            "chain_id": self.chain_id,
            "block_number": self.block_number,
            "timestamp": self.timestamp,
        }


class ERC20Metadata(ContractMetadata):
    """
    ERC-20 token metadata.
    """
    
    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.contract_type = ERC20
        self.standard = "ERC-20"
        self._fetch_metadata()
    
    def _fetch_metadata(self):
        """Fetch ERC-20 metadata from the blockchain."""
        try:
            contract = _get_contract(self.address, ERC20_ABI)
            
            # Fetch basic token info
            self.name = _safe_call(contract.functions.name())
            self.symbol = _safe_call(contract.functions.symbol())
            self.decimals = _safe_call(contract.functions.decimals())
            self.total_supply = _safe_call(contract.functions.totalSupply())
            
            # Try to fetch owner if available
            try:
                owner_contract = _get_contract(self.address, OWNER_ABI)
                self.owner = _safe_call(owner_contract.functions.owner())
            except Exception:
                pass
            
            # Try to fetch version if available
            try:
                version_contract = _get_contract(self.address, METADATA_ABI)
                self.version = _safe_call(version_contract.functions.version())
            except Exception:
                pass
            
            # Get chain info
            w3 = _get_web3()
            self.chain_id = w3.eth.chain_id
            self.block_number = w3.eth.block_number
            
            logger.info(f"Fetched ERC-20 metadata for {self.address}")
            
        except Exception as error:
            logger.error(f"Error fetching ERC-20 metadata: {error}")


class ERC721Metadata(ContractMetadata):
    """
    ERC-721 NFT metadata.
    """
    
    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.contract_type = ERC721
        self.standard = "ERC-721"
        self._fetch_metadata()
    
    def _fetch_metadata(self):
        """Fetch ERC-721 metadata from the blockchain."""
        try:
            contract = _get_contract(self.address, ERC721_ABI)
            
            # Fetch basic NFT info
            self.name = _safe_call(contract.functions.name())
            self.symbol = _safe_call(contract.functions.symbol())
            self.total_supply = _safe_call(contract.functions.totalSupply())
            
            # Try to fetch owner if available
            try:
                owner_contract = _get_contract(self.address, OWNER_ABI)
                self.owner = _safe_call(owner_contract.functions.owner())
            except Exception:
                pass
            
            # Get chain info
            w3 = _get_web3()
            self.chain_id = w3.eth.chain_id
            self.block_number = w3.eth.block_number
            
            logger.info(f"Fetched ERC-721 metadata for {self.address}")
            
        except Exception as error:
            logger.error(f"Error fetching ERC-721 metadata: {error}")


class ERC1155Metadata(ContractMetadata):
    """
    ERC-1155 Multi-Token metadata.
    """
    
    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.contract_type = ERC1155
        self.standard = "ERC-1155"
        self._fetch_metadata()
    
    def _fetch_metadata(self):
        """Fetch ERC-1155 metadata from the blockchain."""
        try:
            contract = _get_contract(self.address, ERC1155_ABI)
            
            # Try to fetch URI (if available)
            try:
                self.name = _safe_call(contract.functions.uri(0))
            except Exception:
                pass
            
            # Try to fetch owner if available
            try:
                owner_contract = _get_contract(self.address, OWNER_ABI)
                self.owner = _safe_call(owner_contract.functions.owner())
            except Exception:
                pass
            
            # Get chain info
            w3 = _get_web3()
            self.chain_id = w3.eth.chain_id
            self.block_number = w3.eth.block_number
            
            logger.info(f"Fetched ERC-1155 metadata for {self.address}")
            
        except Exception as error:
            logger.error(f"Error fetching ERC-1155 metadata: {error}")


###############################################################################
# Main Metadata Factory
###############################################################################


def get_contract_metadata(
    address: str,
    contract_type: str = CONTRACT,
) -> ContractMetadata:
    """
    Factory function to get contract metadata based on type.
    
    Parameters
    ----------
    address : str
        Ethereum contract address.
    contract_type : str
        Type of contract (ERC20, ERC721, ERC1155, CONTRACT).
    
    Returns
    -------
    ContractMetadata
        Contract metadata object.
    """
    
    logger.info(f"Getting metadata for {address} of type {contract_type}")
    
    _validate_address(address)
    
    if contract_type == ERC20:
        return ERC20Metadata(address)
    elif contract_type == ERC721:
        return ERC721Metadata(address)
    elif contract_type == ERC1155:
        return ERC1155Metadata(address)
    else:
        # Generic contract metadata
        metadata = ContractMetadata()
        metadata.address = address
        metadata.contract_type = CONTRACT

        # Try to get basic info
        try:
            w3 = _get_web3()
            metadata.chain_id = w3.eth.chain_id
            metadata.block_number = w3.eth.block_number
        except Exception:
            pass

        return metadata

