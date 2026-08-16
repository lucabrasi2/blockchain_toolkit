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
- Protect private-key access
- Provide the cryptographic signing boundary
- Provide safe key metadata handling
- Support encrypted key serialization
- Support secure private-key cleanup

Architecture
------------

    Wallet
      |
      +-- WalletKey
             |
             +-- Public Key
             |
             +-- Private Key
             |
             +-- CryptoSigner
                    |
                    +-- Cryptographic Implementation

Security Boundary
-----------------

WalletKey owns access to private-key material.

CryptoSigner performs the actual low-level cryptographic operation.

WalletKey does NOT:
- implement ECDSA
- implement secp256k1
- implement Bitcoin signing
- implement Ethereum signing
- implement TRON signing
- serialize blockchain transactions
- communicate with blockchain providers

Those responsibilities belong to their respective layers.

Private-key material must only cross the WalletKey boundary when
explicit authorization has been supplied.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
===============================================================================
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional

from wallets.crypto.base import CryptoSigner
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
    Represents cryptographic key material associated with a wallet.

    Public-key material is safe to expose.

    Private-key material is held internally as a mutable bytearray so that
    WalletKey can overwrite its internal representation when the key is
    cleared or replaced.

    WalletKey is intentionally blockchain-agnostic.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        algorithm: str,
        network: str,
        public_key: Optional[str] = None,
        private_key: Optional[bytes | bytearray] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a WalletKey.

        Parameters
        ----------
        algorithm:
            Cryptographic algorithm identifier.

        network:
            Blockchain network identifier.

        public_key:
            Public-key material.

        private_key:
            Private-key material.

            Must be bytes or bytearray when supplied.

        metadata:
            Optional key metadata.
        """

        self.algorithm = self._validate_algorithm(
            algorithm
        )

        self.network = self._validate_network(
            network
        )

        self._public_key = self._validate_public_key(
            public_key
        )

        self._private_key = self._coerce_private_key(
            private_key
        )

        self.metadata: Dict[str, Any] = (
            metadata.copy()
            if metadata is not None
            else {}
        )

        self.created_at = datetime.now(
            timezone.utc
        )

    ###########################################################################
    # Validation Helpers
    ###########################################################################

    @staticmethod
    def _validate_algorithm(
        algorithm: str,
    ) -> str:
        """
        Validate and normalize the cryptographic algorithm identifier.

        Returns
        -------
        str
            Normalized algorithm identifier.

        Raises
        ------
        WalletValidationError
            If algorithm is missing or invalid.
        """

        if not isinstance(
            algorithm,
            str,
        ):
            raise WalletValidationError(
                "Algorithm must be a string."
            )

        value = algorithm.strip()

        if not value:
            raise WalletValidationError(
                "Key algorithm is required."
            )

        return value

    @staticmethod
    def _validate_network(
        network: str,
    ) -> str:
        """
        Validate and normalize the blockchain network identifier.

        Returns
        -------
        str
            Normalized lowercase network identifier.

        Raises
        ------
        WalletValidationError
            If network is missing or invalid.
        """

        if not isinstance(
            network,
            str,
        ):
            raise WalletValidationError(
                "Network must be a string."
            )

        value = network.strip().lower()

        if not value:
            raise WalletValidationError(
                "Key network is required."
            )

        return value

    @staticmethod
    def _validate_public_key(
        public_key: Optional[str],
    ) -> Optional[str]:
        """
        Validate public-key material.

        Public-key validation of actual cryptographic structure remains
        the responsibility of the appropriate validation/crypto layer.

        This method validates only the basic representation.
        """

        if public_key is None:
            return None

        if not isinstance(
            public_key,
            str,
        ):
            raise WalletValidationError(
                "Public key must be a string or None."
            )

        value = public_key.strip()

        if not value:
            return None

        return value

    @staticmethod
    def _coerce_private_key(
        private_key: Optional[bytes | bytearray],
    ) -> Optional[bytearray]:
        """
        Convert private-key material into private WalletKey storage.

        A new bytearray is always created.

        This is intentional even when the caller provides a bytearray.
        WalletKey must not retain ownership of a caller-controlled mutable
        buffer.

        Returns
        -------
        Optional[bytearray]
            Mutable private-key storage.

        Raises
        ------
        TypeError
            If the private key is not bytes or bytearray.
        """

        if private_key is None:
            return None

        if isinstance(
            private_key,
            bytes,
        ):
            return bytearray(
                private_key
            )

        if isinstance(
            private_key,
            bytearray,
        ):
            return bytearray(
                private_key
            )

        raise TypeError(
            "Private key must be bytes or bytearray. "
            f"Received: {type(private_key).__name__}"
        )

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def has_public_key(
        self,
    ) -> bool:
        """
        Return whether public-key material is available.
        """

        return self._public_key is not None

    @property
    def has_private_key(
        self,
    ) -> bool:
        """
        Return whether private-key material is available.
        """

        return self._private_key is not None

    ###########################################################################
    # Public Key Access
    ###########################################################################

    @property
    def public_key(
        self,
    ) -> Optional[str]:
        """
        Return public-key material.

        Public keys are not considered secret key material.
        """

        return self._public_key

    ###########################################################################
    # Private Key Access
    ###########################################################################

    def get_private_key(
        self,
        authorized: bool = False,
    ) -> bytes:
        """
        Retrieve private-key material.

        Explicit authorization is mandatory.

        A bytes copy is returned rather than the internal bytearray.

        Parameters
        ----------
        authorized:
            Explicit authorization to access private-key material.

        Returns
        -------
        bytes
            Private-key material.

        Raises
        ------
        WalletValidationError
            If access has not been authorized.

        WalletPrivateKeyError
            If no private key is available.
        """

        if not authorized:
            raise WalletValidationError(
                "Private key access denied."
            )

        if self._private_key is None:
            raise WalletPrivateKeyError(
                "Private key is unavailable."
            )

        return bytes(
            self._private_key
        )

    ###########################################################################
    # Cryptographic Signing
    ###########################################################################

    def sign_digest(
        self,
        digest: bytes,
        signer: CryptoSigner,
        authorized: bool = False,
        **options: Any,
    ) -> bytes:
        """
        Sign a precomputed digest.

        WalletKey controls access to the private key.

        CryptoSigner performs the low-level cryptographic operation.

        Blockchain-specific digest construction must occur outside this
        class.

        Parameters
        ----------
        digest:
            Precomputed cryptographic digest.

        signer:
            CryptoSigner implementation.

        authorized:
            Explicit authorization to use private-key material.

        options:
            Algorithm-specific signing options.

        Returns
        -------
        bytes
            Cryptographic signature.

        Raises
        ------
        TypeError
            If digest or signer has an invalid type.

        WalletValidationError
            If signing has not been authorized or the signer algorithm
            does not match the wallet key.

        WalletPrivateKeyError
            If the private key is unavailable.
        """

        if not isinstance(
            digest,
            bytes,
        ):
            raise TypeError(
                "digest must be bytes."
            )

        if not isinstance(
            signer,
            CryptoSigner,
        ):
            raise TypeError(
                "signer must be a CryptoSigner instance."
            )

        if not authorized:
            raise WalletValidationError(
                "Private key access denied."
            )

        if (
            signer.algorithm.lower()
            != self.algorithm.lower()
        ):
            raise WalletValidationError(
                "Signer algorithm does not match "
                "wallet key algorithm."
            )

        private_key = self.get_private_key(
            authorized=True
        )

        try:
            return signer.sign_digest(
                digest,
                private_key,
                **options,
            )

        finally:
            # Python bytes objects are immutable, therefore the local
            # variable cannot be securely wiped in place.
            #
            # The authoritative private-key representation remains inside
            # WalletKey as a mutable bytearray and can be wiped using
            # clear_private_key().
            del private_key

    ###########################################################################
    # Private-Key Cleanup
    ###########################################################################

    def clear_private_key(
        self,
    ) -> None:
        """
        Clear private-key material held by WalletKey.

        The internal bytearray is overwritten with zero bytes before the
        reference is released.

        This method is intended for:
        - wallet shutdown
        - session termination
        - security cleanup
        - key replacement
        - explicit key destruction
        """

        if self._private_key is None:
            return

        for index in range(
            len(self._private_key)
        ):
            self._private_key[index] = 0

        self._private_key = None

    ###########################################################################
    # Key Validation
    ###########################################################################

    def validate(
        self,
    ) -> bool:
        """
        Validate the structural state of the WalletKey.

        Cryptographic validation of actual key material belongs to the
        appropriate crypto/validator implementation.

        Returns
        -------
        bool
            True when the key structure is valid.

        Raises
        ------
        WalletValidationError
            If required identity information is missing.

        WalletPublicKeyError
            If public-key material is missing.
        """

        if not self.algorithm:
            raise WalletValidationError(
                "Missing key algorithm."
            )

        if not self.network:
            raise WalletValidationError(
                "Missing blockchain network."
            )

        if not self.has_public_key:
            raise WalletPublicKeyError(
                "Public key is missing."
            )

        return True

    ###########################################################################
    # Metadata Management
    ###########################################################################

    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or replace metadata.

        Parameters
        ----------
        key:
            Metadata key.

        value:
            Metadata value.

        Raises
        ------
        WalletValidationError
            If the metadata key is invalid.
        """

        if not isinstance(
            key,
            str,
        ):
            raise WalletValidationError(
                "Metadata key must be a string."
            )

        key = key.strip()

        if not key:
            raise WalletValidationError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata.

        Parameters
        ----------
        key:
            Metadata key.

        default:
            Value returned when the key does not exist.
        """

        return self.metadata.get(
            key,
            default,
        )

    ###########################################################################
    # Key Import
    ###########################################################################

    def import_keys(
        self,
        public_key: Optional[str] = None,
        private_key: Optional[bytes | bytearray] = None,
    ) -> None:
        """
        Import or replace key material.

        Existing private-key material is wiped before replacement.

        Parameters
        ----------
        public_key:
            Public-key material.

        private_key:
            Private-key material.

        Raises
        ------
        WalletValidationError
            If no key material is supplied.
        """

        if (
            public_key is None
            and private_key is None
        ):
            raise WalletValidationError(
                "No key material provided."
            )

        if public_key is not None:
            self._public_key = self._validate_public_key(
                public_key
            )

        if private_key is not None:
            new_private_key = self._coerce_private_key(
                private_key
            )

            self.clear_private_key()

            self._private_key = new_private_key

    ###########################################################################
    # Public-Key Export
    ###########################################################################

    def export_public_key(
        self,
    ) -> str:
        """
        Export public-key material.

        Raises
        ------
        WalletPublicKeyError
            If public-key material is unavailable.
        """

        if self._public_key is None:
            raise WalletPublicKeyError(
                "Public key unavailable."
            )

        return self._public_key

    ###########################################################################
    # Private-Key Export
    ###########################################################################

    def export_private_key(
        self,
        authorized: bool = False,
    ) -> bytes:
        """
        Export private-key material.

        Explicit authorization is required.
        """

        return self.get_private_key(
            authorized=authorized
        )

    ###########################################################################
    # Public Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert WalletKey into a public metadata dictionary.

        Private-key material is intentionally excluded.

        This representation is suitable for:
        - inspection
        - logging
        - public metadata
        - non-secret wallet reports

        It is NOT a complete backup of private key material.
        """

        return {
            "algorithm": self.algorithm,
            "network": self.network,
            "public_key": self.public_key,
            "has_private_key": self.has_private_key,
            "metadata": self.metadata.copy(),
            "created_at": self.created_at.isoformat(),
        }

    ###########################################################################
    # Encrypted Serialization
    ###########################################################################

    def to_encrypted_dict(
        self,
        encryption_manager: Any,
        password: str,
    ) -> Dict[str, Any]:
        """
        Serialize WalletKey with encrypted private-key material.

        The private key is converted to hexadecimal text and passed to
        EncryptionManager.

        WalletKey does not implement encryption itself.

        Parameters
        ----------
        encryption_manager:
            EncryptionManager instance.

        password:
            Encryption password.

        Returns
        -------
        dict[str, Any]
            Encrypted keystore payload.

        Raises
        ------
        WalletPrivateKeyError
            If no private key exists.

        TypeError
            If encryption_manager or password has an invalid type.
        """

        if not self.has_private_key:
            raise WalletPrivateKeyError(
                "Cannot encrypt: private key is unavailable."
            )

        if not isinstance(
            password,
            str,
        ):
            raise TypeError(
                "Password must be a string."
            )

        if not password:
            raise WalletValidationError(
                "Encryption password cannot be empty."
            )

        if encryption_manager is None:
            raise TypeError(
                "encryption_manager is required."
            )

        private_key = self.get_private_key(
            authorized=True
        )

        try:
            private_key_hex = private_key.hex()

            encrypted_payload = (
                encryption_manager.encrypt(
                    private_key_hex,
                    password,
                )
            )

        finally:
            del private_key

        return {
            "version": "ubp-keystore-1.0",
            "algorithm": self.algorithm,
            "network": self.network,
            "public_key": self.public_key,
            "metadata": self.metadata.copy(),
            "created_at": self.created_at.isoformat(),
            "encrypted_private_key": encrypted_payload,
        }

    ###########################################################################
    # Encrypted Deserialization
    ###########################################################################

    @classmethod
    def from_encrypted_dict(
        cls,
        data: Dict[str, Any],
        encryption_manager: Any,
        password: str,
    ) -> "WalletKey":
        """
        Restore a WalletKey from an encrypted keystore payload.

        Parameters
        ----------
        data:
            Encrypted WalletKey dictionary.

        encryption_manager:
            EncryptionManager instance.

        password:
            Decryption password.

        Returns
        -------
        WalletKey
            Restored WalletKey instance.

        Raises
        ------
        WalletValidationError
            If the payload is malformed.

        WalletPrivateKeyError
            If decryption or private-key reconstruction fails.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise WalletValidationError(
                "Keystore data must be a dictionary."
            )

        if not isinstance(
            password,
            str,
        ):
            raise TypeError(
                "Password must be a string."
            )

        if not password:
            raise WalletValidationError(
                "Decryption password cannot be empty."
            )

        if encryption_manager is None:
            raise TypeError(
                "encryption_manager is required."
            )

        required_fields = (
            "algorithm",
            "network",
            "encrypted_private_key",
        )

        for field in required_fields:
            if field not in data:
                raise WalletValidationError(
                    f"Missing keystore field: {field}"
                )

        encrypted_private_key = data[
            "encrypted_private_key"
        ]

        try:
            decrypted_hex = (
                encryption_manager.decrypt(
                    encrypted_private_key,
                    password,
                )
            )

            if not isinstance(
                decrypted_hex,
                str,
            ):
                raise TypeError(
                    "Decrypted private key must be a string."
                )

            private_key = bytes.fromhex(
                decrypted_hex
            )

        except WalletPrivateKeyError:
            raise

        except Exception as exc:
            raise WalletPrivateKeyError(
                "Failed to decrypt private key. "
                "Wrong password or corrupt payload."
            ) from exc

        try:
            return cls(
                algorithm=data["algorithm"],
                network=data["network"],
                public_key=data.get(
                    "public_key"
                ),
                private_key=private_key,
                metadata=data.get(
                    "metadata",
                    {},
                ),
            )

        finally:
            del private_key

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.

        Private-key material is never displayed.
        """

        return (
            "WalletKey("
            f"algorithm={self.algorithm!r}, "
            f"network={self.network!r}, "
            f"private_key_present="
            f"{self.has_private_key}"
            ")"
        )

    def __str__(
        self,
    ) -> str:
        """
        Return a human-readable representation.

        Private-key material is never displayed.
        """

        return (
            f"{self.algorithm} key "
            f"for {self.network}"
        )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "WalletKey",
]


###############################################################################
# End of wallets.keys
###############################################################################