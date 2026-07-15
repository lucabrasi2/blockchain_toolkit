"""
Universal Blockchain Platform (UBP)

Version : 1.0.0
Module  : Ethereum Validator
Author  : Jaramogi Diddy

Centralized validation utilities for Ethereum.
"""

from web3 import Web3

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
    UBPException,
)


class EthereumValidator:
    """
    Shared Ethereum validation utilities.
    """

    @staticmethod
    def validate_wallet(address: str) -> bool:
        """
        Validate an Ethereum wallet address.

        Args:
            address: Ethereum wallet address.

        Returns:
            bool: True if valid.

        Raises:
            InvalidWalletAddressError:
                If the address is invalid.
        """

        if not address:

            raise InvalidWalletAddressError(
                "Wallet address cannot be empty."
            )

        if not Web3.is_address(address):

            raise InvalidWalletAddressError(
                "Invalid Ethereum wallet address."
            )

        return True

    @staticmethod
    def validate_transaction_hash(tx_hash: str) -> bool:
        """
        Validate an Ethereum transaction hash.

        Args:
            tx_hash: Transaction hash.

        Returns:
            bool: True if valid.

        Raises:
            UBPException:
                If the hash is invalid.
        """

        if not tx_hash:

            raise UBPException(
                "Transaction hash cannot be empty."
            )

        if not tx_hash.startswith("0x"):

            raise UBPException(
                "Transaction hash must start with '0x'."
            )

        if len(tx_hash) != 66:

            raise UBPException(
                "Invalid Ethereum transaction hash length."
            )

        return True

    @staticmethod
    def validate_block_number(block_number: int) -> bool:
        """
        Validate a block number.

        Args:
            block_number: Ethereum block number.

        Returns:
            bool: True if valid.

        Raises:
            UBPException:
                If invalid.
        """

        if block_number < 0:

            raise UBPException(
                "Block number cannot be negative."
            )

        return True

    @staticmethod
    def validate_contract(address: str) -> bool:
        """
        Validate a smart contract address.

        Currently identical to wallet validation.

        Returns:
            bool
        """

        return EthereumValidator.validate_wallet(
            address
        )