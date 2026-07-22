"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
transactions.transaction

Purpose
-------
Enterprise transaction entity model.

This module defines the core Transaction object used throughout the
Universal Blockchain Platform transaction subsystem.

The Transaction entity represents a value transfer request independent of
any specific blockchain implementation.

Blockchain-specific behaviour such as:

- gas calculation
- nonce handling
- transaction encoding
- network broadcasting
- signature generation

belongs to provider and service layers.

Architecture
------------

Wallet
  |
  ▼
Transaction
  |
  ▼
TransactionManager
  |
  ▼
BlockchainProvider


Responsibilities
----------------

- Store transaction information
- Track transaction lifecycle
- Provide serialization support
- Maintain transaction metadata
- Represent transaction state


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


from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional
from uuid import uuid4


from transactions.exceptions import (
    TransactionValidationError,
    TransactionStateError,
)


###############################################################################
# Transaction Entity
###############################################################################


class Transaction:
    """
    Enterprise transaction model.

    Represents a blockchain-independent transaction.
    """


    ###########################################################################
    # Valid States
    ###########################################################################


    VALID_STATES = (

        "created",

        "validated",

        "signed",

        "broadcast",

        "confirmed",

        "failed",

    )
    
    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
        sender: str,
        receiver: str,
        amount: float,
        asset: str,
        network: str,
        transaction_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a transaction.

        Parameters
        ----------
        sender:
            Source wallet address.

        receiver:
            Destination wallet address.

        amount:
            Transfer amount.

        asset:
            Asset being transferred.

        network:
            Blockchain network.

        transaction_id:
            Optional transaction identifier.

        metadata:
            Additional transaction information.
        """


        if not sender:

            raise TransactionValidationError(
                "Sender cannot be empty."
            )


        if not receiver:

            raise TransactionValidationError(
                "Receiver cannot be empty."
            )


        if amount <= 0:

            raise TransactionValidationError(
                "Transaction amount must be greater than zero."
            )


        if not asset:

            raise TransactionValidationError(
                "Asset cannot be empty."
            )


        if not network:

            raise TransactionValidationError(
                "Network cannot be empty."
            )


        self.transaction_id = (

            transaction_id

            if transaction_id

            else str(uuid4())

        )


        self.sender = sender

        self.receiver = receiver

        self.amount = amount

        self.asset = asset

        self.network = network


        self.status = "created"


        self.signature: Optional[str] = None


        self.timestamp = datetime.utcnow()


        self.metadata = (

            metadata

            if metadata is not None

            else {}

        )
    
    ###########################################################################
    # Transaction State Management
    ###########################################################################


    def update_status(
        self,
        status: str,
    ) -> None:
        """
        Update transaction lifecycle status.

        Parameters
        ----------
        status:
            New transaction state.

        Raises
        ------
        TransactionStateError
            If state is invalid.
        """


        if status not in self.VALID_STATES:

            raise TransactionStateError(

                f"Invalid transaction state: {status}"

            )


        self.status = status



    def validate_state_transition(
        self,
        new_state: str,
    ) -> bool:
        """
        Validate whether a state transition is allowed.

        Parameters
        ----------
        new_state:
            Requested state.

        Returns
        -------
        bool
            True if transition is valid.
        """


        transitions = {

            "created": [

                "validated",

                "failed",

            ],


            "validated": [

                "signed",

                "failed",

            ],


            "signed": [

                "broadcast",

                "failed",

            ],


            "broadcast": [

                "confirmed",

                "failed",

            ],


            "confirmed": [],


            "failed": [],

        }


        if new_state not in transitions.get(

            self.status,

            []

        ):

            raise TransactionStateError(

                f"Cannot move transaction from "
                f"{self.status} to {new_state}"

            )


        return True



    def sign(
        self,
        signature: str,
    ) -> None:
        """
        Attach transaction signature.

        Signature generation is handled by TransactionSigner.

        Parameters
        ----------
        signature:
            Signed transaction proof.
        """


        if self.status not in (

            "created",

            "validated",

        ):

            raise TransactionStateError(

                "Transaction cannot be signed "
                "in current state."

            )


        if not signature:

            raise TransactionValidationError(

                "Signature cannot be empty."

            )


        self.signature = signature


        self.status = "signed"
    
    ###########################################################################
    # Serialization
    ###########################################################################


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert transaction into dictionary format.

        Returns
        -------
        dict
            Serialized transaction.
        """


        return {

            "transaction_id":
                self.transaction_id,


            "sender":
                self.sender,


            "receiver":
                self.receiver,


            "amount":
                self.amount,


            "asset":
                self.asset,


            "network":
                self.network,


            "status":
                self.status,


            "signature":
                self.signature,


            "timestamp":
                self.timestamp.isoformat(),


            "metadata":
                self.metadata,

        }



    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return transaction information.

        Returns
        -------
        dict
            Transaction metadata.
        """


        return {

            "service":
                "Transaction Entity",


            "version":
                "2.0 Enterprise",


            "transaction_id":
                self.transaction_id,


            "network":
                self.network,


            "asset":
                self.asset,


            "status":
                self.status,

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

            f"Transaction("
            f"id='{self.transaction_id}', "
            f"status='{self.status}', "
            f"network='{self.network}'"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """


        return (

            f"Transaction "
            f"{self.transaction_id} "
            f"({self.status})"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "Transaction",

]


###############################################################################
# End of transactions.transaction
###############################################################################