"""
Universal Blockchain Platform (UBP)

Module:
wallets.crypto.base

Purpose:
Abstract cryptographic signing interface for UBP.

Architecture:
    CustodyProvider
          ↓
    Blockchain Signing Adapter
          ↓
       CryptoSigner
          ↓
    Cryptographic Implementation

The crypto layer is blockchain-agnostic.

It does not contain Bitcoin, Ethereum, TRON,
or any other blockchain-specific transaction logic.

Private-key ownership remains with the custody/key-management
layers. Implementations receive key material only through an
explicitly authorized signing boundary.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.1 Enterprise
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


###############################################################################
# Crypto Signer
###############################################################################


class CryptoSigner(ABC):
    """
    Abstract interface for UBP cryptographic signing.

    A CryptoSigner performs low-level cryptographic signing.

    It does not:
        - construct blockchain transactions;
        - serialize blockchain transactions;
        - calculate blockchain-specific signature hashes;
        - manage wallets;
        - store private keys;
        - manage custody.

    Those responsibilities belong to higher-level layers.
    """

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    @abstractmethod
    def algorithm(
        self,
    ) -> str:
        """
        Return the canonical cryptographic implementation identifier.

        The algorithm identifier identifies the concrete cryptographic
        signing implementation used by this CryptoSigner.

        Examples
        --------
        "secp256k1"
        "ed25519"

        Notes
        -----
        This identifier does not represent:

        - a blockchain;
        - a blockchain transaction format;
        - a transaction hash algorithm;
        - a blockchain-specific signature scheme.

        Blockchain-specific signing rules and transaction hashing remain
        the responsibility of the corresponding blockchain signing adapter.

        Returns
        -------
        str
            Canonical cryptographic implementation identifier.
        """

        raise NotImplementedError

    ###########################################################################
    # Signing
    ###########################################################################

    @abstractmethod
    def sign(
        self,
        message: bytes,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Sign arbitrary data using the configured algorithm.

        Parameters
        ----------
        message:
            Data to be signed.

        private_key:
            Private-key material supplied by an authorized
            custody/key-management boundary.

        options:
            Algorithm-specific signing options.

        Returns
        -------
        bytes
            Raw or algorithm-defined signature.

        Raises
        ------
        TypeError
            If message or private_key has an invalid type.

        ValueError
            If the supplied data is invalid.

        Notes
        -----
        Implementations must not persist the supplied private key.
        """

        raise NotImplementedError

    ###########################################################################
    # Prehashed Digest Signing
    ###########################################################################

    @abstractmethod
    def sign_digest(
        self,
        digest: bytes,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Sign an already-computed cryptographic digest.

        Parameters
        ----------
        digest:
            Precomputed message digest.

        private_key:
            Private-key material supplied by an authorized
            custody/key-management boundary.

        options:
            Algorithm-specific signing options.

        Returns
        -------
        bytes
            Raw or algorithm-defined signature.

        Raises
        ------
        TypeError
            If digest or private_key has an invalid type.

        ValueError
            If the supplied digest or private key is invalid.

        Notes
        -----
        Implementations must not hash the supplied digest again.

        This method exists for blockchain protocols whose
        transaction-specific signing rules construct the digest
        before the low-level cryptographic signing operation.

        Implementations must not persist the supplied private key.
        """

        raise NotImplementedError

    ###########################################################################
    # Public Key Derivation
    ###########################################################################

    @abstractmethod
    def derive_public_key(
        self,
        private_key: bytes,
        **options: Any,
    ) -> bytes:
        """
        Derive public-key material from a private key.

        Parameters
        ----------
        private_key:
            Private-key material supplied by an authorized
            custody/key-management boundary.

        options:
            Algorithm-specific options.

        Returns
        -------
        bytes
            Public-key material.

        Raises
        ------
        TypeError
            If private_key has an invalid type.

        ValueError
            If the private key is invalid.

        Notes
        -----
        Implementations must not persist the supplied private key.
        """

        raise NotImplementedError

    ###########################################################################
    # Validation
    ###########################################################################

    @abstractmethod
    def validate_private_key(
        self,
        private_key: bytes,
    ) -> bool:
        """
        Validate private-key material.

        Parameters
        ----------
        private_key:
            Private-key material.

        Returns
        -------
        bool
            True when the private key is valid for the implementation.
        """

        raise NotImplementedError

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"algorithm={self.algorithm!r}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "CryptoSigner",
]


###############################################################################
# End of File
###############################################################################