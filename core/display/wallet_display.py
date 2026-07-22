"""
Universal Blockchain Platform (UBP)

Module:
    Wallet Display

Purpose:
    Display wallet information for all blockchains.

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
    Wallet report display formatter for all blockchains.
    """

    @staticmethod
    def display_wallet_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted wallet report for any blockchain.

        Parameters
        ----------
        report : dict
            Wallet inspection report.
        """
        # Determine blockchain type from report
        blockchain = report.get("blockchain", "Unknown")
        classification = report.get("classification", "Unknown")
        
        # Set appropriate header emoji
        if "Bitcoin" in classification or "BTC" in str(report.get("balance_btc", "")):
            header = "🟠 BITCOIN WALLET REPORT"
        elif "TRON" in classification or "TRX" in str(report.get("balance_trx", "")):
            header = "🔴 TRON WALLET REPORT"
        else:
            header = "👛 WALLET REPORT"
        
        print_header(header, "=", 60)

        # Basic Information
        print_section("📌 Basic Information", "-", 40)
        print(f"  Address:          {format_address(report.get('address', 'N/A'))}")
        print(f"  Full Address:     {report.get('address', 'N/A')}")
        
        # Show contract status if available
        if "is_contract" in report:
            print(f"  Is Contract:      {'✅ Yes' if report.get('is_contract') else '❌ No'}")
        
        print(f"  Classification:   {classification}")
        print()

        # Balance Information (blockchain-specific)
        print_section("💰 Balance Information", "-", 40)
        
        # Check for Bitcoin
        if "balance_btc" in report:
            print(f"  Balance (BTC):    {format_balance(report.get('balance_btc', 0))} BTC")
            print(f"  Balance (Sats):   {report.get('balance_satoshis', 0):,} SATS")
        
        # Check for TRON
        elif "balance_trx" in report:
            print(f"  Balance (TRX):    {format_balance(report.get('balance_trx', 0))} TRX")
            print(f"  Balance (SUN):    {report.get('balance_sun', 0):,} SUN")
        
        # Default to Ethereum
        else:
            print(f"  Balance (ETH):    {format_balance(report.get('balance_eth', 0))} ETH")
            print(f"  Balance (WEI):    {format_wei(report.get('balance_wei', 0))} WEI")
        
        print()

        # Network Information (blockchain-specific)
        print_section("🔗 Network Information", "-", 40)
        
        # Check for Bitcoin
        if "balance_btc" in report:
            print(f"  Tx Count:         {report.get('transaction_count', 0)}")
        
        # Check for TRON
        elif "balance_trx" in report:
            print(f"  Energy:           {report.get('energy', 0)}")
            print(f"  Bandwidth:        {report.get('bandwidth', 0)}")
        
        # Default to Ethereum
        else:
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
        classification = report.get('classification', 'Unknown')
        
        # Determine blockchain type and balance
        if "balance_btc" in report:
            balance = report.get('balance_btc', 0)
            symbol = "BTC"
        elif "balance_trx" in report:
            balance = report.get('balance_trx', 0)
            symbol = "TRX"
        else:
            balance = report.get('balance_eth', 0)
            symbol = "ETH"

        print(f"👛 {format_address(address)} | {format_balance(balance)} {symbol} | {classification}")

    @staticmethod
    def display_balance_only(balance: Dict[str, Any], address: Optional[str] = None) -> None:
        """
        Display only balance information.

        Parameters
        ----------
        balance : dict
            Balance information.
        address : str, optional
            Wallet address to display.
        """
        if address:
            print_header(f"💰 BALANCE FOR {format_address(address)}", "=", 50)
        else:
            print_header("💰 BALANCE", "=", 40)

        # Check for different blockchain types
        if "btc" in balance or "satoshis" in balance:
            print(f"  BTC:  {format_balance(balance.get('btc', 0))}")
            print(f"  SATS: {balance.get('satoshis', 0):,}")
        elif "trx" in balance or "sun" in balance:
            print(f"  TRX:  {format_balance(balance.get('trx', 0))}")
            print(f"  SUN:  {balance.get('sun', 0):,}")
        else:
            print(f"  ETH:  {format_balance(balance.get('ether', 0))}")
            print(f"  WEI:  {format_wei(balance.get('wei', 0))}")
        
        print()