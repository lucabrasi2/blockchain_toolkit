"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.encryption

Purpose
-------
Enterprise wallet encryption service.

This module provides secure encryption, key derivation, hashing and payload
validation services for wallet data.

Responsibilities
----------------
- Generate cryptographic salts
- Derive encryption keys (PBKDF2, Argon2id)
- Encrypt wallet data (str or bytes)
- Decrypt wallet data
- Validate encrypted payloads
- Generate data hashes
- Verify hashes (timing-safe)

Architecture
------------

WalletManager
      |
      ▼
EncryptionManager
      |
      ├── Salt Generator
      ├── PBKDF2 Key Derivation
      ├── Argon2id Key Derivation (optional)
      ├── AES-256 Encryption
      ├── Payload Validator
      └── SHA-256 Integrity Layer


Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise  (Step 3 — Hardened Encryption)
===============================================================================
"""


from __future__ import annotations


import os
import base64
import hashlib
import hmac


from typing import Any
from typing import Dict


from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


from wallets.exceptions import (
    WalletValidationError,
)


###############################################################################
# Optional Argon2id Support
###############################################################################


try:
    from argon2.low_level import (
        hash_secret_raw,
        Type,
    )

    ARGON2_AVAILABLE = True

except ImportError:

    ARGON2_AVAILABLE = False


###############################################################################
# Encryption Manager
###############################################################################


class EncryptionManager:
    """
    Enterprise wallet encryption service.

    Provides AES-256 encryption with PBKDF2 or Argon2id key derivation.
    """


    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
        algorithm: str = "AES-256",
    ) -> None:
        """
        Initialize encryption service.

        Parameters
        ----------
        algorithm:
            Encryption algorithm name.
        """


        if algorithm != "AES-256":

            raise WalletValidationError(
                "Unsupported encryption algorithm."
            )


        self.algorithm = algorithm

    ###########################################################################
    # Salt Generation
    ###########################################################################


    def generate_salt(
        self,
    ) -> bytes:
        """
        Generate cryptographic salt.

        Returns
        -------
        bytes
            32-byte random salt.
        """

        return os.urandom(32)



    ###########################################################################
    # Key Derivation
    ###########################################################################


    def derive_key(
        self,
        password: str,
        salt: bytes,
        iterations: int = 390000,
    ) -> bytes:
        """
        Derive AES-256 encryption key via PBKDF2.

        Parameters
        ----------
        password:
            User encryption password.

        salt:
            Cryptographic salt.

        iterations:
            PBKDF2 iteration count.
            OWASP minimum is 390,000 for SHA-256.

        Returns
        -------
        bytes
            Derived 256-bit key.
        """


        if not password:

            raise WalletValidationError(
                "Password cannot be empty."
            )


        if not isinstance(
            salt,
            bytes,
        ):

            raise WalletValidationError(
                "Salt must be bytes."
            )


        kdf = PBKDF2HMAC(

            algorithm=hashes.SHA256(),

            length=32,

            salt=salt,

            iterations=iterations,

        )


        return kdf.derive(

            password.encode(
                "utf-8"
            )

        )


    def derive_key_argon2id(
        self,
        password: str,
        salt: bytes,
    ) -> bytes:
        """
        Derive AES-256 encryption key via Argon2id.

        Argon2id is memory-hard and resistant to GPU/ASIC attacks.
        It is preferred over PBKDF2 for new keystore files.

        Parameters
        ----------
        password:
            User encryption password.

        salt:
            Cryptographic salt (must be >= 8 bytes).

        Returns
        -------
        bytes
            Derived 256-bit key.

        Raises
        ------
        WalletValidationError
            If argon2-cffi is not installed.
        """

        if not ARGON2_AVAILABLE:

            raise WalletValidationError(
                "Argon2id requires the 'argon2-cffi' package. "
                "Install with: pip install argon2-cffi"
            )

        if not password:

            raise WalletValidationError(
                "Password cannot be empty."
            )

        if not isinstance(
            salt,
            bytes,
        ):

            raise WalletValidationError(
                "Salt must be bytes."
            )

        return hash_secret_raw(

            secret=password.encode(
                "utf-8"
            ),

            salt=salt,

            memory_cost=65536,

            time_cost=3,

            parallelism=4,

            hash_len=32,

            type=Type.ID,

        )


    ###########################################################################
    # Encryption
    ###########################################################################


    def encrypt(
        self,
        data: str | bytes,
        password: str,
        **options: Any,
    ) -> Dict[str, Any]:
        """
        Encrypt plaintext data.

        Parameters
        ----------
        data:
            Data to encrypt.  Accepts str or bytes.

        password:
            Encryption password.

        options:
            Optional encryption configuration.

        Supported options
        -----------------
        kdf:
            Key derivation function: "pbkdf2" (default) or "argon2id".

        iterations:
            PBKDF2 iteration count.  Defaults to 390000.

        Returns
        -------
        dict
            Encrypted payload with versioned metadata.
        """


        if not isinstance(
            data,
            (
                str,
                bytes,
            ),
        ):

            raise WalletValidationError(
                "Data must be a string or bytes."
            )


        kdf = options.get(
            "kdf",
            "pbkdf2",
        ).lower()

        iterations = options.get(
            "iterations",
            390000,
        )

        salt = self.generate_salt()

        if kdf == "pbkdf2":

            key = self.derive_key(
                password,
                salt,
                iterations=iterations,
            )

        elif kdf == "argon2id":

            key = self.derive_key_argon2id(
                password,
                salt,
            )

        else:

            raise WalletValidationError(
                f"Unsupported KDF: {kdf}"
            )


        nonce = os.urandom(12)


        cipher = AESGCM(
            key
        )

        if isinstance(
            data,
            str,
        ):

            plaintext = data.encode(
                "utf-8"
            )

            data_encoding = "utf-8"

        else:

            plaintext = data

            data_encoding = "raw"


        ciphertext = cipher.encrypt(

            nonce,

            plaintext,

            None,

        )


        payload = {

            "version":
                "2.1",


            "algorithm":
                self.algorithm,


            "kdf":
                kdf,


            "iterations":
                iterations,


            "salt":
                base64.b64encode(
                    salt
                ).decode(
                    "utf-8"
                ),


            "nonce":
                base64.b64encode(
                    nonce
                ).decode(
                    "utf-8"
                ),


            "ciphertext":
                base64.b64encode(
                    ciphertext
                ).decode(
                    "utf-8"
                ),


            "data_encoding":
                data_encoding,

        }

        return payload



    ###########################################################################
    # Decryption
    ###########################################################################


    def decrypt(
        self,
        payload: Dict[str, Any],
        password: str,
    ) -> str | bytes:
        """
        Decrypt encrypted wallet data.

        Parameters
        ----------
        payload:
            Encrypted payload.

        password:
            Encryption password.

        Returns
        -------
        str | bytes
            Original plaintext.  Returns str when the original
            data was a string; returns bytes when the original
            data was bytes.

        Raises
        ------
        WalletValidationError
            If payload is invalid or KDF is unsupported.
        """


        self.validate_payload(
            payload
        )


        salt = base64.b64decode(

            payload["salt"]

        )


        nonce = base64.b64decode(

            payload["nonce"]

        )


        ciphertext = base64.b64decode(

            payload["ciphertext"]

        )


        kdf = payload.get(
            "kdf",
            "pbkdf2",
        ).lower()

        iterations = payload.get(
            "iterations",
            390000,
        )


        if kdf == "pbkdf2":

            key = self.derive_key(
                password,
                salt,
                iterations=iterations,
            )

        elif kdf == "argon2id":

            key = self.derive_key_argon2id(
                password,
                salt,
            )

        else:

            raise WalletValidationError(
                f"Unsupported KDF: {kdf}"
            )


        cipher = AESGCM(
            key
        )


        plaintext = cipher.decrypt(

            nonce,

            ciphertext,

            None,

        )


        data_encoding = payload.get(
            "data_encoding",
            "utf-8",
        )


        if data_encoding == "utf-8":

            return plaintext.decode(
                "utf-8"
            )

        return plaintext


    ###########################################################################
    # Payload Validation
    ###########################################################################


    def validate_payload(
        self,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Validate encrypted payload structure.

        Parameters
        ----------
        payload:
            Encrypted payload dictionary.

        Returns
        -------
        bool
            True if payload is valid.

        Raises
        ------
        WalletValidationError
            If payload is invalid.
        """


        if not isinstance(
            payload,
            dict,
        ):

            raise WalletValidationError(
                "Encrypted payload must be a dictionary."
            )


        required_fields = (

            "algorithm",

            "salt",

            "nonce",

            "ciphertext",

        )


        for field in required_fields:

            if field not in payload:

                raise WalletValidationError(
                    f"Missing encrypted field: {field}"
                )


        if payload["algorithm"] != self.algorithm:

            raise WalletValidationError(
                "Encryption algorithm mismatch."
            )


        return True



    ###########################################################################
    # Hash Generation
    ###########################################################################


    def generate_hash(
        self,
        data: str,
    ) -> str:
        """
        Generate SHA-256 hash.

        Parameters
        ----------
        data:
            Input data.

        Returns
        -------
        str
            SHA-256 hexadecimal digest.
        """


        if not isinstance(
            data,
            str,
        ):

            raise WalletValidationError(
                "Hash data must be a string."
            )


        return hashlib.sha256(

            data.encode(
                "utf-8"
            )

        ).hexdigest()



    ###########################################################################
    # Hash Verification
    ###########################################################################


    def verify_hash(
        self,
        data: str,
        digest: str,
    ) -> bool:
        """
        Verify SHA-256 hash using constant-time comparison.

        Parameters
        ----------
        data:
            Original data.

        digest:
            Expected digest.

        Returns
        -------
        bool
            True if hashes match.

        Notes
        -----
        Uses hmac.compare_digest to prevent timing attacks.
        """


        generated_hash = self.generate_hash(

            data

        )


        return hmac.compare_digest(

            generated_hash.encode(
                "utf-8"
            ),

            digest.encode(
                "utf-8"
            ),

        )



    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return encryption service information.

        Returns
        -------
        dict
            Encryption metadata.
        """


        return {

            "service":
                "Wallet Encryption",


            "version":
                "2.1 Enterprise",


            "algorithm":
                self.algorithm,


            "kdf_primary":
                "PBKDF2-HMAC-SHA256",


            "kdf_alternative":
                "Argon2id"
                if ARGON2_AVAILABLE
                else "not installed",


            "hash":
                "SHA-256",


            "key_size":
                "256-bit",

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

            f"EncryptionManager("
            f"algorithm='{self.algorithm}'"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """


        return (

            f"Wallet Encryption "
            f"Service ({self.algorithm})"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "EncryptionManager",

]


###############################################################################
# End of wallets.encryption
###############################################################################