"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.asset_service

Purpose
-------
Universal asset and token business logic service.

Responsibilities
----------------
- Identify native blockchain assets
- Identify supported token standards
- Retrieve native asset information
- Retrieve ERC-20 token information
- Retrieve TRC-20 token information
- Retrieve token balances
- Provide a stable UBP-level asset interface
- Support future token-standard extensions

Architectural Intent
--------------------
This service provides a blockchain-agnostic asset interface.

Blockchain-specific logic remains inside the existing blockchain modules.
This service coordinates those modules and normalizes their responses.

Supported Native Assets
-----------------------
- ETH
- BTC
- TRX

Supported Token Standards
-------------------------
- ERC20
- TRC20

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
    NATIVE,
    TOKEN,
    get_native_asset,
    is_native_asset,
    is_token_standard,
    SUPPORTED_NATIVE_ASSETS,
    SUPPORTED_TOKEN_STANDARDS,
)

from ethereum.tokens import (
    get_token_info as get_erc20_token_info,
    get_token_balance as get_erc20_token_balance,
)

from services.tron.token_service import (
    TronTokenService,
)

from bitcoin.tokens import (
    get_token_metadata as get_bitcoin_token_metadata,
    get_token_balance as get_bitcoin_token_balance,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Universal Asset Service
###############################################################################


class AssetService:
    """
    Universal UBP asset and token business logic service.

    This service does not directly implement blockchain protocol logic.

    Instead, it routes requests to the appropriate blockchain-specific
    implementation.

    This allows higher application layers to work with a stable asset
    interface without needing to know whether an asset is:

        - a native blockchain asset
        - an ERC-20 token
        - a TRC-20 token
        - a future token standard
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Universal Asset Service.
        """

        self.tron_token_service = TronTokenService()

        logger.info(
            "AssetService initialized."
        )

    ###########################################################################
    # Validation helpers
    ###########################################################################

    @staticmethod
    def _normalize_text(value: Any, field: str) -> str:
        """Normalize a required text input and reject empty values."""
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string.")
        value = value.strip()
        if not value:
            raise ValueError(f"{field} cannot be empty.")
        return value

    @classmethod
    def _normalize_standard(cls, standard: Any) -> str:
        """Normalize and validate a supported token standard."""
        value = cls._normalize_text(standard, "Token standard").upper()
        if not cls.is_token(value):
            raise ValueError(f"Unsupported token standard: {value}")
        return value

    @staticmethod
    def _validate_address(value: Any, field: str) -> str:
        """Perform safe structural validation without implementing chain rules."""
        address = AssetService._normalize_text(value, field)
        if len(address) > 255:
            raise ValueError(f"{field} is too long.")
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in address):
            raise ValueError(f"{field} contains invalid control characters.")
        return address

    @staticmethod
    def _safe_error_result(base: dict[str, Any], message: str) -> dict[str, Any]:
        """Return a stable client-safe error without exposing provider internals."""
        result = dict(base)
        result["error"] = message
        return result

    ###########################################################################
    # Native Asset
    ###########################################################################

    @staticmethod
    def get_native_asset(
        blockchain: str,
    ) -> str:
        """
        Return the canonical native asset for a blockchain.
        """

        return get_native_asset(
            blockchain,
        )

    ###########################################################################
    # Asset Classification
    ###########################################################################

    @staticmethod
    def is_native(
        asset: str,
    ) -> bool:
        """
        Determine whether an asset is a supported native asset.
        """

        return is_native_asset(
            asset,
        )

    ###########################################################################

    @staticmethod
    def is_token(
        standard: str,
    ) -> bool:
        """
        Determine whether a value represents a supported token standard.
        """

        return is_token_standard(
            standard,
        )

    ###########################################################################
    # Asset Identification
    ###########################################################################

    @classmethod
    def identify_asset(
        cls,
        blockchain: str,
        asset: str | None = None,
        standard: str | None = None,
    ) -> dict[str, Any]:
        """
        Identify and normalize an asset.

        Native asset example:

            identify_asset("ethereum")

        Token standard example:

            identify_asset(
                "ethereum",
                standard="ERC20",
            )
        """

        normalized_blockchain = cls._normalize_text(
            blockchain, "Blockchain"
        ).lower()

        #######################################################################
        # Token Standard
        #######################################################################

        if standard is not None:

            normalized_standard = cls._normalize_standard(standard)

            standard_blockchain = {
                ERC20: ETHEREUM,
                TRC20: TRON,
            }.get(
                normalized_standard,
            )

            if (
                standard_blockchain
                != normalized_blockchain
            ):
                raise ValueError(
                    f"Token standard "
                    f"{normalized_standard} "
                    f"is not supported on "
                    f"{normalized_blockchain}."
                )

            return {
                "blockchain": normalized_blockchain,
                "asset_type": TOKEN,
                "asset": None,
                "standard": normalized_standard,
            }

        #######################################################################
        # Native Asset
        #######################################################################

        native_asset = cls.get_native_asset(
            normalized_blockchain,
        )

        if asset is not None:

            if not isinstance(
                asset,
                str,
            ):
                raise ValueError(
                    "Asset must be a string."
                )

            normalized_asset = (
                asset.strip().upper()
            )

            if normalized_asset != native_asset:
                raise ValueError(
                    f"Asset {normalized_asset} "
                    f"is not the native asset of "
                    f"{normalized_blockchain}."
                )

        return {
            "blockchain": normalized_blockchain,
            "asset_type": NATIVE,
            "asset": native_asset,
            "standard": None,
        }

    ###########################################################################
    # Supported Assets
    ###########################################################################

    @staticmethod
    def get_supported_native_assets() -> list[str]:
        """
        Return all supported native assets.
        """

        return sorted(
            SUPPORTED_NATIVE_ASSETS
        )

    ###########################################################################

    @staticmethod
    def get_supported_token_standards() -> list[str]:
        """
        Return all supported token standards.
        """

        return sorted(
            SUPPORTED_TOKEN_STANDARDS
        )

    ###########################################################################
    # ERC-20 Information
    ###########################################################################

    def get_erc20_info(
        self,
        token_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve normalized ERC-20 token information.
        """

        logger.info(
            "Retrieving ERC-20 asset information: %s",
            token_address,
        )

        try:
            token_address = self._validate_address(token_address, "Token address")
        except ValueError as error:
            return {
                "error": str(error),
                "standard": ERC20,
                "blockchain": ETHEREUM,
            }

        try:

            info = get_erc20_token_info(
                token_address,
            )

            if not isinstance(
                info,
                dict,
            ):
                info = {}

            return {
                "blockchain": ETHEREUM,
                "asset_type": TOKEN,
                "standard": ERC20,
                "address": token_address,
                "name": info.get(
                    "name",
                    "Unknown",
                ),
                "symbol": info.get(
                    "symbol",
                    "Unknown",
                ),
                "decimals": info.get(
                    "decimals",
                    18,
                ),
                "total_supply": info.get(
                    "total_supply",
                ),
                "is_token": True,
            }

        except Exception as error:

            logger.exception(
                "Failed to retrieve ERC-20 information."
            )

            return {
                "blockchain": ETHEREUM,
                "asset_type": TOKEN,
                "standard": ERC20,
                "address": token_address,
                "is_token": False,
                "error": "Unable to retrieve ERC-20 token information.",
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
        Retrieve and normalize an ERC-20 token balance.
        """

        logger.info(
            "Retrieving ERC-20 balance for wallet: %s",
            wallet_address,
        )

        try:

            balance = get_erc20_token_balance(
                token_address,
                wallet_address,
            )

            return {
                "blockchain": ETHEREUM,
                "asset_type": TOKEN,
                "standard": ERC20,
                "token_address": token_address,
                "wallet_address": wallet_address,
                "balance": balance,
            }

        except Exception as error:

            logger.exception(
                "Failed to retrieve ERC-20 balance."
            )

            return {
                "blockchain": ETHEREUM,
                "asset_type": TOKEN,
                "standard": ERC20,
                "token_address": token_address,
                "wallet_address": wallet_address,
                "balance": None,
                "error": "Unable to retrieve ERC-20 token balance.",
            }

    ###########################################################################
    # TRC-20 Information
    ###########################################################################

    def get_trc20_info(
        self,
        token_address: str,
        wallet_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve normalized TRC-20 token information.
        """

        logger.info(
            "Retrieving TRC-20 asset information: %s",
            token_address,
        )

        try:
            token_address = self._validate_address(token_address, "Token address")
            if wallet_address is not None:
                wallet_address = self._validate_address(wallet_address, "Wallet address")
        except ValueError as error:
            return {
                "error": str(error),
                "standard": TRC20,
                "blockchain": TRON,
            }

        try:

            report = (
                self.tron_token_service.get_token_report(
                    token_address,
                    wallet_address,
                )
            )

            if not isinstance(
                report,
                dict,
            ):
                report = {}

            report.setdefault(
                "blockchain",
                TRON,
            )

            report.setdefault(
                "asset_type",
                TOKEN,
            )

            report.setdefault(
                "standard",
                TRC20,
            )

            return report

        except Exception as error:

            logger.exception(
                "Failed to retrieve TRC-20 information."
            )

            return {
                "blockchain": TRON,
                "asset_type": TOKEN,
                "standard": TRC20,
                "address": token_address,
                "is_token": False,
                "error": "Unable to retrieve TRC-20 token information.",
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
        Retrieve and normalize a TRC-20 token balance.

        The existing TRON token service already performs the blockchain
        specific balance lookup, so this method uses the same service
        interface instead of duplicating TRON contract logic.
        """

        logger.info(
            "Retrieving TRC-20 balance for wallet: %s",
            wallet_address,
        )

        try:

            report = (
                self.tron_token_service.get_token_report(
                    token_address,
                    wallet_address,
                )
            )

            return {
                "blockchain": TRON,
                "asset_type": TOKEN,
                "standard": TRC20,
                "token_address": token_address,
                "wallet_address": wallet_address,
                "balance": report.get(
                    "balance"
                ),
                "symbol": report.get(
                    "symbol"
                ),
                "decimals": report.get(
                    "decimals",
                    6,
                ),
            }

        except Exception as error:

            logger.exception(
                "Failed to retrieve TRC-20 balance."
            )

            return {
                "blockchain": TRON,
                "asset_type": TOKEN,
                "standard": TRC20,
                "token_address": token_address,
                "wallet_address": wallet_address,
                "balance": None,
                "error": "Unable to retrieve TRC-20 token balance.",
            }

    ###########################################################################
    # Universal Token Information
    ###########################################################################

    def get_token_info(
        self,
        standard: str,
        token_address: str,
        wallet_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve token information using a universal interface.

        Parameters
        ----------
        standard:
            Token standard, such as ERC20 or TRC20.

        token_address:
            Token contract address.

        wallet_address:
            Optional wallet address for balance lookup.

        Returns
        -------
        dict[str, Any]
            Normalized token information.
        """

        try:
            normalized_standard = self._normalize_standard(standard)
        except ValueError as error:
            return {"error": str(error)}

        #######################################################################
        # ERC-20
        #######################################################################

        if normalized_standard == ERC20:

            result = self.get_erc20_info(
                token_address,
            )

            if wallet_address:
                balance = self.get_erc20_balance(
                    token_address,
                    wallet_address,
                )

                result["balance"] = balance.get(
                    "balance"
                )

                result["wallet_address"] = (
                    wallet_address
                )

            return result

        #######################################################################
        # TRC-20
        #######################################################################

        if normalized_standard == TRC20:

            return self.get_trc20_info(
                token_address,
                wallet_address,
            )

        #######################################################################
        # Unsupported Standard
        #######################################################################

        return {
            "token_address": token_address,
            "standard": normalized_standard,
            "is_token": False,
            "error": (
                f"Unsupported token standard: "
                f"{normalized_standard}"
            ),
        }

    ###########################################################################
    # Universal Token Balance
    ###########################################################################

    def get_token_balance(
        self,
        standard: str,
        token_address: str,
        wallet_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve a token balance using the universal token interface.

        Parameters
        ----------
        standard:
            Token standard.

        token_address:
            Token contract address.

        wallet_address:
            Wallet address.

        Returns
        -------
        dict[str, Any]
            Normalized token balance.
        """

        try:
            normalized_standard = self._normalize_standard(standard)
        except ValueError as error:
            return {"error": str(error)}

        #######################################################################
        # ERC-20
        #######################################################################

        if normalized_standard == ERC20:

            return self.get_erc20_balance(
                token_address,
                wallet_address,
            )

        #######################################################################
        # TRC-20
        #######################################################################

        if normalized_standard == TRC20:

            return self.get_trc20_balance(
                token_address,
                wallet_address,
            )

        #######################################################################
        # Unsupported Standard
        #######################################################################

        return {
            "token_address": token_address,
            "wallet_address": wallet_address,
            "standard": normalized_standard,
            "balance": None,
            "error": (
                f"Unsupported token standard: "
                f"{normalized_standard}"
            ),
        }

    ###########################################################################
    # Bitcoin Native Asset
    ###########################################################################

    @staticmethod
    def get_bitcoin_asset_info(
        address: str | None = None,
    ) -> dict[str, Any]:
        """
        Return Bitcoin native asset information.

        Bitcoin is represented as a native asset rather than a token
        standard in UBP.
        """

        result: dict[str, Any] = {
            "blockchain": BITCOIN,
            "asset_type": NATIVE,
            "asset": BTC,
            "symbol": BTC,
            "standard": None,
            "is_token": False,
        }

        if address is not None:
            try:
                address = AssetService._validate_address(address, "Bitcoin address")
            except ValueError as error:
                return AssetService._safe_error_result(result, str(error))

            result["address"] = address

            metadata = (
                get_bitcoin_token_metadata(
                    address,
                )
            )

            if isinstance(
                metadata,
                dict,
            ):
                result.update(
                    metadata
                )

            result["blockchain"] = BITCOIN
            result["asset_type"] = NATIVE
            result["asset"] = BTC
            result["symbol"] = BTC
            result["standard"] = None
            result["is_token"] = False

        return result

    ###########################################################################
    # Bitcoin Balance
    ###########################################################################

    @staticmethod
    def get_bitcoin_balance(
        wallet_address: str,
    ) -> dict[str, Any]:
        """
        Retrieve Bitcoin native asset balance.

        Note
        ----
        The current bitcoin.tokens implementation is intentionally a
        structural placeholder. Therefore this method preserves the current
        underlying behavior and does not invent a BTC balance.
        """

        try:
            wallet_address = AssetService._validate_address(wallet_address, "Bitcoin wallet address")
            balance = get_bitcoin_token_balance(
                BTC,
                wallet_address,
            )

            return {
                "blockchain": BITCOIN,
                "asset_type": NATIVE,
                "asset": BTC,
                "symbol": BTC,
                "standard": None,
                "wallet_address": wallet_address,
                "balance": balance,
                "is_token": False,
            }

        except Exception as error:

            logger.exception(
                "Failed to retrieve Bitcoin balance."
            )

            return {
                "blockchain": BITCOIN,
                "asset_type": NATIVE,
                "asset": BTC,
                "symbol": BTC,
                "standard": None,
                "wallet_address": wallet_address,
                "balance": None,
                "is_token": False,
                "error": "Unable to retrieve Bitcoin balance.",
            }


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "AssetService",
]


###############################################################################
# End of File
###############################################################################