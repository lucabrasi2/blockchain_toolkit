"""
Universal Blockchain Platform (UBP)

Module:
    Token Service

Purpose:
    Business logic for Ethereum token operations.

Responsibilities:
    • Get token metadata (name, symbol, decimals)
    • Get token balance
    • Get total supply
    • Generate token reports

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.logger import get_logger
from ethereum.tokens import (
    get_token_metadata,
    get_token_balance,
    get_total_supply,
    is_erc20,
)
from ethereum.wallets import get_eth_balance


logger = get_logger(__name__)


class TokenService:
    """
    Token business logic service.
    """

    def __init__(self):
        """Initialize the Token Service."""
        logger.info("TokenService initialized.")

    def get_token_report(self, address: str, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete token report.

        Parameters
        ----------
        address : str
            Token contract address.
        wallet_address : str, optional
            Wallet address to check balance for.

        Returns
        -------
        Dict[str, Any]
            Token report.
        """
        logger.info(f"Generating token report for {address}")

        # Check if it's an ERC-20 token
        try:
            is_token = is_erc20(address)
        except Exception as error:
            logger.error(f"Error checking ERC-20: {error}")
            is_token = False

        if not is_token:
            return {
                "address": address,
                "is_token": False,
                "error": "Not an ERC-20 token",
            }

        # Get token metadata
        try:
            metadata = get_token_metadata(address)
        except Exception as error:
            logger.error(f"Error getting metadata: {error}")
            metadata = {"name": "Unknown", "symbol": "Unknown", "decimals": 18}

        # Get total supply
        try:
            total_supply = get_total_supply(address)
        except Exception as error:
            logger.error(f"Error getting total supply: {error}")
            total_supply = None

        # Get token balance for wallet if provided
        balance = None
        if wallet_address:
            try:
                balance = get_token_balance(address, wallet_address)
            except Exception as error:
                logger.error(f"Error getting token balance: {error}")
                balance = None

        # Build the report
        report = {
            "address": address,
            "is_token": True,
            "name": metadata.get("name", "Unknown"),
            "symbol": metadata.get("symbol", "Unknown"),
            "decimals": metadata.get("decimals", 18),
            "total_supply": total_supply,
            "balance": balance,
        }

        logger.info(f"Token report generated for {address}")
        return report

    def get_token_info(self, address: str) -> Dict[str, Any]:
        """
        Get basic token information.

        Parameters
        ----------
        address : str
            Token contract address.

        Returns
        -------
        Dict[str, Any]
            Token information.
        """
        logger.info(f"Getting token info for {address}")

        try:
            is_token = is_erc20(address)
        except Exception:
            is_token = False

        if not is_token:
            return {
                "address": address,
                "is_token": False,
                "error": "Not an ERC-20 token",
            }

        try:
            metadata = get_token_metadata(address)
            total_supply = get_total_supply(address)
        except Exception as error:
            logger.error(f"Error getting token info: {error}")
            metadata = {"name": "Unknown", "symbol": "Unknown", "decimals": 18}
            total_supply = None

        return {
            "address": address,
            "is_token": True,
            "name": metadata.get("name", "Unknown"),
            "symbol": metadata.get("symbol", "Unknown"),
            "decimals": metadata.get("decimals", 18),
            "total_supply": total_supply,
        }

    def get_token_balance(self, token_address: str, wallet_address: str) -> Dict[str, Any]:
        """
        Get token balance for a wallet.

        Parameters
        ----------
        token_address : str
            Token contract address.
        wallet_address : str
            Wallet address.

        Returns
        -------
        Dict[str, Any]
            Token balance information.
        """
        logger.info(f"Getting token balance for {wallet_address}")

        try:
            is_token = is_erc20(token_address)
        except Exception:
            is_token = False

        if not is_token:
            return {
                "error": "Not an ERC-20 token",
                "balance": 0,
            }

        try:
            balance = get_token_balance(token_address, wallet_address)
            metadata = get_token_metadata(token_address)
            decimals = metadata.get("decimals", 18)
        except Exception as error:
            logger.error(f"Error getting token balance: {error}")
            return {
                "error": str(error),
                "balance": 0,
            }

        return {
            "token_address": token_address,
            "wallet_address": wallet_address,
            "balance": balance,
            "decimals": decimals,
            "formatted_balance": balance / (10 ** decimals) if balance else 0,
        }