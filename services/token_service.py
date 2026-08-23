"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.token_service

Purpose
-------
Cross-chain asset and token service for UBP.

Responsibilities
----------------
- Resolve native blockchain assets
- Resolve supported token standards
- Provide normalized asset information
- Delegate blockchain-specific token operations
- Provide an extensible architecture for future token standards

Supported Native Assets
-----------------------
- ETH
- BTC
- TRX

Supported Token Standards
-------------------------
- ERC20
- TRC20

Architectural Intent
--------------------
This service provides a stable cross-chain interface while keeping
blockchain-specific implementation inside the corresponding blockchain
modules.

Future token standards can be added without changing the public interface
of this service.

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

from constants.asset_types import (
    ETH,
    BTC,
    TRX,
    ERC20,
    TRC20,
    ETHEREUM,
    BITCOIN,
    TRON,
    TOKEN,
    NATIVE,
    get_native_asset,
    is_native_asset,
    is_token_standard,
)

from ethereum.tokens import (
    get_token_metadata as get_erc20_metadata,
    get_token_balance as get_erc20_balance,
    get_total_supply as get_erc20_total_supply,
)

from tron.contracts import (
    get_trc20_metadata,
    get_trc20_balance,
)

from bitcoin.tokens import (
    get_token_metadata as get_bitcoin_token_metadata,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Token Service
###############################################################################


class TokenService:
    """
    Cross-chain asset and token service.

    This service provides a normalized interface for native assets and
    supported token standards.

    Blockchain-specific operations remain delegated to the corresponding
    blockchain modules.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """Initialize the cross-chain token service."""

        logger.info(
            "TokenService initialized."
        )

    ###########################################################################
    # Native Asset
    ###########################################################################

    @staticmethod
    def get_native_asset(
        blockchain: str,
    ) -> str:
        """
        Return the canonical native asset for a blockchain.

        Parameters
        ----------
        blockchain:
            Blockchain identifier.

        Returns
        -------
        str
            Native asset symbol.

        Raises
        ------
        ValueError
            If the blockchain is unsupported.
        """

        return get_native_asset(
            blockchain
        )

    ###########################################################################
    # Asset Classification
    ###########################################################################

    @staticmethod
    def is_native_asset(
        asset: str,
    ) -> bool:
        """
        Determine whether an asset is a supported native asset.
        """

        return is_native_asset(
            asset
        )

    ###########################################################################

    @staticmethod
    def is_token_standard(
        standard: str,
    ) -> bool:
        """
        Determine whether a token standard is supported.
        """

        return is_token_standard(
            standard
        )

    ###########################################################################
    # ERC-20 Metadata
    ###########################################################################

    def get_erc20_metadata(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve ERC-20 token metadata.

        Parameters
        ----------
        address:
            ERC-20 contract address.

        Returns
        -------
        dict[str, Any]
            Normalized ERC-20 metadata.
        """

        logger.info(
            "Retrieving ERC-20 metadata for: %s",
            address,
        )

        metadata = get_erc20_metadata(
            address
        )

        return {
            "address": address,
            "blockchain": ETHEREUM,
            "asset_type": TOKEN,
            "standard": ERC20,
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
        }

    ###########################################################################
    # ERC-20 Balance
    ###########################################################################

    def get_erc20_balance(
        self,
        token_address: str,
        wallet_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve an ERC-20 wallet balance.

        The returned balance remains in the token's smallest unit.
        """

        logger.info(
            "Retrieving ERC-20 balance for token %s and wallet %s",
            token_address,
            wallet_address,
        )

        metadata = self.get_erc20_metadata(
            token_address
        )

        balance = get_erc20_balance(
            token_address,
            wallet_address,
        )

        return {
            "address": token_address,
            "wallet_address": wallet_address,
            "blockchain": ETHEREUM,
            "asset_type": TOKEN,
            "standard": ERC20,
            "asset": metadata.get(
                "symbol",
                "Unknown",
            ),
            "decimals": metadata.get(
                "decimals",
                18,
            ),
            "balance": balance,
        }

    ###########################################################################
    # ERC-20 Total Supply
    ###########################################################################

    def get_erc20_total_supply(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve ERC-20 total supply.
        """

        logger.info(
            "Retrieving ERC-20 total supply for: %s",
            address,
        )

        metadata = self.get_erc20_metadata(
            address
        )

        total_supply = get_erc20_total_supply(
            address
        )

        return {
            "address": address,
            "blockchain": ETHEREUM,
            "asset_type": TOKEN,
            "standard": ERC20,
            "asset": metadata.get(
                "symbol",
                "Unknown",
            ),
            "decimals": metadata.get(
                "decimals",
                18,
            ),
            "total_supply": total_supply,
        }

    ###########################################################################
    # TRC-20 Metadata
    ###########################################################################

    def get_trc20_metadata(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve TRC-20 token metadata.
        """

        logger.info(
            "Retrieving TRC-20 metadata for: %s",
            address,
        )

        metadata = get_trc20_metadata(
            address
        )

        return {
            "address": address,
            "blockchain": TRON,
            "asset_type": TOKEN,
            "standard": TRC20,
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
                6,
            ),
            "total_supply": metadata.get(
                "total_supply",
                0,
            ),
        }

    ###########################################################################
    # TRC-20 Balance
    ###########################################################################

    def get_trc20_balance(
        self,
        token_address: str,
        wallet_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve a TRC-20 wallet balance.
        """

        logger.info(
            "Retrieving TRC-20 balance for token %s and wallet %s",
            token_address,
            wallet_address,
        )

        metadata = self.get_trc20_metadata(
            token_address
        )

        balance = get_trc20_balance(
            token_address,
            wallet_address,
        )

        return {
            "address": token_address,
            "wallet_address": wallet_address,
            "blockchain": TRON,
            "asset_type": TOKEN,
            "standard": TRC20,
            "asset": metadata.get(
                "symbol",
                "Unknown",
            ),
            "decimals": metadata.get(
                "decimals",
                6,
            ),
            "balance": balance,
        }

    ###########################################################################
    # Native Asset Information
    ###########################################################################

    def get_native_asset_info(
        self,
        blockchain: str,
    ) -> dict[str, Any]:
        """
        Return normalized information about a native blockchain asset.
        """

        blockchain = blockchain.strip().lower()

        asset = self.get_native_asset(
            blockchain
        )

        return {
            "asset": asset,
            "blockchain": blockchain,
            "asset_type": NATIVE,
            "standard": None,
            "is_native": True,
            "is_token": False,
        }

    ###########################################################################
    # Generic Asset Resolver
    ###########################################################################

    def resolve_asset(
        self,
        blockchain: str,
        standard: str | None = None,
        address: str | None = None,
    ) -> dict[str, Any]:
        """
        Resolve a blockchain asset into a normalized representation.

        Parameters
        ----------
        blockchain:
            Blockchain identifier.

        standard:
            Token standard such as ERC20 or TRC20.
            Leave as None for native assets.

        address:
            Token contract address when resolving a token.

        Returns
        -------
        dict[str, Any]
            Normalized asset information.

        Raises
        ------
        ValueError
            If the blockchain or token standard is unsupported.
        """

        blockchain = blockchain.strip().lower()

        #######################################################################
        # Native asset
        #######################################################################

        if standard is None:

            asset = self.get_native_asset(
                blockchain
            )

            return {
                "asset": asset,
                "blockchain": blockchain,
                "asset_type": NATIVE,
                "standard": None,
                "address": None,
                "is_native": True,
                "is_token": False,
            }

        #######################################################################
        # Token standard validation
        #######################################################################

        standard = standard.strip().upper()

        if not self.is_token_standard(
            standard
        ):
            raise ValueError(
                f"Unsupported token standard: {standard}"
            )

        #######################################################################
        # ERC-20
        #######################################################################

        if standard == ERC20:

            if blockchain != ETHEREUM:
                raise ValueError(
                    "ERC20 is supported only on Ethereum."
                )

            if not address:
                raise ValueError(
                    "Token contract address is required for ERC20."
                )

            return self.get_erc20_metadata(
                address
            )

        #######################################################################
        # TRC-20
        #######################################################################

        if standard == TRC20:

            if blockchain != TRON:
                raise ValueError(
                    "TRC20 is supported only on TRON."
                )

            if not address:
                raise ValueError(
                    "Token contract address is required for TRC20."
                )

            return self.get_trc20_metadata(
                address
            )

        #######################################################################
        # Future extension guard
        #######################################################################

        raise ValueError(
            f"Token standard is registered but not implemented: {standard}"
        )

    ###########################################################################
    # Supported Assets
    ###########################################################################

    @staticmethod
    def get_supported_assets() -> dict[str, Any]:
        """
        Return the currently supported UBP asset architecture.
        """

        return {
            "native_assets": {
                ETHEREUM: ETH,
                BITCOIN: BTC,
                TRON: TRX,
            },

            "token_standards": {
                ERC20: ETHEREUM,
                TRC20: TRON,
            },
        }


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TokenService",
]


###############################################################################
# End of File
###############################################################################
