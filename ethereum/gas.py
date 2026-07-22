"""
Universal Blockchain Platform (UBP)

Module:
    Gas Price Optimization

Purpose:
    Analyze and optimize Ethereum gas prices.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Dict, Any, Optional
from web3 import Web3

from ethereum.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


class GasOptimizer:
    """
    Gas price optimization and analysis.
    """

    def __init__(self):
        self.w3 = get_connection()

    def get_gas_price(self) -> Dict[str, Any]:
        """
        Get current gas price information.

        Returns
        -------
        Dict[str, Any]
            Gas price in various units.
        """
        try:
            gas_price_wei = self.w3.eth.gas_price
            gas_price_gwei = gas_price_wei / 1_000_000_000

            return {
                "wei": gas_price_wei,
                "gwei": round(gas_price_gwei, 2),
                "eth": round(gas_price_gwei / 1_000_000_000, 9),
            }
        except Exception as error:
            logger.error(f"Error getting gas price: {error}")
            return {"wei": 0, "gwei": 0, "eth": 0}

    def estimate_gas_cost(
        self,
        gas_limit: int = 21000,
        gas_price_gwei: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Estimate transaction gas cost.

        Parameters
        ----------
        gas_limit : int
            Gas limit for the transaction.
        gas_price_gwei : float, optional
            Gas price in Gwei. If None, uses current gas price.

        Returns
        -------
        Dict[str, Any]
            Estimated gas cost.
        """
        try:
            if gas_price_gwei is None:
                gas_price_gwei = self.get_gas_price()["gwei"]

            gas_price_wei = gas_price_gwei * 1_000_000_000
            total_cost_wei = gas_limit * gas_price_wei
            total_cost_eth = total_cost_wei / 1_000_000_000_000_000_000
            total_cost_usd = total_cost_eth * 3000  # Approximate ETH price

            return {
                "gas_limit": gas_limit,
                "gas_price_gwei": gas_price_gwei,
                "total_cost_wei": total_cost_wei,
                "total_cost_eth": round(total_cost_eth, 6),
                "total_cost_usd": round(total_cost_usd, 2),
            }
        except Exception as error:
            logger.error(f"Error estimating gas cost: {error}")
            return {"error": str(error)}

    def get_optimal_gas_price(
        self,
        urgency: str = "standard"
    ) -> Dict[str, Any]:
        """
        Get optimal gas price based on urgency.

        Parameters
        ----------
        urgency : str
            'slow', 'standard', 'fast', or 'instant'

        Returns
        -------
        Dict[str, Any]
            Optimal gas price recommendations.
        """
        base_gwei = self.get_gas_price()["gwei"]

        multipliers = {
            "slow": 0.8,
            "standard": 1.0,
            "fast": 1.3,
            "instant": 1.6,
        }

        multiplier = multipliers.get(urgency, 1.0)
        optimal_gwei = base_gwei * multiplier

        return {
            "urgency": urgency,
            "current_gwei": base_gwei,
            "recommended_gwei": round(optimal_gwei, 2),
            "estimated_time": self._estimate_transaction_time(urgency),
        }

    def _estimate_transaction_time(self, urgency: str) -> str:
        """
        Estimate transaction confirmation time.

        Parameters
        ----------
        urgency : str
            'slow', 'standard', 'fast', or 'instant'

        Returns
        -------
        str
            Estimated time.
        """
        times = {
            "slow": "5-10 minutes",
            "standard": "2-5 minutes",
            "fast": "1-2 minutes",
            "instant": "30 seconds - 1 minute",
        }
        return times.get(urgency, "unknown")


def get_gas_optimizer() -> GasOptimizer:
    """Get the gas optimizer instance."""
    return GasOptimizer()
