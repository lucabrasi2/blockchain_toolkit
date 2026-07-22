"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.keys

Purpose
-------
Enterprise cryptographic key management abstraction.

This module defines the WalletKey entity used by wallets within UBP.

Responsibilities
----------------
- Represent cryptographic key identity
- Manage public/private key references
- Protect private key access
- Provide safe key metadata handling


Architecture
------------

Wallet
 |
 └── WalletKey
        |
        ├── Public Key
        ├── Private Key
        └── Signing Interface


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


from datetime import datetime, timezone

from typing import Any, Dict, Optional


from wallets.exceptions import (
    WalletPrivateKeyError,
    WalletPublicKeyError,
    WalletValidationError,
)



###############################################################################
# Wallet Key Entity
###############################################################################


class WalletKey:
    """
    Represents a cryptographic key pair associated with a wallet.
    """



    def __init__(
        self,
        algorithm: str,
        network: str,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize wallet key.

        Parameters
        ----------
        algorithm:
            Cryptographic algorithm.

        network:
            Blockchain network.

        public_key:
            Public key material.

        private_key:
            Private key material.

        metadata:
            Additional key information.
        """


        self.algorithm = self._validate_algorithm(
            algorithm
        )


        self.network = self._validate_network(
            network
        )


        self._public_key = public_key


        self._private_key = private_key


        self.metadata = (
            metadata.copy()
            if metadata
            else {}
        )


        self.created_at = datetime.now(
            timezone.utc
        )



    ###############################################################################
    # Validation Helpers
    ###############################################################################


    def _validate_algorithm(
        self,
        algorithm: str,
    ) -> str:
        """
        Validate cryptographic algorithm.
        """

        if not isinstance(
            algorithm,
            str,
        ):

            raise WalletValidationError(
                "Algorithm must be a string"
            )


        if not algorithm.strip():

            raise WalletValidationError(
                "Key algorithm is required"
            )


        return algorithm.strip()



    def _validate_network(
        self,
        network: str,
    ) -> str:
        """
        Validate blockchain network.
        """

        if not isinstance(
            network,
            str,
        ):

            raise WalletValidationError(
                "Network must be a string"
            )


        if not network.strip():

            raise WalletValidationError(
                "Key network is required"
            )


        return network.lower().strip()



    ###############################################################################
    # Key Access Properties
    ###############################################################################


    @property
    def public_key(
        self,
    ) -> Optional[str]:
        """
        Return public key.

        Public keys are safe to expose.
        """

        return self._public_key



    @property
    def has_public_key(
        self,
    ) -> bool:
        """
        Check if public key exists.
        """

        return self._public_key is not None



    @property
    def has_private_key(
        self,
    ) -> bool:
        """
        Check if private key exists.
        """

        return self._private_key is not None
    
        ###############################################################################
    # Private Key Access Management
    ###############################################################################


    def get_private_key(
        self,
        authorized: bool = False,
    ) -> str:
        """
        Retrieve private key with authorization protection.

        Private key material must never be exposed without
        explicit authorization.

        Raises
        ------
        WalletValidationError
            Unauthorized access attempt.

        WalletPrivateKeyError
            Private key unavailable.
        """


        if not authorized:

            raise WalletValidationError(
                "Private key access denied"
            )


        if not self._private_key:

            raise WalletPrivateKeyError(
                "Private key is unavailable"
            )


        return self._private_key



    def clear_private_key(
        self,
    ) -> None:
        """
        Remove private key from memory.

        Used during:
        - session termination
        - wallet shutdown
        - security cleanup
        """

        self._private_key = None



    ###############################################################################
    # Key Validation
    ###############################################################################


    def validate(
        self,
    ) -> bool:
        """
        Validate key structure.

        Returns
        -------
        bool
            True if key structure is valid.
        """


        if not self.algorithm:

            raise WalletValidationError(
                "Missing key algorithm"
            )


        if not self.network:

            raise WalletValidationError(
                "Missing blockchain network"
            )


        if not self.has_public_key:

            raise WalletPublicKeyError(
                "Public key is missing"
            )


        return True



    ###############################################################################
    # Metadata Management
    ###############################################################################


    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Update key metadata.
        """


        if not isinstance(
            key,
            str,
        ):

            raise WalletValidationError(
                "Metadata key must be a string"
            )


        if not key.strip():

            raise WalletValidationError(
                "Metadata key cannot be empty"
            )


        self.metadata[key] = value



    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )



    ###############################################################################
    # Key Import / Export
    ###############################################################################


    def import_keys(
        self,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> None:
        """
        Import existing key material.

        Cryptographic validation is delegated to validators.py.
        """


        if (
            public_key is None
            and private_key is None
        ):

            raise WalletValidationError(
                "No key material provided"
            )


        if public_key:

            self._public_key = public_key



        if private_key:

            self._private_key = private_key



    def export_public_key(
        self,
    ) -> str:
        """
        Export public key.
        """


        if not self._public_key:

            raise WalletPublicKeyError(
                "Public key unavailable"
            )


        return self._public_key



    def export_private_key(
        self,
        authorized: bool = False,
    ) -> str:
        """
        Export private key.

        Requires authorization.
        """


        return self.get_private_key(
            authorized=authorized
        )
        ###############################################################################
    # Serialization
    ###############################################################################


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert wallet key into dictionary form.

        Private key material is intentionally excluded.
        """

        return {

            "algorithm": self.algorithm,

            "network": self.network,

            "public_key": self.public_key,

            "has_private_key": self.has_private_key,

            "metadata": self.metadata.copy(),

            "created_at": self.created_at.isoformat(),

        }



    ###############################################################################
    # Representation
    ###############################################################################


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.

        Private key data is never displayed.
        """

        return (

            f"WalletKey("
            f"algorithm='{self.algorithm}', "
            f"network='{self.network}', "
            f"private_key_present={self.has_private_key}"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.algorithm} key "
            f"for {self.network}"

        )
    ###############################################################################
# Module Exports
###############################################################################

__all__ = [
    "WalletKey",
]
###############################################################################
# End of wallets.keys
###############################################################################