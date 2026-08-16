"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.report_service

Purpose
-------
Ethereum transaction reporting service.

This service converts Ethereum transaction domain objects into structured
human-readable and API-friendly reports.

Responsibilities
----------------
- Generate transaction summaries
- Format transaction status
- Format gas information
- Produce reporting objects
- Prepare controller-ready responses

This service does NOT:
- Connect to blockchain nodes
- Decode RPC responses
- Sign transactions
- Broadcast transactions

Architecture
------------

    EthereumTransaction Model
              |
              ▼
    EthereumReportService
              |
              ▼
    Transaction Reports
              |
              ▼
    Controllers / APIs

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

from core.logger import get_logger
from models.ethereum.transaction import EthereumTransaction


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# Ethereum Report Service
###############################################################################


class EthereumReportService:
    """
    Enterprise Ethereum transaction reporting service.

    Converts EthereumTransaction objects into structured reports.
    """

    ###########################################################################
    # Constructor
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize Ethereum report service.
        """

        logger.info(
            "EthereumReportService initialized."
        )

    ###########################################################################
    # Basic Transaction Summary
    ###########################################################################

    def transaction_summary(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Generate a basic Ethereum transaction summary.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Transaction summary.
        """

        logger.info(
            "Generating transaction summary."
        )

        return {
            "hash": transaction.tx_hash,

            "network": transaction.network,

            "asset": transaction.asset,

            "amount": str(
                transaction.amount,
            ),

            "status": self.format_status(
                transaction.status,
            ),

            "type": transaction.transaction_type.value,

            "sender": self.format_address(
                transaction.sender.address,
            ),

            "receiver": self.format_address(
                transaction.receiver.address,
            ),
        }

    ###########################################################################
    # Status Formatting
    ###########################################################################

    def format_status(
        self,
        status: Any,
    ) -> str:
        """
        Convert transaction status into display format.

        Parameters
        ----------
        status : Any
            Transaction status value or enum.

        Returns
        -------
        str
            Uppercase status representation.
        """

        try:

            return status.value.upper()

        except Exception:

            return str(
                status,
            ).upper()

    ###########################################################################
    # Address Formatting
    ###########################################################################

    def format_address(
        self,
        address: str,
        visible_chars: int = 8,
    ) -> str:
        """
        Shorten blockchain addresses for reports.

        Parameters
        ----------
        address : str
            Blockchain address.

        visible_chars : int
            Number of characters displayed at each end.

        Returns
        -------
        str
            Formatted blockchain address.

        Example
        -------
        0x742d35Cc...12345678
        """

        if not address:
            return "UNKNOWN"

        if len(address) <= visible_chars * 2:
            return address

        return (
            address[:visible_chars]
            + "..."
            + address[-visible_chars:]
        )

    ###########################################################################
    # Value Formatting
    ###########################################################################

    def format_amount(
        self,
        amount: Any,
        asset: str = "ETH",
    ) -> str:
        """
        Format transaction value.

        Parameters
        ----------
        amount : Any
            Transaction amount.

        asset : str
            Asset symbol.

        Returns
        -------
        str
            Formatted amount.
        """

        return f"{amount} {asset}"


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Gas Report
    ###########################################################################

    def gas_report(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Generate gas usage report.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Gas usage information.
        """

        logger.info(
            "Generating gas report."
        )

        gas = transaction.gas

        return {
            "gas_limit": gas.gas_limit,

            "gas_used": gas.gas_used,

            "gas_price": gas.gas_price,

            "max_fee_per_gas": (
                gas.max_fee_per_gas
            ),

            "max_priority_fee_per_gas": (
                gas.max_priority_fee_per_gas
            ),

            "effective_gas_price": (
                gas.effective_gas_price
            ),

            "efficiency": (
                self.calculate_gas_efficiency(
                    gas.gas_limit,
                    gas.gas_used,
                )
            ),
        }

    ###########################################################################
    # Gas Efficiency
    ###########################################################################

    def calculate_gas_efficiency(
        self,
        gas_limit: int,
        gas_used: int | None,
    ) -> float | None:
        """
        Calculate gas utilization percentage.

        Parameters
        ----------
        gas_limit : int
            Transaction gas limit.

        gas_used : int | None
            Actual gas used.

        Returns
        -------
        float | None
            Gas utilization percentage, rounded to two decimals.
        """

        if not gas_used:
            return None

        if gas_limit == 0:
            return None

        return round(
            (
                gas_used
                /
                gas_limit
            )
            * 100,
            2,
        )

    ###########################################################################
    # Receipt Report
    ###########################################################################

    def receipt_report(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Generate blockchain receipt report.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Receipt information.
        """

        receipt = transaction.receipt

        if receipt is None:

            return {
                "available": False,
                "status": "PENDING",
            }

        return {
            "available": True,

            "block_number": (
                receipt.block_number
            ),

            "block_hash": (
                receipt.block_hash
            ),

            "status": self.format_status(
                receipt.status,
            ),

            "gas_used": (
                receipt.gas_used
            ),

            "contract_address": (
                receipt.contract_address
            ),

            "logs_count": len(
                receipt.logs
            ),
        }

    ###########################################################################
    # Contract Analysis
    ###########################################################################

    def contract_analysis(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Identify contract activity.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Contract interaction information.
        """

        is_contract = (
            transaction.contract_address is not None
            or
            transaction.transaction_type.value
            == "CONTRACT_CALL"
        )

        return {
            "contract_interaction": is_contract,

            "contract_address": (
                transaction.contract_address
            ),
        }

    ###########################################################################
    # Transaction Health
    ###########################################################################

    def transaction_health(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Produce basic transaction health indicators.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Transaction health indicators.
        """

        return {
            "confirmed": (
                transaction.status.value
                == "CONFIRMED"
            ),

            "has_receipt": (
                transaction.receipt is not None
            ),

            "has_contract": (
                transaction.contract_address
                is not None
            ),

            "gas_available": (
                transaction.gas is not None
            ),
        }


###############################################################################
# End of Part 2
###############################################################################
     ###########################################################################
    # Full Transaction Report
    ###########################################################################

    def generate_report(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Generate complete Ethereum transaction report.

        Combines:

        - Basic summary
        - Gas analysis
        - Receipt information
        - Contract analysis
        - Health indicators

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            Complete transaction report.
        """

        logger.info(
            "Generating complete Ethereum transaction report."
        )

        return {
            "transaction": self.transaction_summary(
                transaction,
            ),

            "gas": self.gas_report(
                transaction,
            ),

            "receipt": self.receipt_report(
                transaction,
            ),

            "contract": self.contract_analysis(
                transaction,
            ),

            "health": self.transaction_health(
                transaction,
            ),
        }

    ###########################################################################
    # API Serialization
    ###########################################################################

    def to_api_response(
        self,
        transaction: EthereumTransaction,
    ) -> dict[str, Any]:
        """
        Generate controller/API response format.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        dict[str, Any]
            API-ready response.
        """

        return {
            "success": True,

            "data": self.generate_report(
                transaction,
            ),
        }

    ###########################################################################
    # Text Report
    ###########################################################################

    def generate_text_report(
        self,
        transaction: EthereumTransaction,
    ) -> str:
        """
        Generate human-readable transaction report.

        Parameters
        ----------
        transaction : EthereumTransaction
            Ethereum transaction model.

        Returns
        -------
        str
            Human-readable transaction report.
        """

        report = self.generate_report(
            transaction,
        )

        tx = report["transaction"]
        gas = report["gas"]
        receipt = report["receipt"]

        return f"""
==================================================
          ETHEREUM TRANSACTION REPORT
==================================================

Hash:
{tx["hash"]}

Network:
{tx["network"]}

Type:
{tx["type"]}

Status:
{tx["status"]}

FROM:
{tx["sender"]}

TO:
{tx["receiver"]}

VALUE:
{tx["amount"]}

---------------- GAS ----------------

Gas Limit:
{gas["gas_limit"]}

Gas Used:
{gas["gas_used"]}

Gas Efficiency:
{gas["efficiency"]}%

---------------- RECEIPT ----------------

Block:
{receipt.get("block_number")}

Logs:
{receipt.get("logs_count")}

==================================================
"""

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
            f"{self.__class__.__name__}()"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "EthereumReportService",
]


###############################################################################
# End of File
###############################################################################  