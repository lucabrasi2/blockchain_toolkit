"""
Universal Blockchain Platform (UBP)

Module:
    Block Display

Purpose:
    Display block exploration results
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted block reports
    • Show block details
    • List transactions in a block
    • Format block data for user-friendly output

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, List

from core.display.utils import (
    print_header,
    print_divider,
    print_bold,
    print_success,
    print_info,
    print_error,
    format_address,
    print_section,
)


class BlockDisplay:
    """
    Block report display formatter.
    """

    @staticmethod
    def display_block_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted block report.

        Parameters
        ----------
        report : dict
            Block inspection report.
        """
        if report.get("error"):
            print_error(f"Error fetching block: {report.get('error')}")
            return

        print_header("🔍 BLOCK REPORT", "=", 60)

        # Block Information
        print_section("📌 Block Information", "-", 40)
        print(f"  Block Number:     {report.get('number', 'N/A')}")
        print(f"  Block Hash:       {report.get('hash', 'N/A')}")
        print(f"  Parent Hash:      {report.get('parent_hash', 'N/A')}")
        print(f"  Timestamp:        {report.get('timestamp', 'N/A')}")
        print(f"  Transactions:     {report.get('transaction_count', 0)}")
        print()

        # Block Details
        print_section("🔧 Block Details", "-", 40)
        print(f"  Miner:            {format_address(report.get('miner', 'N/A'))}")
        print(f"  Difficulty:       {report.get('difficulty', 'N/A')}")
        print(f"  Gas Used:         {report.get('gas_used', 'N/A')}")
        print(f"  Gas Limit:        {report.get('gas_limit', 'N/A')}")
        print(f"  Size:             {report.get('size', 'N/A')} bytes")
        print()

        # Transactions
        transactions = report.get('transactions', [])
        if transactions:
            print_section("📊 Transactions", "-", 40)
            for i, tx_hash in enumerate(transactions[:10], 1):
                print(f"  {i:2d}. {tx_hash}")
            if len(transactions) > 10:
                print(f"  ... and {len(transactions) - 10} more transactions")
            print()
        else:
            print_info("No transactions in this block.")
            print()

        print_success("Block exploration completed successfully!")