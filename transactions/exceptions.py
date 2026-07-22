"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
transactions.exceptions

Purpose
-------
Enterprise transaction exception hierarchy.

This module defines all transaction-related exceptions used throughout
the Universal Blockchain Platform transaction subsystem.

The exception design allows transaction services, validators, signers,
serializers, and blockchain providers to communicate failures consistently.

Architecture
------------

Transaction
     |
     ▼
TransactionManager
     |
     ├── TransactionValidator
     ├── TransactionSigner
     ├── TransactionSerializer
     └── BlockchainProvider


Exception Hierarchy
-------------------

Exception

└── TransactionError

        ├── TransactionValidationError

        ├── TransactionStateError

        ├── TransactionSignatureError

        ├── TransactionSerializationError

        ├── TransactionNetworkError

        ├── TransactionBroadcastError

        └── TransactionNotFoundError


Responsibilities
----------------

- Invalid transaction data
- Invalid transaction state transitions
- Signing failures
- Serialization failures
- Network communication failures
- Broadcast failures
- Missing transactions


Author
------
Jaramogi Diddy


Platform
--------
Universal Blockchain Platform (UBP)


Version
-------
2.0 Enterprise
===============================================================================
"""


from __future__ import annotations


###############################################################################
# Base Transaction Exception
###############################################################################


class TransactionError(Exception):
    """
    Base exception for all transaction subsystem errors.

    All transaction-specific exceptions inherit from this class.
    """

    pass

###############################################################################
# Transaction Validation Errors
###############################################################################


class TransactionValidationError(
    TransactionError
):
    """
    Raised when transaction data fails validation.

    Examples
    --------
    - Missing sender address
    - Invalid receiver address
    - Invalid amount
    - Unsupported asset
    - Invalid network
    """

    pass



###############################################################################
# Transaction State Errors
###############################################################################


class TransactionStateError(
    TransactionError
):
    """
    Raised when a transaction enters an invalid state.

    Examples
    --------
    - Signing an already finalized transaction
    - Broadcasting an unsigned transaction
    - Confirming a rejected transaction
    """

    pass



###############################################################################
# Transaction Signature Errors
###############################################################################


class TransactionSignatureError(
    TransactionError
):
    """
    Raised when transaction signing or signature verification fails.

    Examples
    --------
    - Invalid private key
    - Signature mismatch
    - Missing signature
    - Unauthorized signing attempt
    """

    pass



###############################################################################
# Transaction Serialization Errors
###############################################################################


class TransactionSerializationError(
    TransactionError
):
    """
    Raised when transaction serialization or deserialization fails.

    Examples
    --------
    - Invalid transaction format
    - Corrupted payload
    - Missing serialized fields
    """

    pass

###############################################################################
# Transaction Network Errors
###############################################################################


class TransactionNetworkError(
    TransactionError
):
    """
    Raised when blockchain network communication fails.

    Examples
    --------
    - RPC connection failure
    - Provider unavailable
    - Node timeout
    - Network rejection
    """

    pass



###############################################################################
# Transaction Broadcast Errors
###############################################################################


class TransactionBroadcastError(
    TransactionError
):
    """
    Raised when transaction broadcasting fails.

    Examples
    --------
    - Transaction rejected by node
    - Invalid raw transaction
    - Duplicate transaction
    - Insufficient network fee
    """

    pass



###############################################################################
# Transaction Not Found Errors
###############################################################################


class TransactionNotFoundError(
    TransactionError
):
    """
    Raised when a requested transaction cannot be found.

    Examples
    --------
    - Unknown transaction ID
    - Missing transaction record
    - Deleted transaction
    """

    pass

###############################################################################
# Exception Information Helpers
###############################################################################


def transaction_exception_info() -> dict:
    """
    Return transaction exception subsystem information.

    Returns
    -------
    dict
        Exception metadata.
    """

    return {

        "service":
            "Transaction Exception Layer",

        "version":
            "2.0 Enterprise",

        "exception_family":
            "TransactionError",

        "supported_errors":
            [

                "Validation",
                "State",
                "Signature",
                "Serialization",
                "Network",
                "Broadcast",
                "NotFound",

            ],
    }



###############################################################################
# Exception Representation Enhancement
###############################################################################


def _exception_repr(
    self,
) -> str:
    """
    Developer representation for transaction exceptions.
    """

    return (

        f"{self.__class__.__name__}"
        f"('{self.args[0] if self.args else ''}')"

    )



def _exception_str(
    self,
) -> str:
    """
    Human-readable representation.
    """

    if self.args:

        return str(
            self.args[0]
        )

    return self.__class__.__name__



###############################################################################
# Attach Common Behaviour
###############################################################################


for _exception in (

    TransactionError,

    TransactionValidationError,

    TransactionStateError,

    TransactionSignatureError,

    TransactionSerializationError,

    TransactionNetworkError,

    TransactionBroadcastError,

    TransactionNotFoundError,

):

    _exception.__repr__ = _exception_repr

    _exception.__str__ = _exception_str



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "TransactionError",

    "TransactionValidationError",

    "TransactionStateError",

    "TransactionSignatureError",

    "TransactionSerializationError",

    "TransactionNetworkError",

    "TransactionBroadcastError",

    "TransactionNotFoundError",

    "transaction_exception_info",

]

###############################################################################
# End of transactions.exceptions
###############################################################################