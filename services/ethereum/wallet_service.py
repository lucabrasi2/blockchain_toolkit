"""
Universal Blockchain Platform (UBP)

Version : 1.3.0
Module  : Ethereum Wallet Service
Author  : Jaramogi Diddy

Business logic for Ethereum wallet
inspection and analysis.
"""

from core.logger import get_logger

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
    get_transaction_count,
    get_token_balances,
)

from ethereum.contracts import (
    is_contract,
    classify_address,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

logger = get_logger(__name__)


class WalletService:
    """
    Ethereum Wallet Intelligence Service.
    """

    def __init__(self):
        """
        Initialize the Wallet Service.
        """

        logger.info(
            "WalletService initialized."
        )

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

    def get_wallet_report(
        self,
        address: str,
    ) -> dict:
        """
        Generate a complete wallet report.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict
            Complete wallet report.
        """

        logger.info(
            f"Generating wallet report for {address}"
        )

        # Validate the address
        self.validate_address(address)

        # Get basic wallet info
        balance = get_eth_balance(address)
        nonce = get_nonce(address)
        transaction_count = get_transaction_count(address)

        # Check if it's a contract
        is_contract_address = is_contract(address)
        
        # Classify the address
        classification = classify_address(address)

        # Get token balances (if any)
        token_balances = get_token_balances(address)

        # Build the report
        report = {
            "address": address,
            "is_contract": is_contract_address,
            "classification": classification,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
            "nonce": nonce,
            "transaction_count": transaction_count,
            "token_balances": token_balances,
        }

        logger.info(
            "Wallet report generated successfully."
        )

        return report

    def get_wallet_balance(
        self,
        address: str,
    ) -> dict:
        """
        Get wallet balance only.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict
            Balance information.
        """

        logger.info(
            f"Getting balance for {address}"
        )

        self.validate_address(address)

        balance = get_eth_balance(address)

        return {
            "address": address,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
        }

    def get_wallet_status(
        self,
        address: str,
    ) -> dict:
        """
        Get wallet status information.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        Returns
        -------
        dict
            Wallet status information.
        """

        logger.info(
            f"Getting status for {address}"
        )

        self.validate_address(address)

        balance = get_eth_balance(address)
        nonce = get_nonce(address)
        transaction_count = get_transaction_count(address)
        is_contract_address = is_contract(address)

        return {
            "address": address,
            "is_contract": is_contract_address,
            "balance_eth": balance.get("ether", 0),
            "balance_wei": balance.get("wei", 0),
            "nonce": nonce,
            "transaction_count": transaction_count,
            "has_balance": balance.get("wei", 0) > 0,
        }