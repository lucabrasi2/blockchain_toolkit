"""
Universal Blockchain Platform (UBP)

Module:
    Wallet Display

Purpose:
    Display Ethereum wallet information
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted wallet reports
    • Show balance information
    • Display transaction count
    • Format wallet data for user-friendly output

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional

from core.display.utils import (
    print_header,
    print_divider,
    print_bold,
    print_success,
    print_info,
    format_address,
    format_balance,
    format_wei,
    print_section,
)


class WalletDisplay:
    """
    Wallet report display formatter.
    """

    @staticmethod
    def display_wallet_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted wallet report.

        Parameters
        ----------
        report : dict
            Wallet inspection report containing:
            - address: Wallet address
            - balance_eth: Balance in ETH
            - balance_wei: Balance in Wei
            - nonce: Transaction nonce
            - is_contract: Whether it's a contract
            - classification: Address classification
            - transaction_count: Total transactions
            - token_balances: List of token balances
        """
        print_header("👛 WALLET REPORT", "=", 60)

        # Basic Information
        print_section("📌 Basic Information", "-", 40)
        print(f"  Address:          {format_address(report.get('address', 'N/A'))}")
        print(f"  Full Address:     {report.get('address', 'N/A')}")
        print(f"  Is Contract:      {'✅ Yes' if report.get('is_contract') else '❌ No'}")
        print(f"  Classification:   {report.get('classification', 'Unknown')}")
        print()

        # Balance Information
        print_section("💰 Balance Information", "-", 40)
        print(f"  Balance (ETH):    {format_balance(report.get('balance_eth', 0))} ETH")
        print(f"  Balance (WEI):    {format_wei(report.get('balance_wei', 0))} WEI")
        print()

        # Network Information
        print_section("🔗 Network Information", "-", 40)
        print(f"  Nonce:            {report.get('nonce', 0)}")
        print(f"  Tx Count:         {report.get('transaction_count', 0)}")
        print()

        # Token Balances
        token_balances = report.get('token_balances', [])
        if token_balances:
            print_section("🪙 Token Balances", "-", 40)
            for token in token_balances:
                print(f"  • {token}")
            print()
        else:
            print_info("No token balances found.")
            print()

        print_success("Wallet inspection completed successfully!")

    @staticmethod
    def display_wallet_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact wallet summary.

        Parameters
        ----------
        report : dict
            Wallet inspection report.
        """
        address = report.get('address', 'N/A')
        balance = report.get('balance_eth', 0)
        classification = report.get('classification', 'Unknown')

        print(f"👛 {format_address(address)} | {format_balance(balance)} ETH | {classification}")

    @staticmethod
    def display_balance_only(balance: Dict[str, Any], address: Optional[str] = None) -> None:
        """
        Display only balance information.

        Parameters
        ----------
        balance : dict
            Balance information with 'ether' and 'wei' keys.
        address : str, optional
            Wallet address to display.
        """
        if address:
            print_header(f"💰 BALANCE FOR {format_address(address)}", "=", 50)
        else:
            print_header("💰 BALANCE", "=", 40)

        print(f"  ETH:  {format_balance(balance.get('ether', 0))}")
        print(f"  WEI:  {format_wei(balance.get('wei', 0))}")
        print()


# Legacy function for backward compatibility
def display_wallet_report(address: str, balance: Dict[str, Any], nonce: int) -> None:
    """
    Legacy function to display a formatted Ethereum wallet report.

    This function is maintained for backward compatibility with
    existing code that expects the old function signature.

    Parameters
    ----------
    address : str
        Ethereum wallet address.
    balance : dict
        Dictionary containing ETH and Wei balances.
    nonce : int
        Transaction count (nonce).
    """
    report = {
        "address": address,
        "balance_eth": balance.get("ether", 0),
        "balance_wei": balance.get("wei", 0),
        "nonce": nonce,
        "is_contract": False,
        "classification": "Unknown",
        "transaction_count": nonce,
        "token_balances": [],
    }
    WalletDisplay.display_wallet_report(report)