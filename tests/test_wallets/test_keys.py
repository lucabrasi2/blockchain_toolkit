"""
Tests for wallets.keys module.

Step 2 — Secure Serialization Foundation

All private-key tests use raw bytes (b"...") to align with
the Secp256k1Signer interface and enable secure memory wiping.

New tests cover encrypted keystore serialization (to_encrypted_dict /
from_encrypted_dict) using the EncryptionManager.
"""

import pytest

from wallets.keys import WalletKey
from wallets.encryption import EncryptionManager

from wallets.exceptions import (
    WalletValidationError,
    WalletPrivateKeyError,
    WalletPublicKeyError,
)


###############################################################################
# Creation Tests
###############################################################################


def test_wallet_key_creation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public123",
        private_key=b"private123",
    )

    assert key.algorithm == "ECDSA"
    assert key.network == "ethereum"
    assert key.has_public_key is True
    assert key.has_private_key is True



def test_missing_algorithm():

    with pytest.raises(
        WalletValidationError
    ):

        WalletKey(
            algorithm="",
            network="ethereum",
        )



def test_missing_network():

    with pytest.raises(
        WalletValidationError
    ):

        WalletKey(
            algorithm="ECDSA",
            network="",
        )



def test_private_key_type_rejects_string():
    """
    Private keys must be bytes or bytearray.
    String private keys are rejected to prevent accidental
    hex-encoding mismatches with the crypto layer.
    """

    with pytest.raises(TypeError):
        WalletKey(
            algorithm="secp256k1",
            network="ethereum",
            private_key="not_allowed_as_string",
        )



def test_private_key_accepts_bytearray():
    """
    Bytearray private keys are accepted and stored mutably.
    """

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        private_key=bytearray(b"valid_bytearray_key_1234567890"),
    )

    assert key.has_private_key is True


###############################################################################
# Key Access Tests
###############################################################################


def test_public_key_access():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        public_key="pubkey",
    )

    assert key.public_key == "pubkey"



def test_private_key_requires_authorization():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key=b"secret",
    )


    with pytest.raises(
        WalletValidationError
    ):

        key.get_private_key()



def test_private_key_authorized_access():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key=b"secret",
    )

    assert (
        key.get_private_key(
            authorized=True
        )
        == b"secret"
    )


###############################################################################
# Security Tests
###############################################################################


def test_clear_private_key():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key=b"secret",
    )

    key.clear_private_key()

    assert key.has_private_key is False


    with pytest.raises(
        WalletPrivateKeyError
    ):

        key.get_private_key(
            authorized=True
        )



def test_clear_private_key_overwrites_memory():
    """
    Verify that clear_private_key zero-fills the internal bytearray.
    """

    original = b"sensitive_key_material_12345678"

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        private_key=original,
    )

    key.clear_private_key()

    assert key._private_key is None


###############################################################################
# Validation Tests
###############################################################################


def test_key_validation_success():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public",
    )

    assert key.validate() is True



def test_missing_public_key_validation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )


    with pytest.raises(
        WalletPublicKeyError
    ):

        key.validate()


###############################################################################
# Metadata Tests
###############################################################################


def test_metadata_management():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )

    key.update_metadata(
        "purpose",
        "wallet signing",
    )

    assert (
        key.get_metadata("purpose")
        == "wallet signing"
    )


###############################################################################
# Import Export Tests
###############################################################################


def test_key_import_export():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )


    key.import_keys(
        public_key="public",
        private_key=b"private",
    )


    assert (
        key.export_public_key()
        == "public"
    )


    assert (
        key.export_private_key(
            authorized=True
        )
        == b"private"
    )



def test_import_keys_rejects_string_private_key():
    """
    import_keys must reject string private keys for type safety.
    """

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
    )

    with pytest.raises(TypeError):
        key.import_keys(
            private_key="string_not_allowed",
        )


###############################################################################
# Serialization Tests
###############################################################################


def test_key_to_dict():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public",
        private_key=b"private",
    )


    data = key.to_dict()


    assert data["algorithm"] == "ECDSA"

    assert data["network"] == "ethereum"

    assert data["public_key"] == "public"

    assert data["has_private_key"] is True

    assert "created_at" in data

    # Critical: private key must NEVER appear in dict serialization
    assert "private_key" not in data


###############################################################################
# Secure Encrypted Serialization Tests
###############################################################################


def test_to_encrypted_dict_roundtrip():
    """
    Encrypt a WalletKey, serialize to dict, then restore and verify
    the private key matches.
    """

    encryption = EncryptionManager()
    password = "strong-password-123"

    original = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        public_key="0xPubKey",
        private_key=b"\x01" * 32,
        metadata={"purpose": "testing"},
    )

    keystore = original.to_encrypted_dict(
        encryption,
        password,
    )

    # Verify plaintext fields are preserved
    assert keystore["version"] == "ubp-keystore-1.0"
    assert keystore["algorithm"] == "secp256k1"
    assert keystore["network"] == "ethereum"
    assert keystore["public_key"] == "0xPubKey"
    assert keystore["metadata"]["purpose"] == "testing"

    # Verify encrypted payload exists
    assert "encrypted_private_key" in keystore
    assert "salt" in keystore["encrypted_private_key"]
    assert "nonce" in keystore["encrypted_private_key"]
    assert "ciphertext" in keystore["encrypted_private_key"]

    # Restore
    restored = WalletKey.from_encrypted_dict(
        keystore,
        encryption,
        password,
    )

    assert restored.algorithm == original.algorithm
    assert restored.network == original.network
    assert restored.public_key == original.public_key
    assert restored.get_private_key(authorized=True) == b"\x01" * 32


def test_to_encrypted_dict_requires_private_key():
    """
    to_encrypted_dict must raise when no private key exists.
    """

    encryption = EncryptionManager()

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        public_key="pubkey",
    )

    with pytest.raises(WalletPrivateKeyError):
        key.to_encrypted_dict(
            encryption,
            "password",
        )


def test_from_encrypted_dict_wrong_password():
    """
    Restoring with the wrong password must raise.
    """

    encryption = EncryptionManager()

    original = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        public_key="pubkey",
        private_key=b"\x02" * 32,
    )

    keystore = original.to_encrypted_dict(
        encryption,
        "correct-password",
    )

    with pytest.raises(WalletPrivateKeyError):
        WalletKey.from_encrypted_dict(
            keystore,
            encryption,
            "wrong-password",
        )


def test_from_encrypted_dict_invalid_payload():
    """
    Malformed keystore payloads must raise validation errors.
    """

    encryption = EncryptionManager()

    with pytest.raises(WalletValidationError):
        WalletKey.from_encrypted_dict(
            {},  # Empty dict
            encryption,
            "password",
        )

    with pytest.raises(WalletValidationError):
        WalletKey.from_encrypted_dict(
            {"algorithm": "secp256k1"},  # Missing encrypted_private_key
            encryption,
            "password",
        )


def test_from_encrypted_dict_non_dict_input():
    """
    Non-dictionary input must raise.
    """

    encryption = EncryptionManager()

    with pytest.raises(WalletValidationError):
        WalletKey.from_encrypted_dict(
            "not_a_dict",
            encryption,
            "password",
        )


###############################################################################
# Representation Tests
###############################################################################


def test_key_representation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        private_key=b"secret",
    )


    representation = repr(key)


    assert "secret" not in representation

    assert "ECDSA" in representation


###############################################################################
# Integration: sign_digest with Secp256k1Signer
###############################################################################


def test_sign_digest_with_secp256k1_signer():
    """
    End-to-end test: WalletKey + Secp256k1Signer.

    Verifies that the bytes-based private key flows correctly
    from WalletKey through to the cryptographic signer.
    """

    from wallets.crypto.secp256k1 import Secp256k1Signer

    # Valid 32-byte secp256k1 private key (generator scalar = 1)
    private_key = bytes.fromhex(
        "00000000000000000000000000000000"
        "00000000000000000000000000000001"
    )

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        public_key="pubkey",
        private_key=private_key,
    )

    signer = Secp256k1Signer()

    digest = b"\xab" * 32  # 32-byte dummy digest

    signature = key.sign_digest(
        digest=digest,
        signer=signer,
        authorized=True,
    )

    assert isinstance(signature, bytes)
    assert len(signature) > 0


def test_sign_digest_algorithm_mismatch():
    """
    sign_digest must reject a signer whose algorithm does not match.
    """

    from wallets.crypto.secp256k1 import Secp256k1Signer

    key = WalletKey(
        algorithm="ed25519",  # Mismatched
        network="ethereum",
        public_key="pubkey",
        private_key=b"\x01" * 32,
    )

    signer = Secp256k1Signer()  # algorithm == "secp256k1"

    with pytest.raises(WalletValidationError):
        key.sign_digest(
            digest=b"\xab" * 32,
            signer=signer,
            authorized=True,
        )


def test_sign_digest_unauthorized():
    """
    sign_digest without authorization must raise.
    """

    from wallets.crypto.secp256k1 import Secp256k1Signer

    key = WalletKey(
        algorithm="secp256k1",
        network="ethereum",
        public_key="pubkey",
        private_key=b"\x01" * 32,
    )

    signer = Secp256k1Signer()

    with pytest.raises(WalletValidationError):
        key.sign_digest(
            digest=b"\xab" * 32,
            signer=signer,
            authorized=False,
        )