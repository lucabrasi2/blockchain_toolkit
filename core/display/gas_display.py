"""
Universal Blockchain Platform (UBP)

Module:
    Gas Display

Purpose:
    Display Ethereum gas information
    for the Universal Blockchain Platform (UBP).

Responsibilities:
    • Display current gas prices
    • Display gas cost estimates
    • Display gas recommendations
    • Format gas data for user-friendly output

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any

from core.display.utils import (
    print_header,
    print_section,
    print_success,
    print_info,
)


class GasDisplay:
    """
    Ethereum gas report display formatter.
    """

    @staticmethod
    def display_gas_info(report: Dict[str, Any]) -> None:
        """
        Display current gas price information.
        """
        if report.get("error"):
            print_info(f"Error: {report.get('error')}")
            return

        print_header("⛽ CURRENT GAS PRICE", "=", 60)

        print_section("📌 Gas Information", "-", 40)

        wei = report.get("wei", "N/A")
        if isinstance(wei, (int, float)):
            wei = f"{wei:,}"

        print(f"  Gas Price (Wei):   {wei}")
        print(f"  Gas Price (Gwei):  {report.get('gwei', 'N/A')}")
        print(f"  Gas Price (ETH):   {report.get('eth', 'N/A')}")
        print()

        print_success("Gas information retrieved successfully!")

    @staticmethod
    def display_gas_estimate(report: Dict[str, Any]) -> None:
        """
        Display estimated gas cost.
        """
        if report.get("error"):
            print_info(f"Error: {report.get('error')}")
            return

        print_header("⛽ GAS COST ESTIMATE", "=", 60)

        print_section("📌 Estimate", "-", 40)

        gas_limit = report.get("gas_limit", "N/A")
        if isinstance(gas_limit, int):
            gas_limit = f"{gas_limit:,}"

        total_cost_wei = report.get("total_cost_wei", "N/A")
        if isinstance(total_cost_wei, (int, float)):
            total_cost_wei = f"{int(total_cost_wei):,}"

        print(f"  Gas Limit:         {gas_limit}")
        print(f"  Gas Price (Gwei):  {report.get('gas_price_gwei', 'N/A')}")
        print(f"  Total Cost (Wei):  {total_cost_wei}")
        print(f"  Total Cost (ETH):  {report.get('total_cost_eth', 'N/A')}")
        print(f"  Total Cost (USD):  ${report.get('total_cost_usd', 'N/A')}")
        print()

        print_success("Gas cost estimate generated successfully!")

    @staticmethod
    def display_gas_recommendation(report: Dict[str, Any]) -> None:
        """
        Display optimal gas recommendation.
        """
        if report.get("error"):
            print_info(f"Error: {report.get('error')}")
            return

        print_header("⛽ GAS RECOMMENDATION", "=", 60)

        print_section("📊 Recommendation", "-", 40)

        print(f"  Urgency:           {report.get('urgency', 'Standard').title()}")
        print(f"  Current Gas:       {report.get('current_gwei', 'N/A')} Gwei")
        print(f"  Recommended Gas:   {report.get('recommended_gwei', 'N/A')} Gwei")
        print(f"  Estimated Time:    {report.get('estimated_time', 'Unknown')}")
        print()

        print_success("Gas recommendation generated successfully!")


###############################################################################
# End of File
###############################################################################