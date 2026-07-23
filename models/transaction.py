"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
models.transaction

Purpose
-------
Universal transaction domain models.

This module defines blockchain-independent transaction structures used across
the Universal Blockchain Platform.

The models in this file contain data only.

They do NOT:
- connect to blockchain networks
- communicate with providers
- perform validation
- sign transactions
- broadcast transactions
- access Web3

Architecture
------------

Blockchain
     |
     ▼
Services
     |
     ▼
Models
     |
     ▼
Reports / API / UI


Supported Concepts
------------------

- Transaction status
- Transaction type
- Transaction participants
- Transaction fees
- Universal transaction representation


Author
------
Jaramogi Diddy


Platform
--------
Universal Blockchain Platform (UBP)


Version
-------
3.0 Enterprise
===============================================================================
"""


from __future__ import annotations


###############################################################################
# Imports
###############################################################################

from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import Optional



###############################################################################
# Transaction Status
###############################################################################


class TransactionStatus(
    Enum
):
    """
    Universal transaction lifecycle states.
    """


    PENDING = "pending"


    CONFIRMED = "confirmed"


    FAILED = "failed"


    REJECTED = "rejected"


    DROPPED = "dropped"


    UNKNOWN = "unknown"



###############################################################################
# Transaction Type
###############################################################################


class TransactionType(
    Enum
):
    """
    Universal blockchain transaction categories.
    """


    TRANSFER = "transfer"


    CONTRACT_CALL = "contract_call"


    CONTRACT_DEPLOYMENT = "contract_deployment"


    TOKEN_TRANSFER = "token_transfer"


    NFT_TRANSFER = "nft_transfer"


    STAKE = "stake"


    UNSTAKE = "unstake"


    SWAP = "swap"


    UNKNOWN = "unknown"



###############################################################################
# Transaction Participant
###############################################################################


@dataclass(
    frozen=True,
    slots=True,
)
class TransactionParticipant:
    """
    Represents an entity participating in a transaction.

    Examples
    --------
    Sender wallet

    Receiver wallet

    Smart contract address
    """


    address: str


    role: str


    network: str



###############################################################################
# End Part 1
###############################################################################
###############################################################################
# Transaction Fee
###############################################################################


@dataclass(
    frozen=True,
    slots=True,
)
class TransactionFee:
    """
    Universal transaction fee representation.

    This model is blockchain-independent.

    Examples
    --------
    Ethereum:
        ETH gas fee

    Bitcoin:
        BTC miner fee

    TRON:
        Energy / bandwidth fee
    """


    amount: Decimal


    asset: str



###############################################################################
# Transaction Metadata
###############################################################################


@dataclass(
    frozen=True,
    slots=True,
)
class TransactionMetadata:
    """
    Additional transaction information.

    This allows blockchain-specific or application-specific
    information to be attached without modifying the core model.
    """


    data: Dict[str, Any]



###############################################################################
# Transaction Confirmation
###############################################################################


@dataclass(
    frozen=True,
    slots=True,
)
class TransactionConfirmation:
    """
    Represents blockchain confirmation information.
    """


    block_number: Optional[int]


    block_hash: Optional[str]


    confirmations: int



###############################################################################
# End Part 2
###############################################################################
###############################################################################
# Universal Transaction Model
###############################################################################


@dataclass(
    frozen=True,
    slots=True,
)
class Transaction:
    """
    Universal blockchain transaction representation.

    This is the core transaction model used throughout UBP.

    It represents concepts common across blockchain networks.

    Blockchain-specific implementations should extend this model.

    Examples
    --------
    Ethereum adds:
        - nonce
        - gas
        - chain id
        - calldata

    Bitcoin adds:
        - inputs
        - outputs
        - satoshi fees
    """


    tx_hash: str


    network: str


    sender: TransactionParticipant


    receiver: TransactionParticipant


    asset: str


    amount: Decimal


    status: TransactionStatus


    transaction_type: TransactionType


    timestamp: Optional[int] = None


    fee: Optional[TransactionFee] = None


    confirmation: Optional[
        TransactionConfirmation
    ] = None


    metadata: Optional[
        TransactionMetadata
    ] = None



###############################################################################
# Transaction Builder Helpers
###############################################################################


def create_transaction_metadata(
    data: Optional[Dict[str, Any]] = None,
) -> TransactionMetadata:
    """
    Create transaction metadata safely.

    Parameters
    ----------
    data:
        Optional metadata dictionary.

    Returns
    -------
    TransactionMetadata
    """


    return TransactionMetadata(

        data=data or {}

    )



def create_transaction_fee(
    amount: Decimal,
    asset: str,
) -> TransactionFee:
    """
    Create a transaction fee model.

    Parameters
    ----------
    amount:
        Fee amount.

    asset:
        Fee currency.

    Returns
    -------
    TransactionFee
    """


    return TransactionFee(

        amount=amount,

        asset=asset,

    )



###############################################################################
# End Part 3
###############################################################################
###############################################################################
# Serialization Helpers
###############################################################################


def transaction_to_dict(
    transaction: Transaction,
) -> Dict[str, Any]:
    """
    Convert Transaction model into dictionary form.

    Useful for:
    - API responses
    - JSON serialization
    - Logging
    - Storage


    Parameters
    ----------
    transaction:
        Transaction instance.

    Returns
    -------
    dict
        Serializable transaction data.
    """


    return {

        "tx_hash":
            transaction.tx_hash,


        "network":
            transaction.network,


        "sender": {

            "address":
                transaction.sender.address,

            "role":
                transaction.sender.role,

            "network":
                transaction.sender.network,

        },


        "receiver": {

            "address":
                transaction.receiver.address,

            "role":
                transaction.receiver.role,

            "network":
                transaction.receiver.network,

        },


        "asset":
            transaction.asset,


        "amount":
            str(transaction.amount),


        "status":
            transaction.status.value,


        "transaction_type":
            transaction.transaction_type.value,


        "timestamp":
            transaction.timestamp,


        "fee": (

            {

                "amount":
                    str(transaction.fee.amount),

                "asset":
                    transaction.fee.asset,

            }

            if transaction.fee

            else None

        ),


        "confirmation": (

            {

                "block_number":
                    transaction.confirmation.block_number,

                "block_hash":
                    transaction.confirmation.block_hash,

                "confirmations":
                    transaction.confirmation.confirmations,

            }

            if transaction.confirmation

            else None

        ),


        "metadata": (

            transaction.metadata.data

            if transaction.metadata

            else {}

        ),

    }



###############################################################################
# Public Exports
###############################################################################


__all__ = [

    "TransactionStatus",

    "TransactionType",

    "TransactionParticipant",

    "TransactionFee",

    "TransactionMetadata",

    "TransactionConfirmation",

    "Transaction",

    "create_transaction_metadata",

    "create_transaction_fee",

    "transaction_to_dict",

]



###############################################################################
# End Module
###############################################################################