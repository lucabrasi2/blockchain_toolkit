"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
core.display.transaction_display

Purpose
-------
Transaction display formatter for all blockchains.

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
    print_divider,
    print_bold,
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

        Parameters
        ----------
        report : dict
            Transaction analysis report.
        """
        if report.get("error"):
            print_error(f"Error fetching transaction: {report.get('error')}")
            return

        # Detect blockchain type
        # Bitcoin has confirmations, Ethereum has gas_used
        blockchain = "Ethereum"
        if "confirmations" in report and report.get("confirmations") is not None:
            blockchain = "Bitcoin"
        elif "block_height" in report:
            blockchain = "Bitcoin"
        elif "inputs" in report and "outputs" in report:
            blockchain = "Bitcoin"
        elif "fee" in report and isinstance(report.get("fee"), (int, float)):
            blockchain = "Bitcoin"

        if blockchain == "Bitcoin":
            TransactionDisplay._display_bitcoin_transaction(report)
        else:
            TransactionDisplay._display_ethereum_transaction(report)

    @staticmethod
    def _display_bitcoin_transaction(report: Dict[str, Any]) -> None:
        """
        Display a Bitcoin transaction report.
        """
        print_header("🟠 BITCOIN TRANSACTION REPORT", "=", 60)

        # Basic Information
        print_section("📌 Transaction Information", "-", 40)
        print(f"  Hash:             {report.get('hash', 'N/A')}")
        print(f"  Block Number:     {report.get('block_number', report.get('block_height', 'N/A'))}")
        print(f"  Block Hash:       {report.get('block_hash', 'N/A')}")
        print(f"  Confirmations:    {report.get('confirmations', 0)}")
        print(f"  Timestamp:        {report.get('timestamp', 'N/A')}")
        print()

        # Transaction Details
        print_section("🔧 Transaction Details", "-", 40)
        print(f"  Size:             {report.get('size', 'N/A')} bytes")
        print(f"  Weight:           {report.get('weight', 'N/A')}")
        print(f"  Version:          {report.get('version', 'N/A')}")
        print(f"  Locktime:         {report.get('locktime', 'N/A')}")

        # Fee
        fee = report.get('fee', 0)
        if fee:
            print(f"  Fee (BTC):        {fee}")
        print()

        # Status
        status = report.get('status', 'Unknown')
        if "Confirmed" in status:
            print_success(f"  Status:           ✅ {status}")
        elif "Pending" in status:
            print_info(f"  Status:           ⏳ {status}")
        else:
            print_info(f"  Status:           {status}")
        print()

        # Inputs
        inputs = report.get('inputs', [])
        if inputs:
            print_section("📥 Inputs", "-", 40)
            print(f"  Total Inputs:     {len(inputs)}")
            for i, inp in enumerate(inputs[:5], 1):
                if isinstance(inp, dict):
                    inp_hash = inp.get('hash', 'N/A')
                else:
                    inp_hash = str(inp)
                if len(str(inp_hash)) > 12:
                    inp_hash = inp_hash[:10] + "..."
                print(f"  {i}. {inp_hash}")
            if len(inputs) > 5:
                print(f"  ... and {len(inputs) - 5} more inputs")
            print()

        # Outputs
        outputs = report.get('outputs', [])
        if outputs:
            print_section("📤 Outputs", "-", 40)
            print(f"  Total Outputs:    {len(outputs)}")
            total_input = report.get('total_input', 0)
            if total_input:
                print(f"  Total Value:      {total_input} BTC")
            for i, out in enumerate(outputs[:5], 1):
                if isinstance(out, dict):
                    address = out.get('address', 'N/A')
                    amount = out.get('amount', 0)
                else:
                    address = 'N/A'
                    amount = 0
                print(f"  {i}. {format_address(address)} -> {amount} BTC")
            if len(outputs) > 5:
                print(f"  ... and {len(outputs) - 5} more outputs")
            print()

        print_success("Bitcoin transaction analysis completed successfully!")

    @staticmethod
    def _display_ethereum_transaction(report: Dict[str, Any]) -> None:
        """
        Display an Ethereum transaction report.
        """
        print_header("📊 ETHEREUM TRANSACTION REPORT", "=", 60)

        # Basic Information
        print_section("📌 Transaction Information", "-", 40)
        print(f"  Hash:             {report.get('hash', 'N/A')}")
        print(f"  Block Number:     {report.get('block_number', 'N/A')}")
        print(f"  From:             {format_address(report.get('from', 'N/A'))}")
        print(f"  To:               {format_address(report.get('to', 'N/A'))}")
        print()

        # Transaction Details
        print_section("🔧 Transaction Details", "-", 40)
        print(f"  Value (ETH):      {format_balance(report.get('value', 0))}")
        print(f"  Gas Used:         {report.get('gas_used', 'N/A')}")
        print(f"  Gas Price:        {report.get('gas_price', 'N/A')}")
        print(f"  Nonce:            {report.get('nonce', 'N/A')}")

        # Status
        status = report.get('is_success')
        if status is True:
            print_success("  Status:           ✅ Success")
        elif status is False:
            print_error("  Status:           ❌ Failed")
        else:
            print_info("  Status:           ⏳ Pending")
        print()

        # Contract Creation
        contract_address = report.get('contract_address')
        if contract_address:
            print_section("📄 Contract Created", "-", 40)
            print(f"  Contract Address: {contract_address}")
            print()

        # Input Data
        input_data = report.get('input', '')
        if input_data and input_data != '0x':
            print_section("📝 Input Data", "-", 40)
            if len(input_data) > 100:
                print(f"  {input_data[:100]}...")
            else:
                print(f"  {input_data}")
            print()

        # Logs
        logs = report.get('logs', [])
        if logs:
            print_section("📋 Event Logs", "-", 40)
            print(f"  Total Logs:       {len(logs)}")
            for i, log in enumerate(logs[:5], 1):
                address = log.get('address', 'N/A')
                print(f"  {i}. {format_address(address)}")
            if len(logs) > 5:
                print(f"  ... and {len(logs) - 5} more logs")
            print()

        print_success("Transaction analysis completed successfully!")


###############################################################################
# End of File
###############################################################################