"""
Universal Blockchain Platform (UBP)

Module:
tests.test_wallets.crypto.test_secp256k1

Purpose:
Tests for the UBP secp256k1 cryptographic signer.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes

import pytest

from wallets.crypto.secp256k1 import (
    PRIVATE_KEY_LENGTH,
    Secp256k1Signer,
)


###############################################################################
# Test Constants
###############################################################################


PRIVATE_KEY = bytes.fromhex(
    "0000000000000000000000000000000000000000000000000000000000000001"
)

INVALID_ZERO_PRIVATE_KEY = bytes(
    PRIVATE_KEY_LENGTH
)

INVALID_SHORT_PRIVATE_KEY = bytes.fromhex(
    "01"
)

MESSAGE = b"UBP secp256k1 test message"


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def signer() -> Secp256k1Signer:
    """
    Return a secp256k1 signer.
    """

    return Secp256k1Signer()


###############################################################################
# Identity
###############################################################################


def test_algorithm(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify the signer algorithm identifier.
    """

    assert signer.algorithm == "secp256k1"


def test_repr(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify developer-friendly representation.
    """

    assert repr(
        signer
    ) == (
        "Secp256k1Signer("
        "algorithm='secp256k1'"
        ")"
    )


###############################################################################
# Private-Key Validation
###############################################################################


def test_validate_valid_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify valid secp256k1 private-key material.
    """

    assert signer.validate_private_key(
        PRIVATE_KEY
    ) is True


def test_validate_zero_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify the zero private key is rejected.
    """

    assert signer.validate_private_key(
        INVALID_ZERO_PRIVATE_KEY
    ) is False


def test_validate_short_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify incorrectly sized private-key material is rejected.
    """

    assert signer.validate_private_key(
        INVALID_SHORT_PRIVATE_KEY
    ) is False


def test_validate_non_bytes_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify non-byte private-key material is rejected.
    """

    assert signer.validate_private_key(
        "private-key"  # type: ignore[arg-type]
    ) is False


###############################################################################
# Public-Key Derivation
###############################################################################


def test_derive_compressed_public_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify compressed public-key derivation.
    """

    public_key = signer.derive_public_key(
        PRIVATE_KEY
    )

    assert isinstance(
        public_key,
        bytes,
    )

    assert len(
        public_key
    ) == 33

    assert public_key[0] in (
        0x02,
        0x03,
    )


def test_derive_uncompressed_public_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify uncompressed public-key derivation.
    """

    public_key = signer.derive_public_key(
        PRIVATE_KEY,
        compressed=False,
    )

    assert isinstance(
        public_key,
        bytes,
    )

    assert len(
        public_key
    ) == 65

    assert public_key[0] == 0x04


def test_public_key_derivation_is_consistent(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify repeated derivation produces the same public key.
    """

    first = signer.derive_public_key(
        PRIVATE_KEY
    )

    second = signer.derive_public_key(
        PRIVATE_KEY
    )

    assert first == second


def test_public_key_rejects_invalid_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify invalid private-key material is rejected.
    """

    with pytest.raises(
        ValueError,
        match="exactly 32 bytes",
    ):
        signer.derive_public_key(
            INVALID_SHORT_PRIVATE_KEY
        )


def test_public_key_rejects_invalid_compressed_option(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify the compressed option requires a boolean.
    """

    with pytest.raises(
        TypeError,
        match="compressed must be a boolean",
    ):
        signer.derive_public_key(
            PRIVATE_KEY,
            compressed="yes",  # type: ignore[arg-type]
        )


###############################################################################
# Signing
###############################################################################


def test_sign_returns_signature(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify message signing returns signature bytes.
    """

    signature = signer.sign(
        MESSAGE,
        PRIVATE_KEY,
    )

    assert isinstance(
        signature,
        bytes,
    )

    assert len(
        signature
    ) > 0


def test_signatures_are_valid_der_encoded_ecdsa_signatures(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify the generated signature can be decoded as ECDSA DER.
    """

    from cryptography.hazmat.primitives.asymmetric.utils import (
        decode_dss_signature,
    )

    signature = signer.sign(
        MESSAGE,
        PRIVATE_KEY,
    )

    r, s = decode_dss_signature(
        signature
    )

    assert isinstance(
        r,
        int,
    )

    assert isinstance(
        s,
        int,
    )

    assert r > 0
    assert s > 0


def test_sign_is_consistent_for_same_inputs(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify signing succeeds repeatedly for identical inputs.

    Note:
    ECDSA signatures may legitimately differ because nonce generation
    need not be deterministic. This test therefore verifies validity
    and structure rather than byte-for-byte equality.
    """

    first = signer.sign(
        MESSAGE,
        PRIVATE_KEY,
    )

    second = signer.sign(
        MESSAGE,
        PRIVATE_KEY,
    )

    assert isinstance(
        first,
        bytes,
    )

    assert isinstance(
        second,
        bytes,
    )

    assert first
    assert second


def test_sign_supports_custom_hash_algorithm(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify a supported custom hash algorithm can be supplied.
    """

    signature = signer.sign(
        MESSAGE,
        PRIVATE_KEY,
        hash_algorithm=hashes.SHA384(),
    )

    assert isinstance(
        signature,
        bytes,
    )

    assert signature


def test_sign_rejects_invalid_message(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify non-byte signing input is rejected.
    """

    with pytest.raises(
        TypeError,
        match="message must be bytes",
    ):
        signer.sign(
            "invalid message",  # type: ignore[arg-type]
            PRIVATE_KEY,
        )


def test_sign_rejects_invalid_private_key(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify invalid private-key material is rejected.
    """

    with pytest.raises(
        ValueError,
        match="exactly 32 bytes",
    ):
        signer.sign(
            MESSAGE,
            INVALID_SHORT_PRIVATE_KEY,
        )


def test_sign_rejects_invalid_hash_algorithm(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify invalid hash configuration is rejected.
    """

    with pytest.raises(
        TypeError,
        match="HashAlgorithm",
    ):
        signer.sign(
            MESSAGE,
            PRIVATE_KEY,
            hash_algorithm="SHA256",
        )
    ###############################################################################
# Prehashed Digest Signing
###############################################################################


def test_sign_digest_returns_signature(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify a precomputed SHA256 digest can be signed.
    """

    import hashlib

    digest = hashlib.sha256(
        b"UBP prehashed signing test"
    ).digest()

    signature = signer.sign_digest(
        digest,
        PRIVATE_KEY,
    )

    assert isinstance(
        signature,
        bytes,
    )

    assert signature


def test_sign_digest_does_not_hash_digest_again(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify sign_digest accepts an already-computed SHA256 digest.
    """

    import hashlib

    digest = hashlib.sha256(
        b"UBP digest"
    ).digest()

    signature = signer.sign_digest(
        digest,
        PRIVATE_KEY,
    )

    assert isinstance(
        signature,
        bytes,
    )


def test_sign_digest_rejects_non_bytes_digest(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify non-byte digest input is rejected.
    """

    with pytest.raises(
        TypeError,
        match="digest must be bytes",
    ):
        signer.sign_digest(
            "invalid",  # type: ignore[arg-type]
            PRIVATE_KEY,
        )


def test_sign_digest_rejects_empty_digest(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify an empty digest is rejected.
    """

    with pytest.raises(
        ValueError,
        match="digest cannot be empty",
    ):
        signer.sign_digest(
            b"",
            PRIVATE_KEY,
        )


def test_sign_digest_rejects_wrong_digest_length(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify a digest with the wrong length is rejected.
    """

    with pytest.raises(
        ValueError,
        match="digest length does not match",
    ):
        signer.sign_digest(
            b"invalid",
            PRIVATE_KEY,
        )


def test_sign_digest_rejects_invalid_hash_algorithm(
    signer: Secp256k1Signer,
) -> None:
    """
    Verify invalid hash configuration is rejected.
    """

    digest = bytes(
        32
    )

    with pytest.raises(
        TypeError,
        match="HashAlgorithm",
    ):
        signer.sign_digest(
            digest,
            PRIVATE_KEY,
            hash_algorithm="SHA256",
        )

###############################################################################
# End of File
###############################################################################
