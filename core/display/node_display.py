"""
Universal Blockchain Platform (UBP)

Module:
    Node Display

Purpose:
    Display node validation results
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display node health reports
    • Show validation results
    • Display node comparison
    • Format node data for user-friendly output

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
    print_warning,
    print_section,
    format_address,
)


class NodeDisplay:
    """
    Node report display formatter.
    """

    @staticmethod
    def display_node_report(report: Dict[str, Any]) -> None:
        """
        Display a formatted node validation report.

        Parameters
        ----------
        report : dict
            Node validation report.
        """
        print_header("🖥️  NODE VALIDATION REPORT", "=", 60)

        # Connection Status
        print_section("🔗 Connection Status", "-", 40)
        connected = report.get('is_connected', False)
        print(f"  Status:           {'✅ Connected' if connected else '❌ Disconnected'}")
        print(f"  Response Time:    {report.get('response_time_ms', 'N/A')} ms")
        print()

        # Node Information
        print_section("📌 Node Information", "-", 40)
        print(f"  Client Version:   {report.get('client_version', 'N/A')}")
        print(f"  Protocol Version: {report.get('protocol_version', 'N/A')}")
        print(f"  Node Type:        {report.get('node_type', 'N/A')}")
        print(f"  Archive Node:     {'✅ Yes' if report.get('is_archive') else '❌ No'}")
        print()

        # Network Information
        print_section("🌐 Network Information", "-", 40)
        print(f"  Chain ID:         {report.get('chain_id', 'N/A')}")
        print(f"  Network ID:       {report.get('network_id', 'N/A')}")
        print(f"  Block Number:     {report.get('block_number', 'N/A')}")
        print(f"  Gas Price:        {report.get('gas_price', 'N/A')} Gwei")
        print()

        # Sync Status
        print_section("🔄 Sync Status", "-", 40)
        is_syncing = report.get('is_syncing', False)
        print(f"  Syncing:          {'🔄 Yes' if is_syncing else '✅ No'}")
        
        sync_progress = report.get('details', {}).get('sync_progress', {})
        if sync_progress:
            print(f"  Current Block:    {sync_progress.get('current_block', 'N/A')}")
            print(f"  Highest Block:    {sync_progress.get('highest_block', 'N/A')}")
            print(f"  Progress:         {report.get('details', {}).get('sync_percentage', 'N/A')}%")
        print()

        # Peer Information
        print_section("👥 Peer Information", "-", 40)
        peer_count = report.get('peer_count', 0)
        if peer_count >= 0:
            print(f"  Peer Count:       {peer_count}")
        else:
            print(f"  Peer Count:       Not available")
        print()

        # Performance
        performance = report.get('details', {}).get('performance', {})
        if performance:
            print_section("⚡ Performance Metrics", "-", 40)
            print(f"  Block Retrieval:  {performance.get('block_retrieval_ms', 'N/A')} ms")
            print(f"  Balance Retrieval:{performance.get('balance_retrieval_ms', 'N/A')} ms")
            print(f"  Average Response: {performance.get('average_response_ms', 'N/A')} ms")
            print()

        # Health Status
        print_section("🏥 Health Status", "-", 40)
        health = report.get('health_status', 'Unknown')
        
        if "Healthy" in health:
            print_success(f"  Status:           {health}")
        elif "Degraded" in health:
            print_warning(f"  Status:           {health}")
        else:
            print_error(f"  Status:           {health}")
        
        issues = report.get('issues', [])
        if issues:
            print(f"\n  Issues Found:")
            for issue in issues:
                print_error(f"    • {issue}")
        else:
            print_info("  No issues detected")
        print()

        print_success("Node validation completed!")

    @staticmethod
    def display_node_comparison(comparison: Dict[str, Any]) -> None:
        """
        Display a node comparison report.

        Parameters
        ----------
        comparison : dict
            Node comparison report.
        """
        print_header("🔄 NODE COMPARISON REPORT", "=", 60)

        print_section("📊 Summary", "-", 40)
        print(f"  Nodes Checked:    {comparison.get('nodes_checked', 0)}")
        print(f"  Nodes Connected:  {comparison.get('nodes_connected', 0)}")
        print(f"  Same Chain:       {'✅ Yes' if comparison.get('same_chain') else '❌ No'}")
        print(f"  Block Consistent: {'✅ Yes' if comparison.get('block_height_consistent') else '❌ No'}")
        print(f"  Consensus:        {comparison.get('consensus_status', 'Unknown')}")
        print()

        # Block comparison
        latest_blocks = comparison.get('latest_blocks', {})
        if latest_blocks:
            print_section("📊 Block Height Comparison", "-", 40)
            for url, block in latest_blocks.items():
                # Truncate long URLs for display
                if len(url) > 50:
                    display_url = url[:47] + "..."
                else:
                    display_url = url
                print(f"  {display_url} -> {block}")
            print(f"\n  Block Difference: {comparison.get('block_difference', 0)} blocks")
            print()

        # Individual results
        results = comparison.get('results', [])
        if results:
            print_section("📋 Individual Results", "-", 40)
            for i, result in enumerate(results, 1):
                status = '✅' if result.get('is_connected') else '❌'
                health = result.get('health_status', 'Unknown')
                rpc_url = result.get('rpc_url', 'Unknown')
                if len(rpc_url) > 45:
                    rpc_url = rpc_url[:42] + "..."
                print(f"  {i}. {status} {rpc_url}")
                print(f"     Health: {health}, Block: {result.get('block_number', 'N/A')}")
                if result.get('error'):
                    print_error(f"     Error: {result.get('error')}")
            print()

        # Consensus verdict
        print_section("⚖️ Consensus Verdict", "-", 40)
        if comparison.get('same_chain') and comparison.get('block_height_consistent'):
            print_success("  ✅ All nodes are in consensus!")
            print_info("  The network is operating normally.")
        else:
            if not comparison.get('same_chain'):
                print_error("  ❌ Nodes are on different chains!")
                print_info("  Chain IDs: {}".format(comparison.get('chain_ids', [])))
            if not comparison.get('block_height_consistent'):
                print_warning("  ⚠️  Nodes have different block heights!")
                print_info(f"  Block difference: {comparison.get('block_difference', 0)} blocks")
        print()

        print_success("Node comparison completed!")

    @staticmethod
    def display_health_summary(report: Dict[str, Any]) -> None:
        """
        Display a compact health summary.

        Parameters
        ----------
        report : dict
            Node validation report.
        """
        health = report.get('health_status', 'Unknown')
        connected = '✅' if report.get('is_connected') else '❌'
        block = report.get('block_number', 'N/A')
        node_type = report.get('node_type', 'Unknown')

        print(f"🖥️  {connected} {health} | Block: {block} | Type: {node_type}")
