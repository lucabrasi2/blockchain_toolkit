"""
Universal Blockchain Platform (UBP)

Module:
    Transaction Display

Purpose:
    Display transaction analysis results
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted transaction reports
    • Show transaction details
    • Display transaction status
    • Format transaction data for user-friendly output

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
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
    Transaction report display formatter.
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

        print_header("📊 TRANSACTION REPORT", "=", 60)

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
        print(f"  Status:           {'✅ Success' if report.get('is_success') else '❌ Failed'}")
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

        # Contract Creation (if applicable)
        contract_address = report.get('contract_address')
        if contract_address:
            print_section("📄 Contract Created", "-", 40)
            print(f"  Contract Address: {contract_address}")
            print()

        # Logs
        logs = report.get('logs', [])
        if logs:
            print_section("📋 Logs", "-", 40)
            print(f"  Total Logs:       {len(logs)}")
            for i, log in enumerate(logs[:5], 1):
                print(f"  {i}. Address: {format_address(log.get('address', 'N/A'))}")
            if len(logs) > 5:
                print(f"  ... and {len(logs) - 5} more logs")
            print()

        print_success("Transaction analysis completed successfully!")