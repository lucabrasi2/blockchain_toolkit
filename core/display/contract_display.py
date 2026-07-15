"""
Universal Blockchain Platform (UBP)

Module:
    Contract Display

Purpose:
    Display contract inspection results
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted contract reports
    • Show contract metadata
    • Display token information
    • Format contract data for user-friendly output

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
    format_wei,
    print_section,
)


class ContractDisplay:
    """
    Contract report display formatter.
    """

    @staticmethod
    def display_contract_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted contract report.

        Parameters
        ----------
        report : dict
            Contract inspection report.
        """
        print_header("📄 CONTRACT REPORT", "=", 60)

        # Basic Information
        print_section("📌 Basic Information", "-", 40)
        print(f"  Address:          {format_address(report.get('address', 'N/A'))}")
        print(f"  Full Address:     {report.get('address', 'N/A')}")
        print(f"  Is Contract:      {'✅ Yes' if report.get('is_contract') else '❌ No'}")
        print(f"  Classification:   {report.get('classification', 'Unknown')}")
        print(f"  Contract Type:    {report.get('contract_type', 'N/A')}")
        print(f"  Bytecode Size:    {report.get('bytecode_size', 0)} bytes")
        print()

        # Balance Information
        print_section("💰 Balance Information", "-", 40)
        print(f"  Balance (ETH):    {format_balance(report.get('balance_eth', 0))} ETH")
        print(f"  Balance (WEI):    {format_wei(report.get('balance_wei', 0))} WEI")
        print()

        # Network Information
        print_section("🔗 Network Information", "-", 40)
        print(f"  Nonce:            {report.get('nonce', 0)}")
        print()

        # Metadata
        metadata = report.get('metadata', {})
        if metadata:
            print_section("📝 Contract Metadata", "-", 40)

            name = metadata.get('name')
            if name:
                print(f"  Name:            {name}")

            symbol = metadata.get('symbol')
            if symbol:
                print(f"  Symbol:          {symbol}")

            decimals = metadata.get('decimals')
            if decimals is not None:
                print(f"  Decimals:        {decimals}")

            total_supply = metadata.get('total_supply')
            if total_supply is not None:
                print(f"  Total Supply:    {total_supply:,}")

            owner = metadata.get('owner')
            if owner:
                print(f"  Owner:           {owner}")

            version = metadata.get('version')
            if version:
                print(f"  Version:         {version}")

            standard = metadata.get('standard')
            if standard:
                print(f"  Standard:        {standard}")

            chain_id = metadata.get('chain_id')
            if chain_id:
                print(f"  Chain ID:        {chain_id}")

            block_number = metadata.get('block_number')
            if block_number:
                print(f"  Block Number:    {block_number}")

            print()
        else:
            print_info("No metadata available for this contract.")
            print()

        print_success("Contract inspection completed successfully!")

    @staticmethod
    def display_contract_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact contract summary.

        Parameters
        ----------
        report : dict
            Contract inspection report.
        """
        address = report.get('address', 'N/A')
        contract_type = report.get('contract_type', 'N/A')
        balance = report.get('balance_eth', 0)

        print(f"📄 {format_address(address)} | {contract_type} | {format_balance(balance)} ETH")
