"""
Universal Blockchain Platform (UBP)

Version : 1.3.0
Module  : Ethereum Contract Service
Author  : Jaramogi Diddy

Business logic for Ethereum Smart Contract
inspection and classification.
"""

from core.logger import get_logger

from constants.contract_types import (
    EOA,
    EOA_DELEGATED,
    CONTRACT,
    ERC20,
    ERC721,
    ERC1155,
)

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
)

from ethereum.contracts import (
    is_contract,
    is_erc20,
    is_erc721,
    is_erc1155,
    is_eip7702_delegated,
    get_bytecode_size,
    classify_address,
)

from ethereum.metadata import (
    get_contract_metadata,
    ContractMetadata,
)

from services.ethereum.token_service import (
    TokenService,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

logger = get_logger(__name__)


class ContractService:
    """
    Ethereum Smart Contract
    Intelligence Service.
    """

    def __init__(self):
        """
        Initialize the Contract Service.
        """

        logger.info(
            "ContractService initialized."
        )

        self.token_service = TokenService()

    def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate an Ethereum address.
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

    def _classify_contract(
        self,
        address: str,
    ) -> dict:
        """
        Classify an Ethereum address.

        Returns:
            dict:
                Classification object.
        """

        logger.info(
            "Classifying Ethereum address."
        )

        classification_type = classify_address(address)

        classification_map = {
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

        return classification_map.get(
            classification_type,
            {
                "type": CONTRACT,
                "name": "Generic Smart Contract",
                "is_contract": True,
            }
        )

    def _enrich_report(
        self,
        classification: dict,
        address: str,
    ) -> dict:
        """
        Enrich the report according
        to its classification.
        """

        logger.info(
            "Enriching contract report."
        )

        enrichment = {}

        # Get metadata for contract types
        if classification["is_contract"]:
            try:
                metadata = get_contract_metadata(
                    address,
                    classification["type"]
                )
                enrichment["metadata"] = metadata.to_dict()
            except Exception as error:
                logger.error(f"Error getting contract metadata: {error}")
                enrichment["metadata"] = {"error": str(error)}

        # Get token-specific data
        if classification["type"] == ERC20:
            logger.info("Retrieving ERC-20 token report.")
            try:
                token_report = self.token_service.get_token_report(address)
                enrichment["token"] = token_report
            except Exception as error:
                logger.error(f"Error getting token report: {error}")
                enrichment["token"] = {"error": str(error)}

        return enrichment

    def get_contract_report(
        self,
        address: str,
    ) -> dict:
        """
        Generate a complete smart
        contract report.
        """

        logger.info(
            f"Generating smart contract report for {address}"
        )

        self.validate_address(address)

        classification = self._classify_contract(address)

        enrichment = self._enrich_report(
            classification,
            address,
        )

        # Get balance and nonce
        try:
            balance = get_eth_balance(address)
        except Exception as error:
            logger.error(f"Error getting balance: {error}")
            balance = {"ether": 0, "wei": 0}

        try:
            nonce = get_nonce(address)
        except Exception as error:
            logger.error(f"Error getting nonce: {error}")
            nonce = 0

        # Get bytecode size
        if classification["is_contract"]:
            try:
                bytecode_size = get_bytecode_size(address)
            except Exception as error:
                logger.error(f"Error getting bytecode size: {error}")
                bytecode_size = 0
        else:
            bytecode_size = 0

        # Build the report
        report = {
            "address": address,
            "is_contract": classification["is_contract"],
            "classification": classification["name"],
            "contract_type": classification["type"],
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
            "nonce": nonce,
            "bytecode_size": bytecode_size,
        }

        # Add enrichment data
        report.update(enrichment)

        logger.info(
            "Smart contract report generated successfully."
        )

        return report