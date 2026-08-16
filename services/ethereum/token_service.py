"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.token_service

Purpose
-------
Business logic for Ethereum token operations.

Responsibilities
----------------
• Retrieve ERC-20 token metadata
• Retrieve token balances
• Retrieve total supply
• Generate controller-friendly token reports

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

from __future__ import annotations

from typing import Any

from core.logger import get_logger

from ethereum.tokens import (
    get_token_balance as _get_token_balance,
    get_token_metadata as _get_token_metadata,
    get_total_supply as _get_total_supply,
    is_erc20 as _is_erc20,
)

logger = get_logger(__name__)


class TokenService:
    """
    Ethereum token business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Token Service.
        """

        logger.info(
            "TokenService initialized."
        )

    ###########################################################################
    # Complete Token Report
    ###########################################################################

    def get_token_report(
        self,
        address: str,
        wallet_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a complete ERC-20 token report.

        Parameters
        ----------
        address : str
            Token contract address.

        wallet_address : str | None
            Optional wallet address used to retrieve
            the holder balance.

        Returns
        -------
        dict[str, Any]
            Token report.
        """

        logger.info(
            "Generating token report for %s.",
            address,
        )

        try:

            ###################################################################
            # ERC-20 Validation
            ###################################################################

            if not _is_erc20(address):

                logger.warning(
                    "Address is not an ERC-20 token."
                )

                return {
                    "address": address,
                    "is_token": False,
                    "error": "Not an ERC-20 token",
                }

            ###################################################################
            # Token Metadata
            ###################################################################

            try:

                metadata = _get_token_metadata(
                    address,
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve token metadata."
                )

                metadata = {
                    "name": "Unknown",
                    "symbol": "Unknown",
                    "decimals": 18,
                }

            ###################################################################
            # Total Supply
            ###################################################################

            try:

                total_supply = _get_total_supply(
                    address,
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve total supply."
                )

                total_supply = None

            ###################################################################
            # Optional Wallet Balance
            ###################################################################

            balance = None

            if wallet_address is not None:

                try:

                    balance = _get_token_balance(
                        address,
                        wallet_address,
                    )

                except Exception:

                    logger.exception(
                        "Failed to retrieve token balance."
                    )

            ###################################################################
            # Token Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,
                "is_token": True,

                "name": metadata.get(
                    "name",
                    "Unknown",
                ),

                "symbol": metadata.get(
                    "symbol",
                    "Unknown",
                ),

                "decimals": metadata.get(
                    "decimals",
                    18,
                ),

                "total_supply": total_supply,

                "balance": balance,
            }

            logger.info(
                "Token report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate token report."
            )

            raise


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Token Information
    ###########################################################################

    def get_token_info(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve basic token information.

        Parameters
        ----------
        address : str
            Token contract address.

        Returns
        -------
        dict[str, Any]
            Token metadata and total supply.
        """

        logger.info(
            "Retrieving token information for %s.",
            address,
        )

        try:

            ###################################################################
            # ERC-20 Validation
            ###################################################################

            if not _is_erc20(address):

                logger.warning(
                    "Address is not an ERC-20 token."
                )

                return {
                    "address": address,
                    "is_token": False,
                    "error": "Not an ERC-20 token",
                }

            ###################################################################
            # Token Metadata
            ###################################################################

            metadata = _get_token_metadata(
                address,
            )

            ###################################################################
            # Total Supply
            ###################################################################

            total_supply = _get_total_supply(
                address,
            )

            ###################################################################
            # Token Information Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,
                "is_token": True,

                "name": metadata.get(
                    "name",
                    "Unknown",
                ),

                "symbol": metadata.get(
                    "symbol",
                    "Unknown",
                ),

                "decimals": metadata.get(
                    "decimals",
                    18,
                ),

                "total_supply": total_supply,
            }

            logger.info(
                "Token information retrieved successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to retrieve token information."
            )

            raise


###############################################################################
# End of Part 2
###############################################################################
    ###########################################################################
    # Token Balance
    ###########################################################################

    def get_token_balance(
        self,
        token_address: str,
        wallet_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve a wallet's token balance.

        Parameters
        ----------
        token_address : str
            ERC-20 contract address.

        wallet_address : str
            Wallet address.

        Returns
        -------
        dict[str, Any]
            Token balance information.
        """

        logger.info(
            "Retrieving token balance for %s.",
            wallet_address,
        )

        try:

            ###################################################################
            # ERC-20 Validation
            ###################################################################

            if not _is_erc20(token_address):

                logger.warning(
                    "Address is not an ERC-20 token: %s.",
                    token_address,
                )

                return {
                    "error": "Not an ERC-20 token",
                    "balance": 0,
                }

            ###################################################################
            # Raw Token Balance
            ###################################################################

            balance = _get_token_balance(
                token_address,
                wallet_address,
            )

            ###################################################################
            # Token Metadata
            ###################################################################

            metadata = _get_token_metadata(
                token_address,
            )

            decimals = metadata.get(
                "decimals",
                18,
            )

            ###################################################################
            # Balance Report
            ###################################################################

            report: dict[str, Any] = {
                "token_address": token_address,
                "wallet_address": wallet_address,
                "balance": balance,
                "decimals": decimals,
                "formatted_balance": (
                    balance / (10 ** decimals)
                    if balance
                    else 0
                ),
            }

            logger.info(
                "Token balance retrieved successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to retrieve token balance."
            )

            raise


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TokenService",
]


###############################################################################
# End of File
###############################################################################