"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
core.display.transaction_display

Purpose
-------
Transaction display formatter for all supported blockchains.

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

from typing import Dict, Any

from core.display.utils import (
    print_header,
    print_success,
    print_info,
    print_error,
    format_address,
    format_balance,
    print_section,
)


class TransactionDisplay:
    """
    Transaction report display formatter for all blockchains.
    """

    @staticmethod
    def display_transaction_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted transaction report.
        """

        if report is None:
            print_error("Transaction report is empty.")
            return

        if report.get("error"):
            print_error(
                f"Error fetching transaction: {report.get('error')}"
            )
            return

        ####################################################################
        # Enterprise blockchain detection
        ####################################################################

        blockchain = (
            report.get("blockchain", "")
            .strip()
            .lower()
        )

        if blockchain == "bitcoin":

            TransactionDisplay._display_bitcoin_transaction(
                report
            )
            return

        if blockchain == "tron":

            TransactionDisplay._display_tron_transaction(
                report
            )
            return

        ####################################################################
        # Backward compatibility
        ####################################################################

        if (
            "confirmations" in report
            or "inputs" in report
            or "outputs" in report
        ):

            TransactionDisplay._display_bitcoin_transaction(
                report
            )

        else:

            TransactionDisplay._display_ethereum_transaction(
                report
            )

    ###########################################################################
    # BITCOIN
    ###########################################################################

    @staticmethod
    def _display_bitcoin_transaction(
        report: Dict[str, Any],
    ) -> None:
        """
        Display a Bitcoin transaction report.
        """

        print_header(
            "🟠 BITCOIN TRANSACTION REPORT",
            "=",
            60,
        )

        ####################################################################
        # Transaction Information
        ####################################################################

        print_section(
            "📌 Transaction Information",
            "-",
            40,
        )

        print(
            f"  Hash:             {report.get('hash', 'N/A')}"
        )

        print(
            "  Block Number:     "
            f"{report.get('block_number', report.get('block_height', 'N/A'))}"
        )

        print(
            "  Block Hash:       "
            f"{report.get('block_hash') or 'Not available'}"
        )

        print(
            f"  Confirmations:    {report.get('confirmations', 0)}"
        )

        print(
            f"  Timestamp:        {report.get('timestamp', 'N/A')}"
        )

        print()

        ####################################################################
        # Transaction Details
        ####################################################################

        print_section(
            "🔧 Transaction Details",
            "-",
            40,
        )

        print(
            f"  Size:             {report.get('size', 'N/A')} bytes"
        )

        print(
            f"  Weight:           {report.get('weight', 'N/A')}"
        )

        print(
            f"  Version:          {report.get('version', 'N/A')}"
        )

        print(
            f"  Locktime:         {report.get('locktime', 'N/A')}"
        )

        fee = report.get("fee")

        if fee not in (None, ""):

            print(
                f"  Fee:              {fee}"
            )

        print()

        ####################################################################
        # Status
        ####################################################################

        status = report.get(
            "status",
            "Unknown",
        )

        if "Confirmed" in str(status):

            print_success(
                f"  Status:           ✅ {status}"
            )

        elif "Pending" in str(status):

            print_info(
                f"  Status:           ⏳ {status}"
            )

        else:

            print_info(
                f"  Status:           {status}"
            )

        print()

        ####################################################################
        # Inputs
        ####################################################################

        inputs = report.get(
            "inputs",
            [],
        )

        if inputs:

            print_section(
                "📥 Inputs",
                "-",
                40,
            )

            print(
                f"  Total Inputs:     {len(inputs)}"
            )

            for index, tx_input in enumerate(inputs[:5], 1):

                if not isinstance(tx_input, dict):

                    print(
                        f"  {index}. Unknown"
                    )

                    continue

                address = tx_input.get("address")

                if (
                    not address
                    or address in (
                        "Unknown",
                        "N/A",
                    )
                ):

                    print(
                        f"  {index}. Coinbase (Mining Reward)"
                    )

                else:

                    value = tx_input.get(
                        "value",
                        0,
                    )

                    print(
                        f"  {index}. "
                        f"{format_address(address)} "
                        f"({value:.8f} BTC)"
                    )

            if len(inputs) > 5:

                print(
                    f"  ... and {len(inputs)-5} more inputs"
                )

            print()

        ####################################################################
        # Outputs
        ####################################################################

        outputs = report.get(
            "outputs",
            [],
        )

        if outputs:

            print_section(
                "📤 Outputs",
                "-",
                40,
            )

            print(
                f"  Total Outputs:    {len(outputs)}"
            )

            print(
                "  Total Output:     "
                f"{report.get('total_output',0):.8f} BTC"
            )

            for index, output in enumerate(outputs[:5], 1):

                if not isinstance(output, dict):
                    continue

                address = (
                    output.get("address")
                    or "Unknown"
                )

                value = output.get(
                    "value",
                    0,
                )

                print(
                    f"  {index}. "
                    f"{format_address(address)} "
                    f"-> {value:.8f} BTC"
                )

            if len(outputs) > 5:

                print(
                    f"  ... and {len(outputs)-5} more outputs"
                )

            print()

        print_success(
            "Bitcoin transaction analysis completed successfully!"
        )
        ###########################################################################
    # ETHEREUM
    ###########################################################################

    @staticmethod
    def _display_ethereum_transaction(
        report: Dict[str, Any],
    ) -> None:
        """
        Display an Ethereum transaction report.
        """

        print_header(
            "📊 ETHEREUM TRANSACTION REPORT",
            "=",
            60,
        )

        print_section(
            "📌 Transaction Information",
            "-",
            40,
        )

        print(
            f"  Hash:             {report.get('hash', 'N/A')}"
        )

        print(
            f"  Block Number:     {report.get('block_number', 'Pending')}"
        )

        print(
            f"  From:             {format_address(report.get('from', 'N/A'))}"
        )

        print(
            f"  To:               {format_address(report.get('to', 'N/A'))}"
        )

        print()

        print_section(
            "🔧 Transaction Details",
            "-",
            40,
        )

        value = report.get("value", 0)

        if isinstance(value, (int, float)):
            value = float(value)

        else:
            value = 0.0

        print(
            f"  Value (ETH):      {value:.6f}"
        )

        print(
            f"  Gas Used:         {report.get('gas_used', 'N/A')}"
        )

        print(
            f"  Gas Price:        {report.get('gas_price', 'N/A')}"
        )

        print(
            f"  Nonce:            {report.get('nonce', 'N/A')}"
        )

        print()

        success = report.get("is_success")

        if success is True:

            print_success(
                "  Status:           ✅ Confirmed"
            )

        elif success is False:

            print_error(
                "  Status:           ❌ Failed"
            )

        else:

            print_info(
                "  Status:           ⏳ Pending"
            )

        print()

        print_success(
            "Transaction analysis completed successfully!"
        )

    ###########################################################################
    # TRON
    ###########################################################################

    @staticmethod
    def _display_tron_transaction(
        report: Dict[str, Any],
    ) -> None:
        """
        Display a TRON transaction report.
        """

        print_header(
            "🔴 TRON TRANSACTION REPORT",
            "=",
            60,
        )

        ####################################################################
        # Transaction Information
        ####################################################################

        print_section(
            "📌 Transaction Information",
            "-",
            40,
        )

        print(
            f"  Hash:             {report.get('hash', 'N/A')}"
        )

        print(
            f"  Block Number:     {report.get('block_number', 'Pending')}"
        )

        print(
            f"  From:             {format_address(report.get('from', 'N/A'))}"
        )

        print(
            f"  To:               {format_address(report.get('to', 'N/A'))}"
        )

        timestamp = report.get("timestamp")

        if timestamp is not None:

            print(
                f"  Timestamp:        {timestamp}"
            )

        print()

        ####################################################################
        # Transaction Details
        ####################################################################

        print_section(
            "🔧 Transaction Details",
            "-",
            40,
        )

        amount = report.get(
            "amount",
            report.get("value", 0),
        )

        try:
            trx_amount = float(amount) / 1_000_000

        except Exception:

            trx_amount = 0.0

        print(
            f"  Amount (TRX):     {trx_amount:.6f}"
        )

        fee = report.get("fee")

        if fee is not None:

            try:
                print(
                    f"  Fee (TRX):        {float(fee)/1_000_000:.6f}"
                )

            except Exception:

                print(
                    f"  Fee:              {fee}"
                )

        energy = report.get("energy_used")

        if energy is not None:

            print(
                f"  Energy Used:      {energy}"
            )

        bandwidth = report.get("bandwidth_used")

        if bandwidth is not None:

            print(
                f"  Bandwidth Used:   {bandwidth}"
            )

        contract_result = report.get("status")

        if contract_result:

            print(
                f"  Contract Result:  {contract_result}"
            )

        print()

        ####################################################################
        # Status
        ####################################################################

        success = report.get("is_success")

        if success is True:

            print_success(
                "  Status:           ✅ Confirmed"
            )

        elif success is False:

            print_error(
                "  Status:           ❌ Failed"
            )

        else:

            status = report.get(
                "status",
                "Pending",
            )

            print_info(
                f"  Status:           ⏳ {status}"
            )

        print()

        print_success(
            "TRON transaction analysis completed successfully!"
        )


###############################################################################
# End of File
###############################################################################