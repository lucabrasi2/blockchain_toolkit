"""
Universal Blockchain Platform (UBP)

Module:
wallets.crypto.secp256k1

Purpose:
secp256k1 cryptographic implementation for UBP.

This module provides low-level cryptographic operations only.

It does not contain:
    - Bitcoin transaction logic
    - Ethereum transaction logic
    - TRON transaction logic
    - wallet management
    - custody management
    - private-key persistence

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.1 Enterprise
"""

from __future__ import annotations

from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from wallets.crypto.base import CryptoSigner

###############################################################################
# Constants
###############################################################################

PRIVATE_KEY_LENGTH = 32

###############################################################################
# Secp256k1 Signer
###############################################################################


class Secp256k1Signer(CryptoSigner):
    """
    Low-level secp256k1 cryptographic signer.

    The implementation uses the cryptography package's
    SECP256K1 elliptic curve.

    Private keys are supplied by the caller and are not
    persisted by this class.
    """

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def algorithm(
        self,
    ) -> str:
        """
        Return the cryptographic algorithm identifier.
        """

        return "secp256k1"

    ###########################################################################
    # Signing
    ###########################################################################

    def sign(
        self,
        message: bytes,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Sign a message using a secp256k1 private key.

        Parameters
        ----------
        message:
            Data to sign.

        private_key:
            32-byte secp256k1 private key.

        options:
            Optional signing configuration.

        Supported options
        -----------------
        hash_algorithm:
            Optional cryptography hash algorithm instance.

            Defaults to SHA256.

        Returns
        -------
        bytes
            DER-encoded ECDSA signature.

        Notes
        -----
        Blockchain-specific message hashing and transaction
        serialization remain outside this class.
        """

        self._validate_message(
            message
        )

        key = self._load_private_key(
            private_key
        )

        hash_algorithm = options.get(
            "hash_algorithm",
            hashes.SHA256(),
        )

        if not isinstance(
            hash_algorithm,
            hashes.HashAlgorithm,
        ):
            raise TypeError(
                "hash_algorithm must be a cryptography "
                "HashAlgorithm instance."
            )

        return key.sign(
            message,
            ec.ECDSA(
                hash_algorithm
            ),
        )
        ###########################################################################
    # Prehashed Digest Signing
    ###########################################################################

    def sign_digest(
        self,
        digest: bytes,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Sign an already-hashed digest using secp256k1.

        Parameters
        ----------
        digest:
            Precomputed message digest.

        private_key:
            32-byte secp256k1 private key.

        options:
            Optional signing configuration.

        Supported options
        -----------------
        hash_algorithm:
            Hash algorithm represented by the supplied digest.

            Defaults to SHA256.

        Returns
        -------
        bytes
            DER-encoded ECDSA signature.

        Notes
        -----
        This method does not hash the supplied digest again.

        It exists for blockchain protocols such as Bitcoin where
        transaction-specific signing rules produce the digest before
        the elliptic-curve signing operation.

        Blockchain-specific digest construction remains outside this
        class.
        """

        if not isinstance(
            digest,
            bytes,
        ):
            raise TypeError(
                "digest must be bytes."
            )

        if not digest:
            raise ValueError(
                "digest cannot be empty."
            )

        key = self._load_private_key(
            private_key
        )

        hash_algorithm = options.get(
            "hash_algorithm",
            hashes.SHA256(),
        )

        if not isinstance(
            hash_algorithm,
            hashes.HashAlgorithm,
        ):
            raise TypeError(
                "hash_algorithm must be a cryptography "
                "HashAlgorithm instance."
            )

        expected_digest_size = (
            hash_algorithm.digest_size
        )

        if len(digest) != expected_digest_size:
            raise ValueError(
                "digest length does not match the "
                "selected hash algorithm."
            )

        from cryptography.hazmat.primitives.asymmetric.utils import (
            Prehashed,
        )

        return key.sign(
            digest,
            ec.ECDSA(
                Prehashed(
                    hash_algorithm
                )
            ),
        )
    ###########################################################################
    # Public Key Derivation
    ###########################################################################

    def derive_public_key(
        self,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Derive the compressed or uncompressed public key.

        Parameters
        ----------
        private_key:
            32-byte secp256k1 private key.

        options
        -------
        compressed:
            Whether to return a compressed public key.

            Defaults to True.

        Returns
        -------
        bytes
            Serialized public key.
        """

        key = self._load_private_key(
            private_key
        )

        compressed = options.get(
            "compressed",
            True,
        )

        if not isinstance(
            compressed,
            bool,
        ):
            raise TypeError(
                "compressed must be a boolean."
            )

        public_key = key.public_key()

        from cryptography.hazmat.primitives import serialization

        encoding = serialization.Encoding.X962

        if compressed:
            format_type = (
                serialization.PublicFormat.CompressedPoint
            )
        else:
            format_type = (
                serialization.PublicFormat.UncompressedPoint
            )

        return public_key.public_bytes(
            encoding=encoding,
            format=format_type,
        )

    ###########################################################################
    # Private-Key Validation
    ###########################################################################

    def validate_private_key(
        self,
        private_key: bytes,
    ) -> bool:
        """
        Validate secp256k1 private-key material.

        Parameters
        ----------
        private_key:
            Private key bytes.

        Returns
        -------
        bool
            True when the private key is valid.

        Notes
        -----
        Invalid key material returns False rather than exposing
        cryptographic implementation details.
        """

        if not isinstance(
            private_key,
            bytes,
        ):
            return False

        if len(
            private_key
        ) != PRIVATE_KEY_LENGTH:
            return False

        try:
            self._load_private_key(
                private_key
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        return True

    ###########################################################################
    # Internal Helpers
    ###########################################################################

    def _load_private_key(
        self,
        private_key: bytes,
    ) -> ec.EllipticCurvePrivateKey:
        """
        Convert raw private-key bytes into a secp256k1 key object.
        """

        if not isinstance(
            private_key,
            bytes,
        ):
            raise TypeError(
                "private_key must be bytes."
            )

        if len(
            private_key
        ) != PRIVATE_KEY_LENGTH:
            raise ValueError(
                "secp256k1 private key must be exactly "
                "32 bytes."
            )

        private_key_int = int.from_bytes(
            private_key,
            byteorder="big",
        )

        if private_key_int == 0:
            raise ValueError(
                "Invalid secp256k1 private key."
            )

        try:
            return ec.derive_private_key(
                private_key_int,
                ec.SECP256K1(),
            )

        except ValueError as exc:
            raise ValueError(
                "Invalid secp256k1 private key."
            ) from exc

    @staticmethod
    def _validate_message(
        message: bytes,
    ) -> None:
        """
        Validate signing input.
        """

        if not isinstance(
            message,
            bytes,
        ):
            raise TypeError(
                "message must be bytes."
            )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "PRIVATE_KEY_LENGTH",
    "Secp256k1Signer",
]


###############################################################################
# End of File
###############################################################################
