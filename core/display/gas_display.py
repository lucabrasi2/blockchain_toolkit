"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
core.display.gas_display

Purpose
-------
Gas price display formatter.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from typing import Dict, Any

from core.display.utils import (
    print_header,
    print_section,
    print_bold,
    print_success,
    print_info,
    print_warning,
    print_divider,
)


class GasDisplay:
    """
    Gas price display formatter.
    """

    @staticmethod
    def display_gas_info(gas_info: Dict[str, Any]) -> None:
        """
        Display gas price information.

        Parameters
        ----------
        gas_info : dict
            Gas price information.
        """
        print_header("⛽ GAS PRICE REPORT", "=", 60)

        # Get values
        wei = gas_info.get('wei', 0)
        gwei = gas_info.get('gwei', 0)
        eth = gas_info.get('eth', 0)

        print_section("📌 Gas Information", "-", 40)

        # Wei (with commas for readability)
        print(f"  Gas Price (Wei):  {wei:,.0f}")

        # Gwei (with 4 decimal places for accuracy)
        print(f"  Gas Price (Gwei): {gwei:.4f}")

        # ETH (with 12 decimal places for accuracy)
        print(f"  Gas Price (ETH):  {eth:.12f}")

        # Status indicator
        if gwei < 1:
            print_info("  💡 Gas price is very low - excellent time to transact!")
        elif gwei < 10:
            print_info("  💡 Gas price is low - good time to transact!")
        elif gwei < 30:
            print_info("  📊 Gas price is average")
        elif gwei < 60:
            print_warning("  ⚠️  Gas price is elevated")
        else:
            print_warning("  🔥 Gas price is high - consider waiting")

        print()

        # Show Gwei in a more readable format
        print_section("📊 Quick Reference", "-", 40)
        print(f"  Current Gwei:     {gwei:.4f} Gwei")
        print(f"  In Wei:           {wei:,}")
        print(f"  USD Estimate:     ${gas_info.get('usd_estimate', 0):.4f} (approx)")

        print()
        print_success("✅ Gas price information displayed successfully!")

    @staticmethod
    def display_gas_estimate(estimate: Dict[str, Any]) -> None:
        """
        Display gas cost estimate.

        Parameters
        ----------
        estimate : dict
            Gas cost estimate.
        """
        print_header("⛽ GAS COST ESTIMATE", "=", 60)

        print_section("📊 Estimate Details", "-", 40)
        print(f"  Gas Limit:       {estimate.get('gas_limit', 0):,}")
        print(f"  Gas Price:       {estimate.get('gas_price_gwei', 0):.4f} Gwei")
        print(f"  Total Cost:      {estimate.get('total_cost_eth', 0):.12f} ETH")
        print(f"  Cost (USD):      ${estimate.get('total_cost_usd', 0):.4f}")

        print()
        print_success("✅ Gas estimate completed successfully!")

    @staticmethod
    def display_optimal_gas(recommendation: Dict[str, Any]) -> None:
        """
        Display optimal gas price recommendations.

        Parameters
        ----------
        recommendation : dict
            Gas price recommendations.
        """
        print_header("⛽ OPTIMAL GAS PRICE", "=", 60)

        print_section("📊 Recommendations", "-", 40)
        print(f"  Urgency:         {recommendation.get('urgency', 'standard').upper()}")

        current = recommendation.get('current_gwei', 0)
        recommended = recommendation.get('recommended_gwei', 0)

        print(f"  Current Price:   {current:.4f} Gwei")
        print(f"  Recommended:     {recommended:.4f} Gwei")

        if recommended < current:
            print_info(f"  💡 Save {current - recommended:.4f} Gwei by waiting")
        elif recommended > current:
            print_warning(f"  ⚠️  Pay {recommended - current:.4f} Gwei extra for speed")

        print(f"  Est. Time:       {recommendation.get('estimated_time', 'unknown')}")

        print()
        print_info("💡 Tip: Standard urgency is usually best for most transactions")
        print_success("✅ Optimal gas recommendations displayed!")

    @staticmethod
    def display_gas_summary(optimizer) -> None:
        """
        Display a complete gas summary.

        Parameters
        ----------
        optimizer : GasOptimizer
            Gas optimizer instance.
        """
        gas_info = optimizer.get_gas_price()
        GasDisplay.display_gas_info(gas_info)

        # Show estimates for different urgencies
        print_section("⏱️  Speed vs Cost", "-", 40)
        for urgency in ["slow", "standard", "fast", "instant"]:
            rec = optimizer.get_optimal_gas_price(urgency)
            print(f"  {urgency.title()}: {rec['recommended_gwei']:.4f} Gwei → {rec['estimated_time']}")

        print()
        print_success("✅ Gas optimization complete!")


###############################################################################
# End of File
###############################################################################