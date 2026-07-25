"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tron.gas

Purpose
-------
TRON energy and fee optimization.

TRON uses energy and bandwidth instead of gas.
This module provides energy price information and cost estimation.

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
import requests

from tron.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)


class TronEnergyOptimizer:
    """
    TRON energy and fee optimization.
    """

    def __init__(self):
        self.client = get_connection()
        self.api_url = "https://api.trongrid.io"

    def get_energy_price(self) -> Dict[str, Any]:
        """
        Get current energy price information.

        Returns
        -------
        Dict[str, Any]
            Energy price in various units.
        """
        try:
            # Get chain parameters
            url = f"{self.api_url}/wallet/getchainparameters"
            response = requests.post(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                chain_params = data.get("chainParameter", [])

                # Find energy price parameter
                energy_price = 1  # Default
                for param in chain_params:
                    if param.get("key") == "getEnergyFee":
                        energy_price = param.get("value", 1)
                        break

                return {
                    "energy_price": energy_price,
                    "unit": "SUN",
                    "description": "Price per energy unit in SUN",
                }

            return {"error": "Unable to fetch energy price"}

        except Exception as error:
            logger.error(f"Error getting energy price: {error}")
            return {"error": str(error)}

    def estimate_fee(
        self,
        energy_used: int = 10000,
        bandwidth_used: int = 0,
    ) -> Dict[str, Any]:
        """
        Estimate transaction fee.

        Parameters
        ----------
        energy_used : int
            Estimated energy consumption.
        bandwidth_used : int
            Estimated bandwidth consumption.

        Returns
        -------
        Dict[str, Any]
            Estimated fee in TRX and SUN.
        """
        try:
            # Get energy price
            energy_info = self.get_energy_price()
            energy_price = energy_info.get("energy_price", 1)

            # Calculate cost
            energy_cost = energy_used * energy_price
            bandwidth_cost = bandwidth_used * 1  # Bandwidth is free for first few transactions

            total_sun = energy_cost + bandwidth_cost
            total_trx = total_sun / 1_000_000

            return {
                "energy_used": energy_used,
                "bandwidth_used": bandwidth_used,
                "energy_cost_sun": energy_cost,
                "bandwidth_cost_sun": bandwidth_cost,
                "total_cost_sun": total_sun,
                "total_cost_trx": round(total_trx, 6),
            }

        except Exception as error:
            logger.error(f"Error estimating fee: {error}")
            return {"error": str(error)}

    def get_optimal_fee(self, urgency: str = "standard") -> Dict[str, Any]:
        """
        Get optimal fee recommendations.

        Parameters
        ----------
        urgency : str
            'slow', 'standard', 'fast'

        Returns
        -------
        Dict[str, Any]
            Fee recommendations.
        """
        multipliers = {
            "slow": 0.8,
            "standard": 1.0,
            "fast": 1.3,
        }

        multiplier = multipliers.get(urgency, 1.0)

        energy_info = self.get_energy_price()
        base_price = energy_info.get("energy_price", 1)

        return {
            "urgency": urgency,
            "base_energy_price": base_price,
            "recommended_multiplier": multiplier,
            "recommended_price": round(base_price * multiplier, 2),
            "estimated_time": self._estimate_time(urgency),
        }

    def _estimate_time(self, urgency: str) -> str:
        """Estimate transaction confirmation time."""
        times = {
            "slow": "5-10 minutes",
            "standard": "2-5 minutes",
            "fast": "1-2 minutes",
        }
        return times.get(urgency, "unknown")


def get_energy_optimizer() -> TronEnergyOptimizer:
    """Get the TRON energy optimizer instance."""
    return TronEnergyOptimizer()


###############################################################################
# End of File
###############################################################################
