"""
Universal Blockchain Platform (UBP)

Module:
    Token Display

Purpose:
    Display token inspection results
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted token reports
    • Show token metadata
    • Display token balances
    • Format token data for user-friendly output

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
    format_address,
    format_balance,
    print_section,
)


class TokenDisplay:
    """
    Token report display formatter.
    """

    @staticmethod
    def display_token_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted token report.

        Parameters
        ----------
        report : dict
            Token inspection report.
        """
        print_header("💱 TOKEN REPORT", "=", 60)

        # Basic Information
        print_section("📌 Basic Information", "-", 40)
        print(f"  Address:          {format_address(report.get('address', 'N/A'))}")
        print(f"  Full Address:     {report.get('address', 'N/A')}")
        print(f"  Name:             {report.get('name', 'N/A')}")
        print(f"  Symbol:           {report.get('symbol', 'N/A')}")
        print(f"  Decimals:         {report.get('decimals', 'N/A')}")
        print()

        # Supply Information
        print_section("📊 Supply Information", "-", 40)
        print(f"  Total Supply:     {report.get('total_supply', 'N/A')}")
        print(f"  Circulating:      {report.get('circulating_supply', 'N/A')}")
        print()

        # Balance Information (if available)
        balance = report.get('balance')
        if balance is not None:
            print_section("💰 Balance Information", "-", 40)
            print(f"  Balance:          {format_balance(balance)}")
            print()

        print_success("Token inspection completed successfully!")

    @staticmethod
    def display_token_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact token summary.

        Parameters
        ----------
        report : dict
            Token inspection report.
        """
        name = report.get('name', 'Unknown')
        symbol = report.get('symbol', 'N/A')
        address = report.get('address', 'N/A')

        print(f"💱 {symbol} ({name}) | {format_address(address)}")