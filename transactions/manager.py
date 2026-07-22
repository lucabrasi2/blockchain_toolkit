"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
transactions.manager

Purpose
-------
Enterprise transaction orchestration layer.

The TransactionManager coordinates transaction creation, validation,
signing and serialization.

The manager delegates implementation details to specialized services.

Architecture
------------

                 TransactionManager
                         |
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 TransactionValidator  TransactionSigner  TransactionSerializer
        |
        ▼
  Transaction


Responsibilities
----------------

- Create transactions
- Validate transactions
- Sign transactions
- Serialize transactions
- Deserialize transactions
- Provide transaction metadata


The manager does NOT perform:

- Blockchain broadcasting
- Network communication
- Gas calculation
- Consensus validation
- Private key generation


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


from typing import Any
from typing import Dict
from typing import Optional


from transactions.transaction import Transaction

from transactions.validator import (
    TransactionValidator,
)

from transactions.signer import (
    TransactionSigner,
)

from transactions.serializer import (
    TransactionSerializer,
)



###############################################################################
# Transaction Manager
###############################################################################


class TransactionManager:
    """
    Enterprise transaction orchestration service.
    """


    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
        validator: Optional[TransactionValidator] = None,
        signer: Optional[TransactionSigner] = None,
        serializer: Optional[TransactionSerializer] = None,
    ) -> None:
        """
        Initialize transaction manager.
        """


        self.validator = (

            validator

            if validator is not None

            else TransactionValidator()

        )


        self.signer = (

            signer

            if signer is not None

            else TransactionSigner()

        )


        self.serializer = (

            serializer

            if serializer is not None

            else TransactionSerializer()

        )
    
    ###########################################################################
    # Transaction Creation
    ###########################################################################


    def create_transaction(
        self,
        transaction_id: str,
        sender: str,
        receiver: str,
        amount: float,
        asset: str,
        network: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Transaction:
        """
        Create a new transaction.

        Parameters
        ----------
        transaction_id:
            Unique transaction identifier.

        sender:
            Sender wallet address.

        receiver:
            Receiver wallet address.

        amount:
            Transfer amount.

        asset:
            Asset symbol.

        network:
            Blockchain network.

        metadata:
            Optional transaction metadata.

        Returns
        -------
        Transaction
            Newly created transaction.
        """


        transaction = Transaction(

            transaction_id=transaction_id,

            sender=sender,

            receiver=receiver,

            amount=amount,

            asset=asset,

            network=network,

            metadata=metadata,

        )


        self.validator.validate_transaction(

            transaction

        )


        return transaction



    ###########################################################################
    # Transaction Validation
    ###########################################################################


    def validate_transaction(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate transaction object.

        Parameters
        ----------
        transaction:
            Transaction instance.

        Returns
        -------
        bool
            True if valid.
        """


        return self.validator.validate_transaction(

            transaction

        )



    def validate_serialized(
        self,
        data: Dict[str, Any],
    ) -> bool:
        """
        Validate serialized transaction data.

        Parameters
        ----------
        data:
            Serialized transaction.

        Returns
        -------
        bool
            True if valid.
        """


        return self.validator.validate_serialized(

            data

        )
    
    ###########################################################################
    # Transaction Signing
    ###########################################################################


    def sign_transaction(
        self,
        transaction: Transaction,
        private_key: str,
    ) -> Transaction:
        """
        Sign a transaction.

        Parameters
        ----------
        transaction:
            Transaction instance.

        private_key:
            Signing key.

        Returns
        -------
        Transaction
            Signed transaction.
        """


        self.validator.validate_transaction(

            transaction

        )


        return self.signer.sign_transaction(

            transaction,

            private_key,

        )



    ###########################################################################
    # Serialization
    ###########################################################################


    def serialize_transaction(
        self,
        transaction: Transaction,
    ) -> Dict[str, Any]:
        """
        Serialize transaction into dictionary format.

        Parameters
        ----------
        transaction:
            Transaction instance.

        Returns
        -------
        dict
            Serialized transaction.
        """


        self.validator.validate_transaction(

            transaction

        )


        return self.serializer.serialize(

            transaction

        )



    def deserialize_transaction(
        self,
        data: Dict[str, Any],
    ) -> Transaction:
        """
        Restore transaction from serialized data.

        Parameters
        ----------
        data:
            Serialized transaction.

        Returns
        -------
        Transaction
            Restored transaction.
        """


        self.validator.validate_serialized(

            data

        )


        transaction = self.serializer.deserialize(

            data

        )


        self.validator.validate_transaction(

            transaction

        )


        return transaction



    ###########################################################################
    # JSON Serialization
    ###########################################################################


    def transaction_to_json(
        self,
        transaction: Transaction,
    ) -> str:
        """
        Convert transaction to JSON.

        Parameters
        ----------
        transaction:
            Transaction instance.

        Returns
        -------
        str
            JSON representation.
        """


        self.validator.validate_transaction(

            transaction

        )


        return self.serializer.to_json(

            transaction

        )



    def transaction_from_json(
        self,
        data: str,
    ) -> Transaction:
        """
        Restore transaction from JSON.

        Parameters
        ----------
        data:
            JSON transaction.

        Returns
        -------
        Transaction
            Transaction object.
        """


        transaction = self.serializer.from_json(

            data

        )


        self.validator.validate_transaction(

            transaction

        )


        return transaction
    
    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return manager information.

        Returns
        -------
        dict
            Manager metadata.
        """


        return {

            "service":

                "Transaction Manager",


            "version":

                "2.0 Enterprise",


            "validator":

                self.validator.__class__.__name__,


            "signer":

                self.signer.__class__.__name__,


            "serializer":

                self.serializer.__class__.__name__,

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

            f"TransactionManager("
            f"validator='{self.validator.__class__.__name__}', "
            f"signer='{self.signer.__class__.__name__}', "
            f"serializer='{self.serializer.__class__.__name__}'"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """


        return (

            "Transaction Manager"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "TransactionManager",

]


###############################################################################
# End of transactions.manager
###############################################################################