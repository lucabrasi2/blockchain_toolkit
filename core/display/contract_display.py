"""
Universal Blockchain Platform (UBP)

Module:
    Contract Display

Purpose:
    Display contract inspection results for supported blockchains.

Responsibilities:
    • Display Ethereum contract reports
    • Display TRON contract reports
    • Display token metadata
    • Automatically detect blockchain type

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.1.0
"""

from typing import Dict, Any

from core.display.utils import (
    print_header,
    print_success,
    print_info,
    print_error,
    print_section,
    format_address,
    format_balance,
    format_wei,
)


class ContractDisplay:
    """
    Contract report display formatter.
    """

    ###########################################################################
    # Public Entry Point
    ###########################################################################

    @staticmethod
    def display_contract_report(report: Dict[str, Any]) -> None:
        """
        Display a blockchain contract report.
        """

        if report is None:
            print_error("Contract report is empty.")
            return

        if report.get("error"):
            print_error(report["error"])
            return

        blockchain = "Ethereum"

        # Detect TRON reports
        if (
            "energy" in report
            or "bandwidth" in report
            or "balance_trx" in report
            or "balance_sun" in report
            or report.get("classification") == "TRC-20 Token"
        ):
            blockchain = "TRON"

        if blockchain == "TRON":
            ContractDisplay._display_tron_contract(report)
        else:
            ContractDisplay._display_ethereum_contract(report)

    ###########################################################################
    # Ethereum Display
    ###########################################################################

    @staticmethod
    def _display_ethereum_contract(report: Dict[str, Any]) -> None:
        """
        Display an Ethereum contract report.
        """

        print_header("📄 CONTRACT REPORT", "=", 60)

        #######################################################################
        # Basic Information
        #######################################################################

        print_section("📌 Basic Information", "-", 40)

        print(
            f"  Address:          {format_address(report.get('address', 'N/A'))}"
        )

        print(
            f"  Full Address:     {report.get('address', 'N/A')}"
        )

        print(
            f"  Is Contract:      {'✅ Yes' if report.get('is_contract') else '❌ No'}"
        )

        print(
            f"  Classification:   {report.get('classification', 'Unknown')}"
        )

        print(
            f"  Contract Type:    {report.get('contract_type', 'N/A')}"
        )

        print(
            f"  Bytecode Size:    {report.get('bytecode_size', 0)} bytes"
        )

        print()

        #######################################################################
        # Balance
        #######################################################################

        print_section("💰 Balance Information", "-", 40)

        print(
            f"  Balance (ETH):    {format_balance(report.get('balance_eth', 0))} ETH"
        )

        print(
            f"  Balance (WEI):    {format_wei(report.get('balance_wei', 0))} WEI"
        )

        print()

        #######################################################################
        # Network
        #######################################################################

        print_section("🔗 Network Information", "-", 40)

        print(
            f"  Nonce:            {report.get('nonce', 0)}"
        )

        print()

        #######################################################################
        # Metadata
        #######################################################################

        metadata = report.get("metadata", {})

        if metadata:

            print_section("📝 Contract Metadata", "-", 40)

            if metadata.get("name"):
                print(f"  Name:             {metadata['name']}")

            if metadata.get("symbol"):
                print(f"  Symbol:           {metadata['symbol']}")

            if metadata.get("decimals") is not None:
                print(f"  Decimals:         {metadata['decimals']}")

            if metadata.get("total_supply") is not None:
                print(
                    f"  Total Supply:     {metadata['total_supply']:,}"
                )

            if metadata.get("owner"):
                print(f"  Owner:            {metadata['owner']}")

            if metadata.get("version"):
                print(f"  Version:          {metadata['version']}")

            if metadata.get("standard"):
                print(f"  Standard:         {metadata['standard']}")

            if metadata.get("chain_id"):
                print(f"  Chain ID:         {metadata['chain_id']}")

            if metadata.get("block_number"):
                print(
                    f"  Block Number:     {metadata['block_number']}"
                )

            print()

        else:

            print_info("No metadata available for this contract.")
            print()

        print_success("Contract inspection completed successfully!")

    ###########################################################################
    # TRON Display
    ###########################################################################

    @staticmethod
    def _display_tron_contract(report: Dict[str, Any]) -> None:
        """
        Display a TRON contract report.
        """

        print_header("🔴 TRON CONTRACT REPORT", "=", 60)

        #######################################################################
        # Basic Information
        #######################################################################

        print_section("📌 Basic Information", "-", 40)

        print(
            f"  Address:          {format_address(report.get('address', 'N/A'))}"
        )

        print(
            f"  Full Address:     {report.get('address', 'N/A')}"
        )

        print(
            f"  Is Contract:      {'✅ Yes' if report.get('is_contract') else '❌ No'}"
        )

        print(
            f"  Classification:   {report.get('classification', 'Unknown')}"
        )
        print()

        #######################################################################
        # TRON Resources
        #######################################################################

        print_section("⚡ Network Resources", "-", 40)

        print(
            f"  Energy:           {report.get('energy', 0)}"
        )

        print(
            f"  Bandwidth:        {report.get('bandwidth', 0)}"
        )

        print()

        #######################################################################
        # Balance
        #######################################################################

        print_section("💰 Balance Information", "-", 40)

        print(
            f"  Balance (TRX):    {report.get('balance_trx', 0):,.6f} TRX"
        )

        print(
            f"  Balance (SUN):    {report.get('balance_sun', 0):,} SUN"
        )

        print()

        #######################################################################
        # Token Metadata
        #######################################################################

        has_metadata = any(
            key in report
            for key in (
                "name",
                "symbol",
                "decimals",
                "total_supply",
            )
        )

        if has_metadata:

            print_section("🪙 Token Metadata", "-", 40)

            if report.get("name"):
                print(
                    f"  Name:             {report['name']}"
                )

            if report.get("symbol"):
                print(
                    f"  Symbol:           {report['symbol']}"
                )

            if report.get("decimals") is not None:
                print(
                    f"  Decimals:         {report['decimals']}"
                )

            if report.get("total_supply") is not None:
                print(
                    f"  Total Supply:     {report['total_supply']:,}"
                )

            if report.get("owner"):
                print(
                    f"  Owner:            {report['owner']}"
                )

            if report.get("standard"):
                print(
                    f"  Standard:         {report['standard']}"
                )

            print()

        else:

            print_info("No metadata available for this contract.")
            print()

        print_success(
            "Contract inspection completed successfully!"
        )

    ###########################################################################
    # Compact Summary
    ###########################################################################

    @staticmethod
    def display_contract_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact contract summary.
        """

        address = report.get("address", "N/A")

        contract_type = report.get(
            "classification",
            report.get("contract_type", "Unknown"),
        )

        if (
            "balance_trx" in report
            or "balance_sun" in report
            or report.get("classification") == "TRC-20 Token"
        ):

            balance = report.get("balance_trx", 0)

            print(
                f"📄 {format_address(address)} | "
                f"{contract_type} | "
                f"{balance:,.6f} TRX"
            )

        else:

            balance = report.get("balance_eth", 0)

            print(
                f"📄 {format_address(address)} | "
                f"{contract_type} | "
                f"{format_balance(balance)} ETH"
            )


###############################################################################
# End of File
###############################################################################