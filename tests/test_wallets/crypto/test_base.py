"""
Universal Blockchain Platform (UBP)

Module:
tests.test_wallets.crypto.test_base

Purpose:
Tests for the abstract CryptoSigner interface.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)
"""

from __future__ import annotations

import pytest

from wallets.crypto.base import CryptoSigner


###############################################################################
# Test Implementation
###############################################################################


class DummyCryptoSigner(CryptoSigner):
    """
    Minimal concrete implementation used to test CryptoSigner.
    """

    @property
    def algorithm(
        self,
    ) -> str:
        return "TEST_ALGORITHM"

    def sign(
        self,
        message: bytes,
        private_key: bytes,
        **options: object,
    ) -> bytes:
        return b"TEST_SIGNATURE"

    def sign_digest(
        self,
        digest: bytes,
        private_key: bytes,
        **options: object,
    ) -> bytes:
        return b"TEST_DIGEST_SIGNATURE"

    def derive_public_key(
        self,
        private_key: bytes,
        **options: object,
    ) -> bytes:
        return b"TEST_PUBLIC_KEY"

    def validate_private_key(
        self,
        private_key: bytes,
    ) -> bool:
        return True


###############################################################################
# Tests
###############################################################################


def test_crypto_signer_is_abstract() -> None:
    """
    Verify CryptoSigner cannot be instantiated directly.
    """

    with pytest.raises(
        TypeError
    ):
        CryptoSigner()


def test_algorithm_property() -> None:
    """
    Verify concrete implementations expose their algorithm.
    """

    signer = DummyCryptoSigner()

    assert signer.algorithm == "TEST_ALGORITHM"


def test_sign_method() -> None:
    """
    Verify the signing interface can be implemented.
    """

    signer = DummyCryptoSigner()

    result = signer.sign(
        b"message",
        b"private-key",
    )

    assert result == b"TEST_SIGNATURE"


def test_sign_accepts_options() -> None:
    """
    Verify signing options can be forwarded.
    """

    signer = DummyCryptoSigner()

    result = signer.sign(
        b"message",
        b"private-key",
        encoding="test",
    )

    assert result == b"TEST_SIGNATURE"


def test_sign_digest_method() -> None:
    """
    Verify the prehashed digest signing interface can be implemented.
    """

    signer = DummyCryptoSigner()

    result = signer.sign_digest(
        b"digest",
        b"private-key",
    )

    assert result == b"TEST_DIGEST_SIGNATURE"


def test_sign_digest_accepts_options() -> None:
    """
    Verify digest signing options can be forwarded.
    """

    signer = DummyCryptoSigner()

    result = signer.sign_digest(
        b"digest",
        b"private-key",
        hash_algorithm="test",
    )

    assert result == b"TEST_DIGEST_SIGNATURE"


def test_derive_public_key() -> None:
    """
    Verify public-key derivation can be implemented.
    """

    signer = DummyCryptoSigner()

    result = signer.derive_public_key(
        b"private-key"
    )

    assert result == b"TEST_PUBLIC_KEY"


def test_validate_private_key() -> None:
    """
    Verify private-key validation can be implemented.
    """

    signer = DummyCryptoSigner()

    assert signer.validate_private_key(
        b"private-key"
    ) is True


def test_repr() -> None:
    """
    Verify developer-friendly representation.
    """

    signer = DummyCryptoSigner()

    result = repr(
        signer
    )

    assert result == (
        "DummyCryptoSigner("
        "algorithm='TEST_ALGORITHM'"
        ")"
    )


###############################################################################
# End of File
###############################################################################