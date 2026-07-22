"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
transactions.validator

Purpose
-------
Enterprise transaction validation service.

This module provides blockchain-agnostic validation for Transaction entities
within the Universal Blockchain Platform (UBP).

The validator ensures transaction objects and serialized transaction data are
structurally correct before they are signed, stored, encrypted, or transmitted.

The validator intentionally does NOT perform blockchain-specific validation:

- Ethereum transaction rules
- Bitcoin transaction format checks
- TRON transaction encoding
- Gas calculation
- Nonce validation
- Provider-specific rules

Those responsibilities belong to blockchain provider implementations.


Architecture
------------

Transaction
      |
      ▼
TransactionValidator
      |
      ├── Transaction Validation
      ├── Address Validation
      ├── Amount Validation
      ├── Asset Validation
      ├── Network Validation
      └── Serialization Validation


Responsibilities
----------------

- Validate Transaction objects
- Validate transaction identifiers
- Validate sender and receiver fields
- Validate amounts
- Validate assets
- Validate networks
- Validate metadata
- Validate serialized transactions


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


import re


from typing import Any
from typing import Dict


from transactions.transaction import Transaction


from transactions.exceptions import (
    TransactionValidationError,
)



###############################################################################
# Transaction Validator
###############################################################################


class TransactionValidator:
    """
    Enterprise transaction validation service.

    Performs generic structural validation while remaining blockchain
    independent.
    """


    ###########################################################################
    # Validation Patterns
    ###########################################################################


    VALID_IDENTIFIER = re.compile(
        r"^[A-Za-z0-9_-]{8,128}$"
    )


    VALID_ADDRESS = re.compile(
        r"^[A-Za-z0-9]{3,128}$"
    )


    VALID_NETWORK = re.compile(
        r"^[A-Za-z0-9_-]{2,64}$"
    )


    VALID_ASSET = re.compile(
        r"^[A-Za-z0-9_-]{2,32}$"
    )



    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
    ) -> None:
        """
        Initialize validator.
        """

        pass
    
    ###########################################################################
    # Transaction Validation
    ###########################################################################


    def validate_transaction(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Validate Transaction object.

        Parameters
        ----------
        transaction:
            Transaction instance.

        Returns
        -------
        bool
            True if validation succeeds.

        Raises
        ------
        TransactionValidationError
            If validation fails.
        """


        if not isinstance(

            transaction,

            Transaction,

        ):

            raise TransactionValidationError(

                "Expected Transaction instance."

            )


        self.validate_transaction_id(

            transaction.transaction_id

        )


        self.validate_sender(

            transaction.sender

        )


        self.validate_receiver(

            transaction.receiver

        )


        self.validate_amount(

            transaction.amount

        )


        self.validate_asset(

            transaction.asset

        )


        self.validate_network(

            transaction.network

        )


        self.validate_metadata(

            transaction.metadata

        )


        return True



    ###########################################################################
    # Transaction ID Validation
    ###########################################################################


    def validate_transaction_id(
        self,
        transaction_id: str,
    ) -> bool:
        """
        Validate transaction identifier.
        """


        if not transaction_id:

            raise TransactionValidationError(

                "Transaction ID cannot be empty."

            )


        if not isinstance(

            transaction_id,

            str,

        ):

            raise TransactionValidationError(

                "Transaction ID must be a string."

            )


        if not self.VALID_IDENTIFIER.fullmatch(

            transaction_id

        ):

            raise TransactionValidationError(

                "Invalid transaction ID."

            )


        return True



    ###########################################################################
    # Address Validation
    ###########################################################################


    def validate_sender(
        self,
        sender: str,
    ) -> bool:
        """
        Validate transaction sender address.
        """


        if not sender:

            raise TransactionValidationError(

                "Sender address cannot be empty."

            )


        if not isinstance(

            sender,

            str,

        ):

            raise TransactionValidationError(

                "Sender address must be a string."

            )


        if not self.VALID_ADDRESS.fullmatch(

            sender

        ):

            raise TransactionValidationError(

                "Invalid sender address."

            )


        return True



    def validate_receiver(
        self,
        receiver: str,
    ) -> bool:
        """
        Validate transaction receiver address.
        """


        if not receiver:

            raise TransactionValidationError(

                "Receiver address cannot be empty."

            )


        if not isinstance(

            receiver,

            str,

        ):

            raise TransactionValidationError(

                "Receiver address must be a string."

            )


        if not self.VALID_ADDRESS.fullmatch(

            receiver

        ):

            raise TransactionValidationError(

                "Invalid receiver address."

            )


        return True
    
    ###########################################################################
    # Amount Validation
    ###########################################################################


    def validate_amount(
        self,
        amount: Any,
    ) -> bool:
        """
        Validate transaction amount.

        Parameters
        ----------
        amount:
            Transaction amount.

        Returns
        -------
        bool
            True if valid.
        """


        if amount is None:

            raise TransactionValidationError(

                "Transaction amount cannot be empty."

            )


        if isinstance(

            amount,

            bool,

        ):

            raise TransactionValidationError(

                "Invalid transaction amount."

            )


        if not isinstance(

            amount,

            (int, float),

        ):

            raise TransactionValidationError(

                "Transaction amount must be numeric."

            )


        if amount <= 0:

            raise TransactionValidationError(

                "Transaction amount must be greater than zero."

            )


        return True



    ###########################################################################
    # Asset Validation
    ###########################################################################


    def validate_asset(
        self,
        asset: str,
    ) -> bool:
        """
        Validate transaction asset.

        Examples:

        ETH
        BTC
        USDT
        TRX
        """


        if not asset:

            raise TransactionValidationError(

                "Asset cannot be empty."

            )


        if not isinstance(

            asset,

            str,

        ):

            raise TransactionValidationError(

                "Asset must be a string."

            )


        asset = asset.strip()


        if not self.VALID_ASSET.fullmatch(

            asset

        ):

            raise TransactionValidationError(

                "Invalid asset format."

            )


        return True



    ###########################################################################
    # Network Validation
    ###########################################################################


    def validate_network(
        self,
        network: str,
    ) -> bool:
        """
        Validate blockchain network name.

        Examples:

        ethereum
        bitcoin
        tron
        solana
        """


        if not network:

            raise TransactionValidationError(

                "Network cannot be empty."

            )


        if not isinstance(

            network,

            str,

        ):

            raise TransactionValidationError(

                "Network must be a string."

            )


        network = network.strip()


        if not self.VALID_NETWORK.fullmatch(

            network

        ):

            raise TransactionValidationError(

                "Invalid network format."

            )


        return True



    ###########################################################################
    # Metadata Validation
    ###########################################################################


    def validate_metadata(
        self,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Validate transaction metadata.
        """


        if metadata is None:

            return True



        if not isinstance(

            metadata,

            dict,

        ):

            raise TransactionValidationError(

                "Metadata must be a dictionary."

            )



        for key in metadata.keys():


            if not isinstance(

                key,

                str,

            ):

                raise TransactionValidationError(

                    "Metadata keys must be strings."

                )


        return True
    
    ###########################################################################
    # Serialized Transaction Validation
    ###########################################################################


    def validate_serialized(
        self,
        data: Dict[str, Any],
    ) -> bool:
        """
        Validate serialized transaction dictionary.

        Parameters
        ----------
        data:
            Serialized transaction.

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

                    f"Missing required field: {field}"

                )


        self.validate_transaction_id(

            data["transaction_id"]

        )


        self.validate_sender(

            data["sender"]

        )


        self.validate_receiver(

            data["receiver"]

        )


        self.validate_amount(

            data["amount"]

        )


        self.validate_asset(

            data["asset"]

        )


        self.validate_network(

            data["network"]

        )


        self.validate_metadata(

            data.get(

                "metadata",

                {},

            )

        )


        return True



    ###########################################################################
    # Convenience Validation
    ###########################################################################


    def is_valid(
        self,
        transaction: Transaction,
    ) -> bool:
        """
        Determine whether transaction is valid.

        Unlike validate_transaction(), this method returns False instead
        of raising exceptions.
        """


        try:

            return self.validate_transaction(

                transaction

            )


        except TransactionValidationError:

            return False



    ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return validator information.
        """


        return {

            "service":

                "Transaction Validator",


            "version":

                "2.0 Enterprise",


            "validation_scope":

                (

                    "Generic blockchain-agnostic "
                    "transaction validation"

                ),

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

            f"{self.__class__.__name__}()"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """


        return (

            "Transaction Validator"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [

    "TransactionValidator",

]



###############################################################################
# End of transactions.validator
###############################################################################