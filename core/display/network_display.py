"""
Universal Blockchain Platform (UBP)

Module:
    Network Display

Purpose:
    Display network information
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display formatted network reports
    • Show connection status
    • Display network details
    • Format network data for user-friendly output

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
    print_section,
)


class NetworkDisplay:
    """
    Network report display formatter.
    """

    @staticmethod
    def display_network_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted network report.

        Parameters
        ----------
        report : dict
            Network inspection report containing:
            - network: Network name
            - chain_id: Chain ID
            - block_number: Current block number
            - connected: Connection status
            - provider: Provider name
            - rpc_url: RPC URL
        """
        print_header("🌐 NETWORK REPORT", "=", 60)

        # Network Information
        print_section("📌 Network Information", "-", 40)
        print(f"  Network:          {report.get('network', 'N/A')}")
        print(f"  Chain ID:         {report.get('chain_id', 'N/A')}")
        print(f"  Block Number:     {report.get('block_number', 'N/A')}")
        print()

        # Connection Status
        print_section("🔗 Connection Status", "-", 40)
        connected = report.get('connected', False)
        print(f"  Connected:        {'✅ Yes' if connected else '❌ No'}")
        print(f"  Provider:         {report.get('provider', 'N/A')}")
        print(f"  RPC URL:          {report.get('rpc_url', 'N/A')}")
        print()

        # Additional Info
        print_section("📊 Additional Information", "-", 40)
        print(f"  Gas Price:        {report.get('gas_price', 'N/A')}")
        print(f"  Syncing:          {'✅ Yes' if report.get('syncing') else '❌ No'}")
        print()

        if connected:
            print_success("Network connection is healthy!")
        else:
            print_info("Network is not connected. Please check your RPC URL.")

    @staticmethod
    def display_connection_status(status: Dict[str, Any]) -> None:
        """
        Display connection status.

        Parameters
        ----------
        status : dict
            Connection status information.
        """
        print_section("🔗 Connection Status", "-", 40)
        connected = status.get('connected', False)
        print(f"  Connected:        {'✅ Yes' if connected else '❌ No'}")
        print(f"  Provider:         {status.get('provider', 'N/A')}")
        print(f"  Network:          {status.get('network', 'N/A')}")
        print(f"  Block Number:     {status.get('block_number', 'N/A')}")
        print()

    @staticmethod
    def display_network_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact network summary.

        Parameters
        ----------
        report : dict
            Network inspection report.
        """
        network = report.get('network', 'Unknown')
        block = report.get('block_number', 'N/A')
        connected = '✅' if report.get('connected') else '❌'

        print(f"🌐 {network} | Block: {block} | {connected}")

    @staticmethod
    def display_provider_info(provider: Dict[str, Any]) -> None:
        """
        Display provider information.

        Parameters
        ----------
        provider : dict
            Provider information.
        """
        print_section("🔌 Provider Information", "-", 40)
        print(f"  Name:             {provider.get('name', 'N/A')}")
        print(f"  Type:             {provider.get('type', 'N/A')}")
        print(f"  Status:           {provider.get('status', 'N/A')}")
        print(f"  Endpoint:         {provider.get('endpoint', 'N/A')}")
        print()