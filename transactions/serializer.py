"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
transactions.serializer

Purpose
-------
Enterprise transaction serialization service.

This module converts transaction entities between internal objects and
external data formats.

Responsibilities
----------------

- Serialize Transaction objects
- Deserialize transaction dictionaries
- Convert transactions to JSON
- Restore transactions from JSON
- Preserve transaction integrity during conversion


The serializer does NOT perform:

- Transaction validation
- Transaction signing
- Blockchain encoding
- RPC communication


Architecture
------------

Transaction
     |
     ▼
TransactionSerializer
     |
     ├── Dictionary
     |
     └── JSON


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


import json


from datetime import datetime


from typing import Any
from typing import Dict


from transactions.transaction import Transaction

from transactions.exceptions import (
    TransactionValidationError,
)



###############################################################################
# Transaction Serializer
###############################################################################


class TransactionSerializer:
    """
    Enterprise transaction serialization service.

    Converts transaction objects into portable formats.
    """


    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
    ) -> None:
        """
        Initialize serializer.
        """

        pass
    
    ###########################################################################
    # Dictionary Serialization
    ###########################################################################


    def to_dict(
        self,
        transaction: Transaction,
    ) -> Dict[str, Any]:
        """
        Convert Transaction object into dictionary.

        Parameters
        ----------
        transaction:
            Transaction instance.

        Returns
        -------
        dict
            Serialized transaction.
        """


        if not isinstance(
            transaction,
            Transaction,
        ):

            raise TransactionValidationError(

                "Expected Transaction instance."

            )


        return transaction.to_dict()



    ###########################################################################
    # Dictionary Deserialization
    ###########################################################################


    def from_dict(
        self,
        data: Dict[str, Any],
    ) -> Transaction:
        """
        Restore Transaction object from dictionary.

        Parameters
        ----------
        data:
            Serialized transaction data.

        Returns
        -------
        Transaction
            Restored transaction.
        """


        if not isinstance(
            data,
            dict,
        ):

            raise TransactionValidationError(

                "Serialized transaction must be a dictionary."

            )


        required_fields = (

            "transaction_id",

            "sender",

            "receiver",

            "amount",

            "asset",

            "network",

        )


        for field in required_fields:

            if field not in data:

                raise TransactionValidationError(

                    f"Missing transaction field: {field}"

                )



        transaction = Transaction(

            transaction_id=data["transaction_id"],

            sender=data["sender"],

            receiver=data["receiver"],

            amount=data["amount"],

            asset=data["asset"],

            network=data["network"],

            metadata=data.get(
                "metadata",
                {},
            ),

        )



        if data.get("signature"):

            transaction.signature = data["signature"]



        if data.get("status"):

            transaction.status = data["status"]



        if data.get("timestamp"):

            transaction.timestamp = datetime.fromisoformat(

                data["timestamp"]

            )


        return transaction
    
    ###########################################################################
    # JSON Serialization
    ###########################################################################


    def to_json(
        self,
        transaction: Transaction,
        indent: int = 4,
    ) -> str:
        """
        Convert Transaction object into JSON string.

        Parameters
        ----------
        transaction:
            Transaction instance.

        indent:
            JSON indentation level.

        Returns
        -------
        str
            JSON representation.
        """


        data = self.to_dict(

            transaction

        )


        return json.dumps(

            data,

            indent=indent,

            default=str,

        )



    ###########################################################################
    # JSON Deserialization
    ###########################################################################


    def from_json(
        self,
        payload: str,
    ) -> Transaction:
        """
        Restore Transaction object from JSON.

        Parameters
        ----------
        payload:
            JSON transaction string.

        Returns
        -------
        Transaction
            Restored transaction.
        """


        if not isinstance(

            payload,

            str,

        ):

            raise TransactionValidationError(

                "JSON payload must be a string."

            )


        try:

            data = json.loads(

                payload

            )


        except json.JSONDecodeError as exc:

            raise TransactionValidationError(

                "Invalid JSON transaction data."

            ) from exc



        return self.from_dict(

            data

        )



    ###########################################################################
    # File Serialization
    ###########################################################################


    def save_json(
        self,
        transaction: Transaction,
        filename: str,
    ) -> str:
        """
        Save transaction as JSON file.

        Parameters
        ----------
        transaction:
            Transaction instance.

        filename:
            Destination file.

        Returns
        -------
        str
            Saved filename.
        """


        payload = self.to_json(

            transaction

        )


        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as file:

            file.write(

                payload

            )


        return filename



    ###########################################################################
    # File Restoration
    ###########################################################################


    def load_json(
        self,
        filename: str,
    ) -> Transaction:
        """
        Load transaction from JSON file.

        Parameters
        ----------
        filename:
            JSON file.

        Returns
        -------
        Transaction
            Restored transaction.
        """


        try:

            with open(

                filename,

                "r",

                encoding="utf-8",

            ) as file:

                payload = file.read()


        except FileNotFoundError as exc:

            raise TransactionValidationError(

                "Transaction file not found."

            ) from exc



        return self.from_json(

            payload

        )
    
    ###########################################################################
    # Validation Helpers
    ###########################################################################


    def validate_serialized(
        self,
        data: Dict[str, Any],
    ) -> bool:
        """
        Validate serialized transaction structure.

        Parameters
        ----------
        data:
            Serialized transaction dictionary.

        Returns
        -------
        bool
            True if valid.
        """


        if not isinstance(

            data,

            dict,

        ):

            raise TransactionValidationError(

                "Serialized transaction must be a dictionary."

            )



        required_fields = (

            "transaction_id",

            "sender",

            "receiver",

            "amount",

            "asset",

            "network",

        )


        for field in required_fields:

            if field not in data:

                raise TransactionValidationError(

                    f"Missing transaction field: {field}"

                )


        return True



    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return serializer information.

        Returns
        -------
        dict
            Serializer metadata.
        """


        return {

            "service":
                "Transaction Serializer",


            "version":
                "2.0 Enterprise",


            "formats":
                [

                    "dictionary",

                    "json",

                ],


            "purpose":
                "Transaction serialization and restoration",

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

            "TransactionSerializer()"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """


        return (

            "Transaction Serialization Service"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "TransactionSerializer",

]



###############################################################################
# End of transactions.serializer
###############################################################################