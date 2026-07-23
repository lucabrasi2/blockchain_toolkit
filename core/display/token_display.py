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
        if report.get("error"):
            print_info(f"Error: {report.get('error')}")
            return

        print_header("💱 TOKEN REPORT", "=", 60)

        # Basic Information
        print_section("📌 Basic Information", "-", 40)
        print(f"  Address:          {format_address(report.get('address', 'N/A'))}")
        print(f"  Full Address:     {report.get('address', 'N/A')}")
        print(f"  Name:             {report.get('name', 'Unknown')}")
        print(f"  Symbol:           {report.get('symbol', 'Unknown')}")
        print(f"  Decimals:         {report.get('decimals', 'N/A')}")
        print()

        # Supply Information
        print_section("📊 Supply Information", "-", 40)
        total_supply = report.get('total_supply', 'N/A')
        if total_supply != 'N/A':
            print(f"  Total Supply:     {total_supply:,}")
        else:
            print(f"  Total Supply:     N/A")
        print(f"  Circulating:      {report.get('circulating_supply', 'N/A')}")
        print()

        # Balance Information (if available)
        balance = report.get('balance')
        if balance is not None:
            print_section("💰 Balance Information", "-", 40)
            print(f"  Balance:          {format_balance(balance)}")
            print()

        # Token status
        if report.get('is_token', False):
            print_success("✅ Token is valid and verified")
        else:
            print_info("⚠️  Token information may be incomplete")

        print_success("Token inspection completed successfully!")


###############################################################################
# End of File
###############################################################################