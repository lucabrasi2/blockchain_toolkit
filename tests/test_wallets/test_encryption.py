"""
Tests for wallets.encryption module.

Step 3 — Hardened Encryption

Covers polymorphic encrypt/decrypt (str | bytes), payload versioning,
configurable KDF, and timing-safe hash verification.
"""

import pytest

from wallets.encryption import EncryptionManager, ARGON2_AVAILABLE
from wallets.exceptions import (
    WalletValidationError,
)


###############################################################################
# Creation Tests
###############################################################################


def test_encryption_manager_creation():

    manager = EncryptionManager()

    assert manager.algorithm == "AES-256"



def test_invalid_algorithm():

    with pytest.raises(
        WalletValidationError
    ):

        EncryptionManager(
            algorithm=""
        )


###############################################################################
# Salt Generation
###############################################################################


def test_generate_salt():

    manager = EncryptionManager()

    salt = manager.generate_salt()

    assert isinstance(salt, bytes)

    assert len(salt) == 32



###############################################################################
# Key Derivation
###############################################################################


def test_derive_key():

    manager = EncryptionManager()

    salt = manager.generate_salt()

    key = manager.derive_key(
        "password",
        salt,
    )

    assert isinstance(key, bytes)

    assert len(key) == 32



def test_derive_key_custom_iterations():
    """
    PBKDF2 iteration count must be configurable.
    """

    manager = EncryptionManager()

    salt = manager.generate_salt()

    key_fast = manager.derive_key(
        "password",
        salt,
        iterations=1000,
    )

    key_slow = manager.derive_key(
        "password",
        salt,
        iterations=390000,
    )

    assert isinstance(key_fast, bytes)
    assert isinstance(key_slow, bytes)
    assert key_fast != key_slow



###############################################################################
# Encryption / Decryption — Strings
###############################################################################


def test_encrypt_decrypt():

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "Hello Blockchain",
        "password123",
    )

    decrypted = manager.decrypt(
        encrypted,
        "password123",
    )

    assert decrypted == "Hello Blockchain"



def test_decrypt_returns_str_for_str_input():
    """
    When encrypt() receives a string, decrypt() must return a string.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "string_payload",
        "password",
    )

    decrypted = manager.decrypt(
        encrypted,
        "password",
    )

    assert isinstance(decrypted, str)
    assert decrypted == "string_payload"


###############################################################################
# Encryption / Decryption — Bytes
###############################################################################


def test_encrypt_decrypt_bytes():
    """
    Encrypt and decrypt raw bytes.
    """

    manager = EncryptionManager()

    original = b"\x00\x01\x02\xff\xfe"

    encrypted = manager.encrypt(
        original,
        "password",
    )

    decrypted = manager.decrypt(
        encrypted,
        "password",
    )

    assert decrypted == original



def test_decrypt_returns_bytes_for_bytes_input():
    """
    When encrypt() receives bytes, decrypt() must return bytes.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        b"bytes_payload",
        "password",
    )

    decrypted = manager.decrypt(
        encrypted,
        "password",
    )

    assert isinstance(decrypted, bytes)
    assert decrypted == b"bytes_payload"



def test_encrypt_rejects_invalid_data_type():
    """
    encrypt() must reject non-str, non-bytes input.
    """

    manager = EncryptionManager()

    with pytest.raises(WalletValidationError):
        manager.encrypt(
            12345,
            "password",
        )


###############################################################################
# Payload Metadata
###############################################################################


def test_payload_version_field():
    """
    Encrypted payload must contain a version field.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "data",
        "password",
    )

    assert "version" in encrypted
    assert encrypted["version"] == "2.1"



def test_payload_kdf_field():
    """
    Encrypted payload must record the KDF used.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "data",
        "password",
    )

    assert "kdf" in encrypted
    assert encrypted["kdf"] == "pbkdf2"



def test_payload_iterations_field():
    """
    Encrypted payload must record PBKDF2 iterations.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "data",
        "password",
        iterations=500000,
    )

    assert "iterations" in encrypted
    assert encrypted["iterations"] == 500000



def test_payload_data_encoding_field():
    """
    Encrypted payload must record whether original data was str or bytes.
    """

    manager = EncryptionManager()

    encrypted_str = manager.encrypt(
        "string_data",
        "password",
    )

    encrypted_bytes = manager.encrypt(
        b"bytes_data",
        "password",
    )

    assert encrypted_str["data_encoding"] == "utf-8"
    assert encrypted_bytes["data_encoding"] == "raw"


###############################################################################
# KDF Selection
###############################################################################


def test_unsupported_kdf():
    """
    encrypt() must reject unsupported KDF names.
    """

    manager = EncryptionManager()

    with pytest.raises(WalletValidationError):
        manager.encrypt(
            "data",
            "password",
            kdf="scrypt",
        )



def test_decrypt_unsupported_kdf():
    """
    decrypt() must reject payloads with unsupported KDF.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "data",
        "password",
    )

    encrypted["kdf"] = "unknown_kdf"

    with pytest.raises(WalletValidationError):
        manager.decrypt(
            encrypted,
            "password",
        )



@pytest.mark.skipif(
    not ARGON2_AVAILABLE,
    reason="argon2-cffi not installed",
)
def test_encrypt_decrypt_argon2id():
    """
    Roundtrip using Argon2id KDF.
    """

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "argon2id_payload",
        "password",
        kdf="argon2id",
    )

    assert encrypted["kdf"] == "argon2id"

    decrypted = manager.decrypt(
        encrypted,
        "password",
    )

    assert decrypted == "argon2id_payload"



@pytest.mark.skipif(
    ARGON2_AVAILABLE,
    reason="argon2-cffi is installed",
)
def test_argon2id_not_installed():
    """
    Argon2id methods must raise when package is missing.
    """

    manager = EncryptionManager()

    with pytest.raises(WalletValidationError):
        manager.derive_key_argon2id(
            "password",
            b"salt",
        )


###############################################################################
# Payload Validation
###############################################################################


def test_validate_payload():

    manager = EncryptionManager()

    encrypted = manager.encrypt(
        "Secret",
        "password",
    )

    assert manager.validate_payload(
        encrypted
    )



def test_invalid_payload():

    manager = EncryptionManager()

    with pytest.raises(
        WalletValidationError
    ):

        manager.validate_payload({})


###############################################################################
# Hashing
###############################################################################


def test_hash_generation():

    manager = EncryptionManager()

    digest = manager.generate_hash(
        "wallet"
    )

    assert len(digest) == 64



def test_hash_verification():

    manager = EncryptionManager()

    digest = manager.generate_hash(
        "wallet"
    )

    assert manager.verify_hash(
        "wallet",
        digest,
    )



def test_hash_verification_timing_safe():
    """
    verify_hash must use constant-time comparison.

    This test verifies functional correctness; the timing-safe
    property is ensured by hmac.compare_digest internally.
    """

    manager = EncryptionManager()

    digest = manager.generate_hash("secret")

    assert manager.verify_hash("secret", digest)
    assert not manager.verify_hash("wrong", digest)


###############################################################################
# Information
###############################################################################


def test_info():

    manager = EncryptionManager()

    info = manager.info()

    assert info["algorithm"] == "AES-256"
    assert info["kdf_primary"] == "PBKDF2-HMAC-SHA256"
    assert "kdf_alternative" in info


###############################################################################
# Representation
###############################################################################


def test_repr():

    manager = EncryptionManager()

    assert "AES-256" in repr(manager)



def test_str():

    manager = EncryptionManager()

    assert "wallet encryption" in str(manager).lower()