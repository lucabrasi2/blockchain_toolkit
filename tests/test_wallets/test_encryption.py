"""
Tests for wallets.encryption module.
"""

import pytest

from wallets.encryption import EncryptionManager
from wallets.exceptions import (
    WalletEncryptionError,
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



###############################################################################
# Encryption / Decryption
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



###############################################################################
# Information
###############################################################################


def test_info():

    manager = EncryptionManager()

    info = manager.info()

    assert info["algorithm"] == "AES-256"



###############################################################################
# Representation
###############################################################################


def test_repr():

    manager = EncryptionManager()

    assert "AES-256" in repr(manager)



def test_str():

    manager = EncryptionManager()

    assert "wallet encryption" in str(manager).lower()
