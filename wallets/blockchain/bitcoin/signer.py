"""
Universal Blockchain Platform (UBP)

Module:
wallets.blockchain.bitcoin.signer

Purpose:
Bitcoin-specific transaction signing adapter.

Supported transaction type:
    - Legacy P2PKH
    - SIGHASH_ALL

Architecture:

    BitcoinWallet
          |
          v
    BitcoinTransactionSigner
          |
          +---- Bitcoin transaction rules
          |
          +---- Signature-hash construction
          |
          +---- ScriptSig construction
          |
          v
      Secp256k1Signer
          |
          v
      cryptography

This module does not:
    - store private keys;
    - manage wallet custody;
    - communicate directly with Bitcoin nodes;
    - broadcast transactions;
    - implement generic cryptography.

BitcoinProvider remains responsible for blockchain/RPC
communication, while Secp256k1Signer remains responsible
for low-level elliptic-curve signing.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.1 Enterprise
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

from wallets.crypto.secp256k1 import (
    Secp256k1Signer,
)


###############################################################################
# Constants
###############################################################################


SIGHASH_ALL = 0x01

SECP256K1_ORDER = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    16,
)


###############################################################################
# Internal Transaction Models
###############################################################################


@dataclass
class BitcoinInput:
    """
    Internal representation of a Bitcoin transaction input.
    """

    txid: bytes
    vout: int
    script_sig: bytes
    sequence: int


@dataclass
class BitcoinOutput:
    """
    Internal representation of a Bitcoin transaction output.
    """

    value: int
    script_pubkey: bytes


@dataclass
class BitcoinTransaction:
    """
    Internal representation of a legacy Bitcoin transaction.
    """

    version: int
    inputs: list[BitcoinInput]
    outputs: list[BitcoinOutput]
    locktime: int


###############################################################################
# Bitcoin Transaction Signer
###############################################################################


class BitcoinTransactionSigner:
    """
    Bitcoin-specific transaction signing adapter.

    The signer currently supports legacy P2PKH transactions using
    SIGHASH_ALL.

    Private-key material is accepted only for the duration of the
    signing operation and is not retained by this object.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        crypto_signer: Secp256k1Signer | None = None,
    ) -> None:
        """
        Initialize the Bitcoin transaction signer.

        Parameters
        ----------
        crypto_signer:
            Optional low-level secp256k1 signer.

        Notes
        -----
        A signer may be injected during testing or by a higher-level
        application.
        """

        self._crypto_signer = (
            crypto_signer
            if crypto_signer is not None
            else Secp256k1Signer()
        )

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def blockchain(
        self,
    ) -> str:
        """
        Return the blockchain identifier.
        """

        return "bitcoin"

    @property
    def transaction_type(
        self,
    ) -> str:
        """
        Return the currently supported transaction type.
        """

        return "p2pkh"

    ###########################################################################
    # Signing
    ###########################################################################

    def sign(
        self,
        transaction: str,
        private_key: bytes,
        previous_outputs: dict[
            tuple[str, int],
            dict[str, Any],
        ],
    ) -> str:
        """
        Sign a legacy Bitcoin P2PKH transaction.

        Parameters
        ----------
        transaction:
            Unsigned or partially signed Bitcoin transaction
            serialized as hexadecimal.

        private_key:
            32-byte secp256k1 private key.

        previous_outputs:
            Mapping of:

                (transaction_id, output_index)

            to previous-output information.

            Each record must contain:

                scriptPubKey.hex

            or:

                script_pubkey

            containing the previous output's locking script
            in hexadecimal form.

        Returns
        -------
        str
            Fully serialized signed transaction in hexadecimal.

        Raises
        ------
        TypeError
            If an argument has an invalid type.

        ValueError
            If the transaction or previous-output data is invalid.

        Notes
        -----
        This implementation supports legacy P2PKH SIGHASH_ALL.

        SegWit and Taproot signing are intentionally not handled
        by this adapter yet.
        """

        raw_transaction = self._validate_transaction_hex(
            transaction
        )

        if not isinstance(
            previous_outputs,
            dict,
        ):
            raise TypeError(
                "previous_outputs must be a dictionary."
            )

        parsed = self._parse_transaction(
            raw_transaction
        )

        public_key = (
            self._crypto_signer.derive_public_key(
                private_key,
                compressed=True,
            )
        )

        for index, transaction_input in enumerate(
            parsed.inputs
        ):
            previous_output = self._get_previous_output(
                transaction_input,
                previous_outputs,
            )

            script_pubkey = (
                self._extract_script_pubkey(
                    previous_output
                )
            )

            if not self._is_p2pkh_script(
                script_pubkey
            ):
                raise ValueError(
                    "BitcoinTransactionSigner currently "
                    "supports only P2PKH previous outputs."
                )

            signature_hash = (
                self._create_signature_hash(
                    parsed,
                    index,
                    script_pubkey,
                )
            )

            signature = self._sign_digest(
                signature_hash,
                private_key,
            )

            transaction_input.script_sig = (
                self._build_p2pkh_script_sig(
                    signature,
                    public_key,
                )
            )

        return self._serialize_transaction(
            parsed
        ).hex()

    ###########################################################################
    # Transaction Parsing
    ###########################################################################

    def _parse_transaction(
        self,
        raw_transaction: bytes,
    ) -> BitcoinTransaction:
        """
        Parse a legacy Bitcoin transaction.
        """

        offset = 0

        version, offset = self._read_uint32_le(
            raw_transaction,
            offset,
        )

        input_count, offset = self._read_varint(
            raw_transaction,
            offset,
        )

        if input_count == 0:
            raise ValueError(
                "Bitcoin transaction must contain at least one input."
            )

        inputs: list[BitcoinInput] = []

        for _ in range(input_count):
            txid, offset = self._read_bytes(
                raw_transaction,
                offset,
                32,
            )

            vout, offset = self._read_uint32_le(
                raw_transaction,
                offset,
            )

            script_length, offset = self._read_varint(
                raw_transaction,
                offset,
            )

            script_sig, offset = self._read_bytes(
                raw_transaction,
                offset,
                script_length,
            )

            sequence, offset = self._read_uint32_le(
                raw_transaction,
                offset,
            )

            inputs.append(
                BitcoinInput(
                    txid=txid,
                    vout=vout,
                    script_sig=script_sig,
                    sequence=sequence,
                )
            )

        output_count, offset = self._read_varint(
            raw_transaction,
            offset,
        )

        if output_count == 0:
            raise ValueError(
                "Bitcoin transaction must contain at least one output."
            )

        outputs: list[BitcoinOutput] = []

        for _ in range(output_count):
            value, offset = self._read_uint64_le(
                raw_transaction,
                offset,
            )

            script_length, offset = self._read_varint(
                raw_transaction,
                offset,
            )

            script_pubkey, offset = self._read_bytes(
                raw_transaction,
                offset,
                script_length,
            )

            outputs.append(
                BitcoinOutput(
                    value=value,
                    script_pubkey=script_pubkey,
                )
            )

        locktime, offset = self._read_uint32_le(
            raw_transaction,
            offset,
        )

        if offset != len(raw_transaction):
            raise ValueError(
                "Bitcoin transaction contains trailing data."
            )

        return BitcoinTransaction(
            version=version,
            inputs=inputs,
            outputs=outputs,
            locktime=locktime,
        )

    ###########################################################################
    # Signature Hash
    ###########################################################################

    def _create_signature_hash(
        self,
        transaction: BitcoinTransaction,
        input_index: int,
        script_pubkey: bytes,
    ) -> bytes:
        """
        Construct the legacy Bitcoin SIGHASH_ALL digest.
        """

        if not isinstance(
            input_index,
            int,
        ):
            raise TypeError(
                "input_index must be an integer."
            )

        if input_index < 0 or input_index >= len(
            transaction.inputs
        ):
            raise IndexError(
                "Bitcoin transaction input index is out of range."
            )

        signing_transaction = BitcoinTransaction(
            version=transaction.version,
            inputs=[
                BitcoinInput(
                    txid=tx_input.txid,
                    vout=tx_input.vout,
                    script_sig=(
                        script_pubkey
                        if index == input_index
                        else b""
                    ),
                    sequence=tx_input.sequence,
                )
                for index, tx_input in enumerate(
                    transaction.inputs
                )
            ],
            outputs=[
                BitcoinOutput(
                    value=output.value,
                    script_pubkey=output.script_pubkey,
                )
                for output in transaction.outputs
            ],
            locktime=transaction.locktime,
        )

        serialized = self._serialize_transaction(
            signing_transaction
        )

        serialized += SIGHASH_ALL.to_bytes(
            4,
            byteorder="little",
        )

        return self._double_sha256(
            serialized
        )

    ###########################################################################
    # Low-Level Signature
    ###########################################################################

    def _sign_digest(
        self,
        digest: bytes,
        private_key: bytes,
    ) -> bytes:
        """
        Sign a Bitcoin signature digest.

        Bitcoin-specific digest construction remains in this adapter.

        The actual secp256k1 signing operation is delegated to
        Secp256k1Signer.sign_digest().

        The resulting DER signature is normalized to low-S and
        then receives the Bitcoin SIGHASH_ALL byte.
        """

        if not isinstance(
            digest,
            bytes,
        ):
            raise TypeError(
                "digest must be bytes."
            )

        if len(digest) != 32:
            raise ValueError(
                "Bitcoin signature digest must be 32 bytes."
            )

        if not self._crypto_signer.validate_private_key(
            private_key
        ):
            raise ValueError(
                "Invalid secp256k1 private key."
            )

        signature = self._crypto_signer.sign_digest(
            digest,
            private_key,
        )

        r, s = decode_dss_signature(
            signature
        )

        if s > (
            SECP256K1_ORDER // 2
        ):
            s = (
                SECP256K1_ORDER
                - s
            )

        normalized_signature = encode_dss_signature(
            r,
            s,
        )

        return (
            normalized_signature
            + bytes(
                [SIGHASH_ALL]
            )
        )

    ###########################################################################
    # P2PKH Script Construction
    ###########################################################################

    @staticmethod
    def _build_p2pkh_script_sig(
        signature: bytes,
        public_key: bytes,
    ) -> bytes:
        """
        Construct a legacy P2PKH scriptSig.
        """

        if len(signature) > 75:
            raise ValueError(
                "Signature is too large for a direct PUSHDATA operation."
            )

        if len(public_key) > 75:
            raise ValueError(
                "Public key is too large for a direct PUSHDATA operation."
            )

        return (
            bytes([len(signature)])
            + signature
            + bytes([len(public_key)])
            + public_key
        )

    @staticmethod
    def _is_p2pkh_script(
        script_pubkey: bytes,
    ) -> bool:
        """
        Determine whether a script is a standard P2PKH script.
        """

        return (
            len(script_pubkey) == 25
            and script_pubkey[0] == 0x76
            and script_pubkey[1] == 0xA9
            and script_pubkey[2] == 0x14
            and script_pubkey[23] == 0x88
            and script_pubkey[24] == 0xAC
        )

    ###########################################################################
    # Previous Output Handling
    ###########################################################################

    @staticmethod
    def _get_previous_output(
        transaction_input: BitcoinInput,
        previous_outputs: dict[
            tuple[str, int],
            dict[str, Any],
        ],
    ) -> dict[str, Any]:
        """
        Retrieve previous-output metadata for an input.
        """

        transaction_id = (
            transaction_input.txid[::-1].hex()
        )

        key = (
            transaction_id,
            transaction_input.vout,
        )

        previous_output = previous_outputs.get(
            key
        )

        if previous_output is None:
            raise ValueError(
                "Missing previous-output information for "
                f"{transaction_id}:{transaction_input.vout}."
            )

        if not isinstance(
            previous_output,
            dict,
        ):
            raise TypeError(
                "Previous-output information must be a dictionary."
            )

        return previous_output

    @staticmethod
    def _extract_script_pubkey(
        previous_output: dict[str, Any],
    ) -> bytes:
        """
        Extract scriptPubKey hexadecimal data.
        """

        script_pubkey = previous_output.get(
            "script_pubkey"
        )

        if script_pubkey is None:
            script_pubkey = previous_output.get(
                "scriptPubKey"
            )

        if script_pubkey is None:
            raise ValueError(
                "Previous output is missing scriptPubKey."
            )

        if isinstance(
            script_pubkey,
            dict,
        ):
            script_hex = script_pubkey.get(
                "hex"
            )
        else:
            script_hex = script_pubkey

        if not isinstance(
            script_hex,
            str,
        ):
            raise TypeError(
                "Previous output scriptPubKey must be hexadecimal text."
            )

        script_hex = script_hex.strip()

        if not script_hex:
            raise ValueError(
                "Previous output scriptPubKey cannot be empty."
            )

        try:
            return bytes.fromhex(
                script_hex
            )
        except ValueError as exc:
            raise ValueError(
                "Previous output scriptPubKey is not valid hexadecimal."
            ) from exc

    ###########################################################################
    # Serialization
    ###########################################################################

    @classmethod
    def _serialize_transaction(
        cls,
        transaction: BitcoinTransaction,
    ) -> bytes:
        """
        Serialize a Bitcoin transaction.
        """

        result = bytearray()

        result.extend(
            transaction.version.to_bytes(
                4,
                byteorder="little",
                signed=True,
            )
        )

        result.extend(
            cls._encode_varint(
                len(transaction.inputs)
            )
        )

        for transaction_input in transaction.inputs:
            result.extend(
                transaction_input.txid
            )

            result.extend(
                transaction_input.vout.to_bytes(
                    4,
                    byteorder="little",
                )
            )

            result.extend(
                cls._encode_varint(
                    len(
                        transaction_input.script_sig
                    )
                )
            )

            result.extend(
                transaction_input.script_sig
            )

            result.extend(
                transaction_input.sequence.to_bytes(
                    4,
                    byteorder="little",
                )
            )

        result.extend(
            cls._encode_varint(
                len(transaction.outputs)
            )
        )

        for transaction_output in transaction.outputs:
            result.extend(
                transaction_output.value.to_bytes(
                    8,
                    byteorder="little",
                )
            )

            result.extend(
                cls._encode_varint(
                    len(
                        transaction_output.script_pubkey
                    )
                )
            )

            result.extend(
                transaction_output.script_pubkey
            )

        result.extend(
            transaction.locktime.to_bytes(
                4,
                byteorder="little",
            )
        )

        return bytes(result)

    ###########################################################################
    # Binary Helpers
    ###########################################################################

    @staticmethod
    def _encode_varint(
        value: int,
    ) -> bytes:
        """
        Encode a Bitcoin compact-size integer.
        """

        if value < 0:
            raise ValueError(
                "VarInt value cannot be negative."
            )

        if value < 0xFD:
            return bytes([value])

        if value <= 0xFFFF:
            return (
                b"\xfd"
                + value.to_bytes(
                    2,
                    byteorder="little",
                )
            )

        if value <= 0xFFFFFFFF:
            return (
                b"\xfe"
                + value.to_bytes(
                    4,
                    byteorder="little",
                )
            )

        if value <= 0xFFFFFFFFFFFFFFFF:
            return (
                b"\xff"
                + value.to_bytes(
                    8,
                    byteorder="little",
                )
            )

        raise ValueError(
            "VarInt value is too large."
        )

    @staticmethod
    def _read_varint(
        data: bytes,
        offset: int,
    ) -> tuple[int, int]:
        """
        Read a Bitcoin compact-size integer.
        """

        if offset >= len(data):
            raise ValueError(
                "Unexpected end of transaction while reading VarInt."
            )

        prefix = data[offset]
        offset += 1

        if prefix < 0xFD:
            return prefix, offset

        if prefix == 0xFD:
            size = 2
        elif prefix == 0xFE:
            size = 4
        else:
            size = 8

        raw, offset = BitcoinTransactionSigner._read_bytes(
            data,
            offset,
            size,
        )

        return (
            int.from_bytes(
                raw,
                byteorder="little",
            ),
            offset,
        )

    @staticmethod
    def _read_bytes(
        data: bytes,
        offset: int,
        length: int,
    ) -> tuple[bytes, int]:
        """
        Read an exact number of bytes.
        """

        if length < 0:
            raise ValueError(
                "Read length cannot be negative."
            )

        end = offset + length

        if end > len(data):
            raise ValueError(
                "Unexpected end of Bitcoin transaction."
            )

        return (
            data[offset:end],
            end,
        )

    @staticmethod
    def _read_uint32_le(
        data: bytes,
        offset: int,
    ) -> tuple[int, int]:
        """
        Read a little-endian unsigned 32-bit integer.
        """

        raw, offset = (
            BitcoinTransactionSigner._read_bytes(
                data,
                offset,
                4,
            )
        )

        return (
            int.from_bytes(
                raw,
                byteorder="little",
            ),
            offset,
        )

    @staticmethod
    def _read_uint64_le(
        data: bytes,
        offset: int,
    ) -> tuple[int, int]:
        """
        Read a little-endian unsigned 64-bit integer.
        """

        raw, offset = (
            BitcoinTransactionSigner._read_bytes(
                data,
                offset,
                8,
            )
        )

        return (
            int.from_bytes(
                raw,
                byteorder="little",
            ),
            offset,
        )

    ###########################################################################
    # Validation
    ###########################################################################

    @staticmethod
    def _validate_transaction_hex(
        transaction: str,
    ) -> bytes:
        """
        Validate and decode transaction hexadecimal.
        """

        if not isinstance(
            transaction,
            str,
        ):
            raise TypeError(
                "transaction must be a hexadecimal string."
            )

        transaction = transaction.strip()

        if not transaction:
            raise ValueError(
                "transaction cannot be empty."
            )

        try:
            raw_transaction = bytes.fromhex(
                transaction
            )
        except ValueError as exc:
            raise ValueError(
                "transaction must contain valid hexadecimal data."
            ) from exc

        if not raw_transaction:
            raise ValueError(
                "transaction cannot be empty."
            )

        return raw_transaction

    ###########################################################################
    # Hashing
    ###########################################################################

    @staticmethod
    def _double_sha256(
        data: bytes,
    ) -> bytes:
        """
        Calculate Bitcoin's double-SHA256 digest.
        """

        return sha256(
            sha256(
                data
            ).digest()
        ).digest()


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "BitcoinTransactionSigner",
    "BitcoinInput",
    "BitcoinOutput",
    "BitcoinTransaction",
    "SIGHASH_ALL",
]


###############################################################################
# End of File
###############################################################################