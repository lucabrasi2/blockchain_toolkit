"""
Universal Blockchain Platform (UBP)

Module:
tests.test_wallets.blockchain.bitcoin.test_signer

Purpose:
Tests for the Bitcoin transaction signing adapter.

Supported scope:
    - Legacy Bitcoin P2PKH
    - SIGHASH_ALL

These tests intentionally exercise the Bitcoin signing layer
independently from BitcoinWallet and BitcoinProvider.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)
"""

from __future__ import annotations

import hashlib

import pytest

from wallets.blockchain.bitcoin.signer import (
    BitcoinTransactionSigner,
    SIGHASH_ALL,
)


###############################################################################
# Constants
###############################################################################


PRIVATE_KEY = bytes.fromhex(
    "0000000000000000000000000000000000000000000000000000000000000001"
)

P2PKH_SCRIPT_PUBKEY = (
    "76a914"
    "0000000000000000000000000000000000000001"
    "88ac"
)

TRANSACTION_HEX = (
    "01000000"
    "01"
    "1111111111111111111111111111111111111111111111111111111111111111"
    "00000000"
    "00"
    "ffffffff"
    "01"
    "1027000000000000"
    "19"
    "76a914"
    "0000000000000000000000000000000000000001"
    "88ac"
    "00000000"
)

PREVIOUS_TXID = (
    "1111111111111111111111111111111111111111111111111111111111111111"
)

PREVIOUS_OUTPUTS = {
    (
        PREVIOUS_TXID,
        0,
    ): {
        "scriptPubKey": {
            "hex": P2PKH_SCRIPT_PUBKEY,
        },
        "value": 0.001,
    }
}


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def signer() -> BitcoinTransactionSigner:
    """
    Return a Bitcoin transaction signer.
    """

    return BitcoinTransactionSigner()


###############################################################################
# Identity
###############################################################################


def test_blockchain_identifier(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the blockchain identifier.
    """

    assert signer.blockchain == "bitcoin"


def test_transaction_type(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the supported transaction type.
    """

    assert signer.transaction_type == "p2pkh"


###############################################################################
# Transaction Validation
###############################################################################


def test_sign_rejects_non_string_transaction(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify non-string transaction input is rejected.
    """

    with pytest.raises(
        TypeError,
        match="transaction must be a hexadecimal string",
    ):
        signer.sign(
            b"invalid",  # type: ignore[arg-type]
            PRIVATE_KEY,
            PREVIOUS_OUTPUTS,
        )


def test_sign_rejects_empty_transaction(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify an empty transaction is rejected.
    """

    with pytest.raises(
        ValueError,
        match="transaction cannot be empty",
    ):
        signer.sign(
            "",
            PRIVATE_KEY,
            PREVIOUS_OUTPUTS,
        )


def test_sign_rejects_invalid_hex(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify invalid transaction hexadecimal is rejected.
    """

    with pytest.raises(
        ValueError,
        match="valid hexadecimal",
    ):
        signer.sign(
            "not-hex",
            PRIVATE_KEY,
            PREVIOUS_OUTPUTS,
        )


def test_sign_rejects_invalid_previous_outputs(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify previous-output metadata must be a dictionary.
    """

    with pytest.raises(
        TypeError,
        match="previous_outputs must be a dictionary",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            None,  # type: ignore[arg-type]
        )


###############################################################################
# Previous Output Resolution
###############################################################################


def test_missing_previous_output_is_rejected(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify every transaction input requires previous-output data.
    """

    with pytest.raises(
        ValueError,
        match="Missing previous-output information",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            {},
        )


def test_invalid_previous_output_record_is_rejected(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify previous-output records must be dictionaries.
    """

    previous_outputs = {
        (
            PREVIOUS_TXID,
            0,
        ): "invalid",
    }

    with pytest.raises(
        TypeError,
        match="Previous-output information must be a dictionary",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            previous_outputs,  # type: ignore[arg-type]
        )


def test_missing_script_pubkey_is_rejected(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify scriptPubKey is required.
    """

    previous_outputs = {
        (
            PREVIOUS_TXID,
            0,
        ): {
            "value": 0.001,
        }
    }

    with pytest.raises(
        ValueError,
        match="missing scriptPubKey",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            previous_outputs,
        )


def test_invalid_script_pubkey_is_rejected(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify malformed scriptPubKey data is rejected.
    """

    previous_outputs = {
        (
            PREVIOUS_TXID,
            0,
        ): {
            "scriptPubKey": {
                "hex": "invalid",
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="not valid hexadecimal",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            previous_outputs,
        )


###############################################################################
# P2PKH Validation
###############################################################################


def test_p2pkh_script_is_recognized(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify a standard P2PKH script is recognized.
    """

    assert signer._is_p2pkh_script(
        bytes.fromhex(
            P2PKH_SCRIPT_PUBKEY
        )
    ) is True


def test_non_p2pkh_script_is_rejected(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify unsupported script types are rejected.
    """

    previous_outputs = {
        (
            PREVIOUS_TXID,
            0,
        ): {
            "scriptPubKey": {
                "hex": "00140000000000000000000000000000000000000000",
            }
        }
    }

    with pytest.raises(
        ValueError,
        match="supports only P2PKH",
    ):
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            previous_outputs,
        )


###############################################################################
# Transaction Signing
###############################################################################


def test_sign_returns_hexadecimal_transaction(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify signing returns serialized hexadecimal data.
    """

    signed = signer.sign(
        TRANSACTION_HEX,
        PRIVATE_KEY,
        PREVIOUS_OUTPUTS,
    )

    assert isinstance(
        signed,
        str,
    )

    assert signed

    bytes.fromhex(
        signed
    )


def test_signed_transaction_is_larger_than_unsigned_transaction(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the resulting transaction contains signature data.
    """

    signed = signer.sign(
        TRANSACTION_HEX,
        PRIVATE_KEY,
        PREVIOUS_OUTPUTS,
    )

    assert len(
        signed
    ) > len(
        TRANSACTION_HEX
    )


def test_signed_transaction_contains_script_sig(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the transaction contains a non-empty scriptSig.
    """

    signed = bytes.fromhex(
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            PREVIOUS_OUTPUTS,
        )
    )

    # Version
    offset = 4

    # One input
    assert signed[offset] == 1
    offset += 1

    # Previous transaction hash
    offset += 32

    # vout
    offset += 4

    script_length = signed[offset]
    offset += 1

    assert script_length > 0

    script_sig = signed[
        offset:offset + script_length
    ]

    assert len(
        script_sig
    ) == script_length

    assert script_sig


def test_signature_contains_sighash_all(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the generated scriptSig contains SIGHASH_ALL.
    """

    signed = bytes.fromhex(
        signer.sign(
            TRANSACTION_HEX,
            PRIVATE_KEY,
            PREVIOUS_OUTPUTS,
        )
    )

    offset = 4

    input_count = signed[offset]
    assert input_count == 1

    offset += 1
    offset += 32
    offset += 4

    script_length = signed[offset]
    offset += 1

    script_sig = signed[
        offset:offset + script_length
    ]

    assert SIGHASH_ALL in script_sig


###############################################################################
# Transaction Integrity
###############################################################################


def test_signing_does_not_modify_input_transaction(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify the original transaction string is unchanged.
    """

    original = TRANSACTION_HEX

    signer.sign(
        original,
        PRIVATE_KEY,
        PREVIOUS_OUTPUTS,
    )

    assert original == TRANSACTION_HEX


def test_signing_is_repeatable(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify repeated signing produces valid serialized transactions.

    ECDSA signatures may legitimately differ because the signing nonce
    need not be deterministic, so byte-for-byte equality is not required.
    """

    first = signer.sign(
        TRANSACTION_HEX,
        PRIVATE_KEY,
        PREVIOUS_OUTPUTS,
    )

    second = signer.sign(
        TRANSACTION_HEX,
        PRIVATE_KEY,
        PREVIOUS_OUTPUTS,
    )

    assert first
    assert second

    bytes.fromhex(
        first
    )

    bytes.fromhex(
        second
    )


###############################################################################
# Signature Hash
###############################################################################


def test_double_sha256_returns_32_bytes(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify Bitcoin double-SHA256 produces a 32-byte digest.
    """

    digest = signer._double_sha256(
        b"UBP"
    )

    assert isinstance(
        digest,
        bytes,
    )

    assert len(
        digest
    ) == 32


def test_signature_hash_is_32_bytes(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify legacy SIGHASH_ALL construction produces a 32-byte digest.
    """

    raw = bytes.fromhex(
        TRANSACTION_HEX
    )

    parsed = signer._parse_transaction(
        raw
    )

    digest = signer._create_signature_hash(
        parsed,
        0,
        bytes.fromhex(
            P2PKH_SCRIPT_PUBKEY
        ),
    )

    assert isinstance(
        digest,
        bytes,
    )

    assert len(
        digest
    ) == 32


###############################################################################
# Serialization
###############################################################################


def test_parse_and_serialize_round_trip(
    signer: BitcoinTransactionSigner,
) -> None:
    """
    Verify unsigned transaction parsing and serialization are reversible.
    """

    raw = bytes.fromhex(
        TRANSACTION_HEX
    )

    parsed = signer._parse_transaction(
        raw
    )

    serialized = signer._serialize_transaction(
        parsed
    )

    assert serialized == raw


###############################################################################
# End of File
###############################################################################
