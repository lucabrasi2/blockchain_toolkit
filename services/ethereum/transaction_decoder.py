"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.transaction_decoder

Purpose
-------
Ethereum transaction decoding layer.

This module converts raw Ethereum blockchain data obtained from providers
(Web3/RPC responses) into strongly typed UBP Ethereum transaction models.

Responsibilities
----------------
- Decode Ethereum transaction objects
- Decode Ethereum receipts
- Extract gas information
- Extract contract interaction details
- Extract event logs

This module does NOT:
- Connect directly to blockchain nodes
- Broadcast transactions
- Sign transactions
- Manage private keys


Architecture
------------

Ethereum RPC Provider
          |
          ▼
EthereumTransactionService
          |
          ▼
EthereumTransactionDecoder
          |
          ▼
EthereumTransaction Model
          |
          ▼
Reports / APIs / Analytics


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

import logging


from decimal import Decimal


from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple


from models.ethereum.transaction import (
    EthereumGasInfo,
    EthereumTransaction,
    EthereumTransactionLog,
    EthereumTransactionReceipt,
    create_ethereum_transaction,
)


from models.transaction import (
    TransactionFee,
    TransactionMetadata,
    TransactionParticipant,
    TransactionStatus,
    TransactionType,
)



###############################################################################
# Logger
###############################################################################

logger = logging.getLogger(__name__)



###############################################################################
# Ethereum Transaction Decoder
###############################################################################


class EthereumTransactionDecoder:
    """
    Converts raw Ethereum blockchain data into UBP Ethereum transaction models.
    """



    ###########################################################################
    # Constructor
    ###########################################################################

    def __init__(
        self,
        network: str = "Ethereum",
    ) -> None:
        """
        Initialize Ethereum transaction decoder.

        Parameters
        ----------
        network:
            Ethereum network name.
        """


        self.network = network


        logger.info(
            "EthereumTransactionDecoder initialized for %s network.",
            network,
        )



###############################################################################
# End Part 1
###############################################################################
###############################################################################
# Status Mapping
###############################################################################


    def decode_status(
        self,
        receipt_status: Optional[int],
    ) -> TransactionStatus:
        """
        Convert Ethereum receipt status into UBP transaction status.

        Ethereum:
            1 = success
            0 = failed
            None = pending/unavailable
        """


        if receipt_status == 1:

            return TransactionStatus.CONFIRMED


        if receipt_status == 0:

            return TransactionStatus.FAILED


        return TransactionStatus.PENDING



###############################################################################
# Transaction Type Detection
###############################################################################


    def detect_transaction_type(
        self,
        transaction: Dict[str, Any],
    ) -> TransactionType:
        """
        Determine Ethereum transaction type.

        Rules:

        No receiver:
            Contract creation

        Empty input:
            Native ETH transfer

        Input data:
            Contract interaction
        """


        receiver = transaction.get(
            "to"
        )


        input_data = transaction.get(
            "input",
            "0x",
        )


        if receiver is None:

            return TransactionType.CONTRACT_CREATION



        if input_data in (
            "",
            "0x",
            b"",
        ):

            return TransactionType.TRANSFER



        return TransactionType.CONTRACT_CALL


###############################################################################
###############################################################################
# Participant Creation
###############################################################################


    def create_participant(
        self,
        address: Optional[str],
        role: str,
    ) -> TransactionParticipant:
        """
        Create transaction participant object.

        Parameters
        ----------
        address:
            Ethereum wallet address.

        role:
            Participant role.

        Returns
        -------
        TransactionParticipant
        """


        if address is None:

            address = "CONTRACT_CREATION"



        return TransactionParticipant(

            address=address,

            role=role,

            network=self.network,

        )

###############################################################################
# Gas Decoding
###############################################################################


    def decode_gas(
        self,
        transaction: Dict[str, Any],
        receipt: Optional[
            Dict[str, Any]
        ] = None,
    ) -> EthereumGasInfo:
        """
        Convert raw Ethereum gas fields into
        EthereumGasInfo model.
        """


        return EthereumGasInfo(

            gas_limit=transaction.get(
                "gas",
                0,
            ),


            gas_used=(

                receipt.get(
                    "gasUsed"
                )

                if receipt

                else None

            ),


            gas_price=transaction.get(
                "gasPrice"
            ),


            max_fee_per_gas=transaction.get(
                "maxFeePerGas"
            ),


            max_priority_fee_per_gas=transaction.get(
                "maxPriorityFeePerGas"
            ),


            effective_gas_price=(

                receipt.get(
                    "effectiveGasPrice"
                )

                if receipt

                else None

            ),

        )



###############################################################################
# End Part 2
###############################################################################
###############################################################################
# Transaction Decoder
###############################################################################


    def decode_transaction(
        self,
        transaction: Dict[str, Any],
        receipt: Optional[
            Dict[str, Any]
        ] = None,
    ) -> EthereumTransaction:
        """
        Convert raw Ethereum transaction data
        into a UBP EthereumTransaction object.

        Parameters
        ----------
        transaction:
            Raw transaction dictionary from Web3.

        receipt:
            Optional transaction receipt.

        Returns
        -------
        EthereumTransaction
        """


        logger.info(
            "Decoding Ethereum transaction %s",
            transaction.get("hash"),
        )


        #######################################################################
        # Basic fields
        #######################################################################


        tx_hash = transaction.get(
            "hash"
        )


        if hasattr(
            tx_hash,
            "hex"
        ):

            tx_hash = tx_hash.hex()


        sender = self.create_participant(

            transaction.get(
                "from"
            ),

            role="SENDER",

        )


        receiver = self.create_participant(

            transaction.get(
                "to"
            ),

            role="RECEIVER",

        )

        #######################################################################
        # Transaction classification
        #######################################################################


        transaction_type = self.detect_transaction_type(

            transaction

        )

        #######################################################################
        # Status
        #######################################################################


        receipt_status = None


        if receipt:

            receipt_status = receipt.get(
                "status"
            )


        status = self.decode_status(

            receipt_status

        )

        #######################################################################
        # Gas
        #######################################################################


        gas = self.decode_gas(

            transaction,

            receipt,

        )


        #######################################################################
        # Receipt decoding
        #######################################################################


        decoded_receipt = None


        if receipt:


            decoded_receipt = self.decode_receipt(

                receipt

            )



        #######################################################################
        # Metadata
        #######################################################################


        metadata = TransactionMetadata(

            data={

                "input":

                    transaction.get(
                        "input",
                        "0x",
                    ),


                "block_number":

                    transaction.get(
                        "blockNumber"
                    ),

            }

        )

        #######################################################################
        # Fee
        #######################################################################


        fee = None


        if gas.gas_used and gas.effective_gas_price:


            fee = TransactionFee(

                amount=Decimal(

                    gas.gas_used

                    *

                    gas.effective_gas_price

                ),


                asset="ETH",

            )



        #######################################################################
        # Build Ethereum Model
        #######################################################################


        return create_ethereum_transaction(

            tx_hash=tx_hash,

            network=self.network,

            sender=sender,

            receiver=receiver,

            amount=Decimal(

                transaction.get(
                    "value",
                    0,
                )

            ),


            asset="ETH",


            status=status,


            transaction_type=transaction_type,


            nonce=transaction.get(
                "nonce",
                0,
            ),


            chain_id=transaction.get(
                "chainId",
                1,
            ),


            gas=gas,


            input_data=transaction.get(

                "input",

                "0x",

            ),


            contract_address=(

                receipt.get(
                    "contractAddress"
                )

                if receipt

                else None

            ),


            fee=fee,


            metadata=metadata,


            receipt=decoded_receipt,

        )



###############################################################################
# End Part 3
###############################################################################
###############################################################################
# Receipt Decoder
###############################################################################


    ###############################################################################
# Receipt Decoder
###############################################################################


    def decode_receipt(
        self,
        receipt: Dict[str, Any],
    ) -> EthereumTransactionReceipt:
        """
        Convert raw Ethereum receipt into
        UBP EthereumTransactionReceipt model.
        """


        logs = []


        for log in receipt.get(
            "logs",
            [],
        ):

            logs.append(

                self.decode_log(
                    log
                )

            )


        return EthereumTransactionReceipt(

            block_number=receipt.get(
                "blockNumber"
            ),


            block_hash=(

                receipt.get(
                    "blockHash"
                ).hex()

                if hasattr(
                    receipt.get(
                        "blockHash"
                    ),
                    "hex"
                )

                else receipt.get(
                    "blockHash"
                )

            ),


            transaction_index=receipt.get(
                "transactionIndex"
            ),


            status=receipt.get(
                "status"
            ),


            gas_used=receipt.get(
                "gasUsed"
            ),


            cumulative_gas_used=receipt.get(
                "cumulativeGasUsed"
            ),


            contract_address=receipt.get(
                "contractAddress"
            ),


            logs=tuple(
                logs
            ),

        )


################################################################################
# Log Decoder
###############################################################################


    def decode_log(
        self,
        log: Dict[str, Any],
    ) -> EthereumTransactionLog:
        """
        Convert Ethereum event log into
        UBP EthereumTransactionLog model.
        """


        return EthereumTransactionLog(

            address=log.get(
                "address",
            ),


            topics=tuple(

                topic.hex()

                if hasattr(
                    topic,
                    "hex",
                )

                else topic

                for topic in log.get(
                    "topics",
                    [],
                )

            ),


            data=log.get(
                "data",
                "0x",
            ),

        )


###############################################################################
# Batch Helpers
###############################################################################


    def decode_transactions(
        self,
        transactions: list[
            Dict[str, Any]
        ],
    ) -> list[EthereumTransaction]:
        """
        Decode multiple Ethereum transactions.
        """


        return [

            self.decode_transaction(
                tx
            )

            for tx in transactions

        ]



###############################################################################
# Representation
###############################################################################


    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"network={self.network}"

            ")"

        )



###############################################################################
# Public Exports
###############################################################################


__all__ = [

    "EthereumTransactionDecoder",

]



###############################################################################
# End Module
###############################################################################