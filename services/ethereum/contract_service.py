"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.contract_service

Purpose
-------
Business logic for Ethereum smart contract inspection
and classification.

Responsibilities
----------------
• Validate Ethereum addresses
• Classify smart contracts
• Retrieve contract metadata
• Enrich reports with token information
• Generate controller-friendly reports

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

from constants.contract_types import (
    CONTRACT,
    EOA,
    EOA_DELEGATED,
    ERC20,
    ERC721,
    ERC1155,
)

from ethereum.wallets import (
    get_eth_balance,
    get_nonce,
    is_valid_address,
)

from ethereum.contracts import (
    classify_address,
    get_bytecode_size,
)

from ethereum.metadata import (
    get_contract_metadata,
)

from services.ethereum.token_service import TokenService

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

logger = get_logger(__name__)


###############################################################################
# Contract Classification Map
###############################################################################

CONTRACT_CLASSIFICATION_MAP: dict[str, dict[str, Any]] = {
    EOA: {
        "type": EOA,
        "name": "Externally Owned Account",
        "is_contract": False,
    },
    EOA_DELEGATED: {
        "type": EOA_DELEGATED,
        "name": "Delegated Account (EIP-7702)",
        "is_contract": False,
    },
    ERC20: {
        "type": ERC20,
        "name": "ERC-20 Token Contract",
        "is_contract": True,
    },
    ERC721: {
        "type": ERC721,
        "name": "ERC-721 NFT Contract",
        "is_contract": True,
    },
    ERC1155: {
        "type": ERC1155,
        "name": "ERC-1155 Multi-Token Contract",
        "is_contract": True,
    },
    CONTRACT: {
        "type": CONTRACT,
        "name": "Generic Smart Contract",
        "is_contract": True,
    },
}


###############################################################################
# Contract Service
###############################################################################


class ContractService:
    """
    Ethereum Smart Contract Intelligence Service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Contract Service.
        """

        self.token_service = TokenService()

        logger.info(
            "ContractService initialized."
        )

    ###########################################################################
    # Address Validation
    ###########################################################################

    def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate an Ethereum address.

        Parameters
        ----------
        address : str
            Ethereum address.

        Returns
        -------
        bool
            True if the address is valid.

        Raises
        ------
        InvalidWalletAddressError
            If the address is invalid.
        """

        logger.info(
            "Validating Ethereum address."
        )

        if not is_valid_address(address):

            logger.warning(
                "Invalid Ethereum address."
            )

            raise InvalidWalletAddressError(
                "Invalid Ethereum address."
            )

        logger.info(
            "Ethereum address validation successful."
        )

        return True

    ###########################################################################
    # Contract Classification
    ###########################################################################

    def _classify_contract(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Classify an Ethereum address.

        Parameters
        ----------
        address : str
            Ethereum address.

        Returns
        -------
        dict[str, Any]
            Classification information.
        """

        logger.info(
            "Classifying Ethereum address."
        )

        classification = classify_address(
            address
        )

        return CONTRACT_CLASSIFICATION_MAP.get(
            classification,
            CONTRACT_CLASSIFICATION_MAP[CONTRACT],
        )


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Report Enrichment
    ###########################################################################

    def _enrich_report(
        self,
        classification: dict[str, Any],
        address: str,
    ) -> dict[str, Any]:
        """
        Enrich the contract report with metadata
        and token information.

        Parameters
        ----------
        classification : dict[str, Any]
            Address classification result.

        address : str
            Ethereum contract address.

        Returns
        -------
        dict[str, Any]
            Enrichment data.
        """

        logger.info(
            "Enriching contract report."
        )

        enrichment: dict[str, Any] = {}

        #######################################################################
        # Contract Metadata
        #######################################################################

        if classification["is_contract"]:

            try:

                metadata = get_contract_metadata(
                    address,
                    classification["type"],
                )

                enrichment["metadata"] = (
                    metadata.to_dict()
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve contract metadata "
                    "for %s.",
                    address,
                )

                enrichment["metadata"] = {
                    "error": (
                        "Unable to retrieve metadata."
                    ),
                }

        #######################################################################
        # ERC-20 Token Information
        #######################################################################

        if classification["type"] == ERC20:

            logger.info(
                "Retrieving ERC-20 token report."
            )

            try:

                enrichment["token"] = (
                    self.token_service.get_token_report(
                        address,
                    )
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve ERC-20 token "
                    "report for %s.",
                    address,
                )

                enrichment["token"] = {
                    "error": (
                        "Unable to retrieve token report."
                    ),
                }

        return enrichment


###############################################################################
# End of Part 2
###############################################################################
    ###########################################################################
    # Contract Report
    ###########################################################################

    def get_contract_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete smart contract report.

        Parameters
        ----------
        address : str
            Ethereum address.

        Returns
        -------
        dict[str, Any]
            Smart contract report.
        """

        logger.info(
            "Generating smart contract report for %s",
            address,
        )

        try:

            ###################################################################
            # Validate Address
            ###################################################################

            self.validate_address(
                address,
            )

            ###################################################################
            # Classification
            ###################################################################

            classification = (
                self._classify_contract(
                    address,
                )
            )

            ###################################################################
            # Metadata and Token Enrichment
            ###################################################################

            enrichment = (
                self._enrich_report(
                    classification,
                    address,
                )
            )

            ###################################################################
            # ETH Balance
            ###################################################################

            try:

                balance = get_eth_balance(
                    address,
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve wallet balance "
                    "for %s.",
                    address,
                )

                balance = {
                    "ether": 0,
                    "wei": 0,
                }

            ###################################################################
            # Nonce
            ###################################################################

            try:

                nonce = get_nonce(
                    address,
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve nonce "
                    "for %s.",
                    address,
                )

                nonce = 0

            ###################################################################
            # Bytecode Size
            ###################################################################

            if classification["is_contract"]:

                try:

                    bytecode_size = (
                        get_bytecode_size(
                            address,
                        )
                    )

                except Exception:

                    logger.exception(
                        "Failed to retrieve bytecode size "
                        "for %s.",
                        address,
                    )

                    bytecode_size = 0

            else:

                bytecode_size = 0

            ###################################################################
            # Base Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,

                "is_contract": (
                    classification["is_contract"]
                ),

                "classification": (
                    classification["name"]
                ),

                "contract_type": (
                    classification["type"]
                ),

                "balance_eth": balance.get(
                    "ether",
                    0,
                ),

                "balance_wei": balance.get(
                    "wei",
                    0,
                ),

                "nonce": nonce,

                "bytecode_size": bytecode_size,
            }

            ###################################################################
            # Enrichment
            ###################################################################

            report.update(
                enrichment,
            )

            logger.info(
                "Smart contract report generated "
                "successfully for %s.",
                address,
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate smart contract "
                "report for %s.",
                address,
            )

            raise


###############################################################################
# End of File
###############################################################################