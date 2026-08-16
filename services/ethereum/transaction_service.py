"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.transaction_service

Purpose
-------
Ethereum transaction service layer.

This service provides comprehensive transaction analysis,
retrieval, and reporting functionality.

Responsibilities
----------------
- Retrieve Ethereum transactions
- Retrieve transaction receipts
- Generate transaction reports
- Determine transaction status
- Calculate transaction confirmations
- Retrieve gas price information
- Perform ETH/Wei conversions

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

from typing import Any

from web3 import Web3

from core.logger import get_logger
from ethereum.connection import get_connection


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Ethereum Transaction Service
###############################################################################


class TransactionService:
    """
    Ethereum transaction service.

    Provides transaction analysis, retrieval,
    reporting, and confirmation functionality.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the transaction service.
        """

        self.w3 = get_connection()

        logger.info(
            "TransactionService initialized."
        )

    ###########################################################################
    # Connection
    ###########################################################################

    def get_connection(
        self,
    ) -> Web3:
        """
        Get the active Web3 connection.

        Returns
        -------
        Web3
            Active Web3 connection.
        """

        return self.w3

    ###########################################################################
    # Transaction Retrieval
    ###########################################################################

    def get_transaction(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Get a raw Ethereum transaction by hash.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Raw transaction data.
        """

        logger.info(
            "Retrieving Ethereum transaction: %s",
            tx_hash,
        )

        try:

            transaction = (
                self.w3.eth.get_transaction(
                    tx_hash,
                )
            )

            logger.info(
                "Ethereum transaction retrieved successfully."
            )

            return transaction

        except Exception:

            logger.exception(
                "Failed to retrieve transaction: %s",
                tx_hash,
            )

            raise

    ###########################################################################
    # Transaction Receipt
    ###########################################################################

    def get_receipt(
        self,
        tx_hash: str,
    ) -> dict[str, Any] | None:
        """
        Get an Ethereum transaction receipt.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any] | None
            Transaction receipt, or None when unavailable.
        """

        logger.info(
            "Retrieving transaction receipt: %s",
            tx_hash,
        )

        try:

            receipt = (
                self.w3.eth.get_transaction_receipt(
                    tx_hash,
                )
            )

            logger.info(
                "Transaction receipt retrieved successfully."
            )

            return receipt

        except Exception:

            logger.warning(
                "Transaction receipt unavailable: %s",
                tx_hash,
            )

            return None

    ###########################################################################
    # Unit Conversion
    ###########################################################################

    def wei_to_eth(
        self,
        wei: int,
    ) -> float:
        """
        Convert Wei to Ether.

        Parameters
        ----------
        wei : int
            Amount in Wei.

        Returns
        -------
        float
            Amount in Ether.
        """

        return float(
            self.w3.from_wei(
                wei,
                "ether",
            )
        )

    def eth_to_wei(
        self,
        eth: float,
    ) -> int:
        """
        Convert Ether to Wei.

        Parameters
        ----------
        eth : float
            Amount in Ether.

        Returns
        -------
        int
            Amount in Wei.
        """

        return int(
            self.w3.to_wei(
                eth,
                "ether",
            )
        )


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Transaction Report
    ###########################################################################

    def get_transaction_report(
        self,
        tx_hash: str,
    ) -> dict[str, Any]:
        """
        Generate a complete Ethereum transaction report.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Complete transaction report.
        """

        logger.info(
            "Generating transaction report for: %s",
            tx_hash,
        )

        #######################################################################
        # Normalize Transaction Hash
        #######################################################################

        if isinstance(tx_hash, bytes):

            tx_hash = (
                "0x"
                + tx_hash.hex()
            )

        elif not tx_hash.startswith("0x"):

            tx_hash = (
                "0x"
                + tx_hash
            )

        try:

            ###################################################################
            # Retrieve Transaction
            ###################################################################

            transaction = self.get_transaction(
                tx_hash,
            )

            ###################################################################
            # Retrieve Receipt
            ###################################################################

            receipt = self.get_receipt(
                tx_hash,
            )

            ###################################################################
            # Transaction Fields
            ###################################################################

            block_hash = transaction.get(
                "blockHash",
            )

            if hasattr(
                block_hash,
                "hex",
            ):
                block_hash = block_hash.hex()

            input_data = transaction.get(
                "input",
            )

            if hasattr(
                input_data,
                "hex",
            ):
                input_data = input_data.hex()

            elif not input_data:
                input_data = "0x"

            ###################################################################
            # Base Transaction Report
            ###################################################################

            report: dict[str, Any] = {
                "hash": tx_hash,

                "block_number": transaction.get(
                    "blockNumber",
                ),

                "block_hash": block_hash,

                "from": transaction.get(
                    "from",
                ),

                "to": transaction.get(
                    "to",
                ),

                "value": self.wei_to_eth(
                    transaction.get(
                        "value",
                        0,
                    )
                ),

                "gas": transaction.get(
                    "gas",
                ),

                "gas_price": transaction.get(
                    "gasPrice",
                ),

                "nonce": transaction.get(
                    "nonce",
                ),

                "input": input_data,

                "chain_id": transaction.get(
                    "chainId",
                ),

                "transaction_index": transaction.get(
                    "transactionIndex",
                ),

                "type": transaction.get(
                    "type",
                ),
            }

            ###################################################################
            # Receipt Information
            ###################################################################

            if receipt:

                logs = receipt.get(
                    "logs",
                    [],
                )

                report.update(
                    {
                        "is_success": (
                            receipt.get(
                                "status",
                            ) == 1
                        ),

                        "gas_used": receipt.get(
                            "gasUsed",
                        ),

                        "cumulative_gas_used": receipt.get(
                            "cumulativeGasUsed",
                        ),

                        "contract_address": receipt.get(
                            "contractAddress",
                        ),

                        "logs": logs,

                        "effective_gas_price": (
                            receipt.get(
                                "effectiveGasPrice",
                            )
                        ),

                        "logs_count": len(
                            logs,
                        ),
                    }
                )

            else:

                report.update(
                    {
                        "is_success": None,
                        "gas_used": None,
                        "cumulative_gas_used": None,
                        "contract_address": None,
                        "logs": [],
                        "effective_gas_price": None,
                        "logs_count": 0,
                    }
                )

            logger.info(
                "Transaction report generated successfully: %s",
                tx_hash,
            )

            return report

        except Exception as error:

            logger.exception(
                "Failed to generate transaction report: %s",
                tx_hash,
            )

            return {
                "hash": tx_hash,
                "error": str(error),
            }

    ###########################################################################
    # Transaction Status
    ###########################################################################

    def get_transaction_status(
        self,
        tx_hash: str,
    ) -> str:
        """
        Get transaction status as a string.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        str
            Transaction status.
        """

        logger.info(
            "Checking transaction status: %s",
            tx_hash,
        )

        try:

            receipt = self.get_receipt(
                tx_hash,
            )

            if receipt is None:
                return "Pending"

            status = receipt.get(
                "status",
            )

            if status == 1:
                return "Success"

            if status == 0:
                return "Failed"

            return "Unknown"

        except Exception:

            logger.exception(
                "Failed to determine transaction status: %s",
                tx_hash,
            )

            return "Unknown"


###############################################################################
# End of Part 2
###############################################################################
    ###########################################################################
    # Gas Price
    ###########################################################################

    def get_gas_price(
        self,
    ) -> int:
        """
        Get the current Ethereum gas price in Wei.

        Returns
        -------
        int
            Gas price in Wei.
        """

        logger.info(
            "Retrieving current Ethereum gas price."
        )

        return self.w3.eth.gas_price

    def get_gas_price_gwei(
        self,
    ) -> float:
        """
        Get the current Ethereum gas price in Gwei.

        Returns
        -------
        float
            Gas price in Gwei.
        """

        logger.info(
            "Retrieving current Ethereum gas price in Gwei."
        )

        return float(
            self.w3.from_wei(
                self.get_gas_price(),
                "gwei",
            )
        )

    ###########################################################################
    # Transaction Confirmation
    ###########################################################################

    def is_transaction_confirmed(
        self,
        tx_hash: str,
    ) -> bool:
        """
        Check whether a transaction has been confirmed.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        bool
            True if a transaction receipt exists.
        """

        receipt = self.get_receipt(
            tx_hash,
        )

        return receipt is not None

    def get_transaction_confirmations(
        self,
        tx_hash: str,
    ) -> int:
        """
        Get the number of confirmations for a transaction.

        Parameters
        ----------
        tx_hash : str
            Transaction hash.

        Returns
        -------
        int
            Number of confirmations.
        """

        logger.info(
            "Calculating confirmations for transaction: %s",
            tx_hash,
        )

        try:

            receipt = self.get_receipt(
                tx_hash,
            )

            if receipt is None:
                return 0

            current_block = (
                self.w3.eth.block_number
            )

            transaction_block = receipt.get(
                "blockNumber",
            )

            if transaction_block is None:
                return 0

            confirmations = (
                current_block
                - transaction_block
                + 1
            )

            return max(
                confirmations,
                0,
            )

        except Exception:

            logger.exception(
                "Failed to calculate transaction confirmations: %s",
                tx_hash,
            )

            return 0

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"connected={self.w3.is_connected()}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "TransactionService",
]


###############################################################################
# End of File
###############################################################################