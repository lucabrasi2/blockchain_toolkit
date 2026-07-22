"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.validators

Purpose
-------
Enterprise wallet validation services.

This module provides blockchain-agnostic validation for wallet entities
within the Universal Blockchain Platform (UBP).

The validator is responsible for ensuring wallet objects and their
associated data are structurally correct before they are persisted,
encrypted, signed, or transmitted.

Responsibilities
----------------
- Validate wallet identifiers
- Validate wallet addresses
- Validate blockchain network names
- Validate public keys
- Validate private keys
- Validate metadata
- Validate Wallet objects
- Validate serialized wallet dictionaries

The validator intentionally does NOT perform blockchain-specific checks
such as:

- Ethereum checksum validation
- Bitcoin Base58 decoding
- TRON address conversion
- Solana ed25519 verification

Those responsibilities belong to blockchain-specific providers.

Architecture
------------

Wallet
    │
    └── WalletValidator
            │
            ├── Wallet Validation
            ├── Address Validation
            ├── Key Validation
            ├── Metadata Validation
            └── Serialization Validation

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations


import re


from typing import Any
from typing import Dict


from wallets.exceptions import (
    WalletAddressError,
    WalletPrivateKeyError,
    WalletPublicKeyError,
    WalletValidationError,
)


from wallets.wallet import Wallet


###############################################################################
# Wallet Validator
###############################################################################


class WalletValidator:
    """
    Enterprise validator for wallet objects.

    This validator performs generic structural validation while remaining
    independent of blockchain-specific implementations.
    """


    VALID_IDENTIFIER = re.compile(
        r"^[A-Za-z0-9_.-]{1,128}$"
    )


    VALID_NETWORK = re.compile(
        r"^[A-Za-z0-9_-]{2,64}$"
    )


    #
    # Generic wallet address structure validation.
    #
    # Blockchain-specific validation is intentionally delegated
    # to provider implementations.
    #
    VALID_ADDRESS = re.compile(
        r"^[A-Za-z0-9xX_:\-]{3,256}$"
    )


    def __init__(
        self,
    ) -> None:
        """
        Initialize wallet validator.
        """

        pass


    ###########################################################################
    # Wallet Validation
    ###########################################################################


    def validate_wallet(
        self,
        wallet: Wallet,
    ) -> bool:
        """
        Validate a Wallet instance.

        Parameters
        ----------
        wallet:
            Wallet object.

        Returns
        -------
        bool
            True if validation succeeds.

        Raises
        ------
        WalletValidationError
            If validation fails.
        """


        if not isinstance(
            wallet,
            Wallet,
        ):

            raise WalletValidationError(
                "Expected Wallet instance."
            )


        self.validate_wallet_id(
            wallet.wallet_id
        )


        self.validate_address(
            wallet.address
        )


        self.validate_network(
            wallet.network
        )


        self.validate_metadata(
            wallet.metadata
        )


        return True



    def validate_wallet_id(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Validate wallet identifier.
        """


        if not wallet_id:

            raise WalletValidationError(
                "Wallet ID cannot be empty."
            )


        if not self.VALID_IDENTIFIER.fullmatch(
            wallet_id
        ):

            raise WalletValidationError(
                "Invalid wallet ID."
            )


        return True


    def validate_network(
        self,
        network: str,
    ) -> bool:
        """
        Validate blockchain network name.

        Parameters
        ----------
        network:
            Blockchain network identifier.

        Returns
        -------
        bool
            True if valid.
        """


        if not network:

            raise WalletValidationError(
                "Network cannot be empty."
            )


        if not isinstance(
            network,
            str,
        ):

            raise WalletValidationError(
                "Network must be a string."
            )


        network = network.strip()


        if not self.VALID_NETWORK.fullmatch(
            network
        ):

            raise WalletValidationError(
                "Invalid blockchain network."
            )


        return True



    ###########################################################################
    # Address Validation
    ###########################################################################


    def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate wallet address.

        This performs generic structural validation only.

        Blockchain-specific validation such as:

        - Ethereum checksum validation
        - Bitcoin Base58 validation
        - TRON Base58Check validation
        - Solana address validation

        is delegated to provider implementations.

        Parameters
        ----------
        address:
            Wallet address.

        Returns
        -------
        bool
            True if valid.

        Raises
        ------
        WalletAddressError
            If the address is invalid.
        """


        if not isinstance(
            address,
            str,
        ):

            raise WalletAddressError(
                "Wallet address must be a string."
            )


        address = address.strip()


        if not address:

            raise WalletAddressError(
                "Wallet address cannot be empty."
            )


        if not self.VALID_ADDRESS.fullmatch(
            address
        ):

            raise WalletAddressError(
                "Invalid wallet address format."
            )


        return True



    ###########################################################################
    # Key Validation
    ###########################################################################


    def validate_public_key(
        self,
        public_key: str,
    ) -> bool:
        """
        Validate public key structure.

        Performs generic structural validation only.

        Parameters
        ----------
        public_key:
            Public key.

        Returns
        -------
        bool
            True if valid.
        """


        if not public_key:

            raise WalletPublicKeyError(
                "Public key cannot be empty."
            )


        if not isinstance(
            public_key,
            str,
        ):

            raise WalletPublicKeyError(
                "Public key must be a string."
            )


        public_key = public_key.strip()


        if len(public_key) < 32:

            raise WalletPublicKeyError(
                "Public key is too short."
            )


        return True



    def validate_private_key(
        self,
        private_key: str,
    ) -> bool:
        """
        Validate private key structure.

        Performs generic structural validation only.

        Parameters
        ----------
        private_key:
            Private key.

        Returns
        -------
        bool
            True if valid.
        """


        if not private_key:

            raise WalletPrivateKeyError(
                "Private key cannot be empty."
            )


        if not isinstance(
            private_key,
            str,
        ):

            raise WalletPrivateKeyError(
                "Private key must be a string."
            )


        private_key = private_key.strip()


        if len(private_key) < 32:

            raise WalletPrivateKeyError(
                "Private key is too short."
            )


        return True
        ###########################################################################
    # Metadata Validation
    ###########################################################################


    def validate_metadata(
        self,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Validate wallet metadata.

        Parameters
        ----------
        metadata:
            Wallet metadata dictionary.

        Returns
        -------
        bool
            True if valid.
        """


        if metadata is None:

            return True


        if not isinstance(
            metadata,
            dict,
        ):

            raise WalletValidationError(
                "Metadata must be a dictionary."
            )


        for key in metadata.keys():

            if not isinstance(
                key,
                str,
            ):

                raise WalletValidationError(
                    "Metadata keys must be strings."
                )


        return True



    ###########################################################################
    # Serialized Wallet Validation
    ###########################################################################


    def validate_serialized(
        self,
        data: Dict[str, Any],
    ) -> bool:
        """
        Validate a serialized wallet dictionary.

        Parameters
        ----------
        data:
            Serialized wallet data.

        Returns
        -------
        bool
            True if valid.
        """


        if not isinstance(
            data,
            dict,
        ):

            raise WalletValidationError(
                "Serialized wallet must be a dictionary."
            )


        required_fields = (
            "wallet_id",
            "address",
            "network",
        )


        for field in required_fields:

            if field not in data:

                raise WalletValidationError(
                    f"Missing required field: {field}"
                )


        self.validate_wallet_id(
            data["wallet_id"]
        )


        self.validate_address(
            data["address"]
        )


        self.validate_network(
            data["network"]
        )


        self.validate_metadata(
            data.get(
                "metadata",
                {},
            )
        )


        return True



    ###########################################################################
    # Convenience Validation
    ###########################################################################


    def is_valid(
        self,
        wallet: Wallet,
    ) -> bool:
        """
        Determine whether a wallet is valid.

        Unlike validate_wallet(), this method returns False instead of
        propagating validation exceptions.

        Parameters
        ----------
        wallet:
            Wallet instance.

        Returns
        -------
        bool
            True if valid, otherwise False.
        """


        try:

            return self.validate_wallet(
                wallet
            )


        except (
            WalletValidationError,
            WalletAddressError,
            WalletPublicKeyError,
            WalletPrivateKeyError,
        ):

            return False



    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return validator information.

        Returns
        -------
        dict
            Validator metadata.
        """


        return {

            "service":
                "Wallet Validator",

            "version":
                "2.0 Enterprise",

            "validation_scope":
                (
                    "Generic wallet validation "
                    "(blockchain agnostic)"
                ),
        }



    ###########################################################################
    # Representation
    ###########################################################################


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """


        return (
            f"{self.__class__.__name__}()"
        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """


        return (
            "Wallet Validator"
        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [
    "WalletValidator",
]


###############################################################################
# End of wallets.validators
###############################################################################