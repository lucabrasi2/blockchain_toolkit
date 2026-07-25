"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
bitcoin.gas

Purpose
-------
Bitcoin fee optimization.

Bitcoin uses transaction fees instead of gas.
This module provides fee estimation and optimization.

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

from core.logger import get_logger

logger = get_logger(__name__)


class BitcoinFeeOptimizer:
    """
    Bitcoin fee optimization.
    """

    def __init__(self):
        self.mempool_url = "https://mempool.space/api/v1"
        self.blockchain_info_url = "https://blockchain.info"

    def get_fee_estimate(self) -> Dict[str, Any]:
        """
        Get current fee estimates.

        Returns
        -------
        Dict[str, Any]
            Fee estimates in satoshis per byte.
        """
        try:
            # Try mempool.space first
            response = requests.get(f"{self.mempool_url}/fees/recommended", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "fast": data.get("fastestFee", 0),
                    "standard": data.get("halfHourFee", 0),
                    "slow": data.get("hourFee", 0),
                    "unit": "sat/byte",
                    "source": "mempool.space"
                }
            
            # Fallback to blockchain.info
            response = requests.get(f"{self.blockchain_info_url}/fee-estimates", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "fast": data.get("30", 0),
                    "standard": data.get("60", 0),
                    "slow": data.get("120", 0),
                    "unit": "sat/byte",
                    "source": "blockchain.info"
                }

            return {"error": "Unable to fetch fee estimates"}

        except Exception as error:
            logger.error(f"Error getting fee estimate: {error}")
            return {"error": str(error)}

    def estimate_fee(
        self,
        tx_size: int = 250,
        fee_rate: int = 10,
    ) -> Dict[str, Any]:
        """
        Estimate transaction fee.

        Parameters
        ----------
        tx_size : int
            Transaction size in bytes.
        fee_rate : int
            Fee rate in satoshis per byte.

        Returns
        -------
        Dict[str, Any]
            Estimated fee in satoshis and BTC.
        """
        try:
            total_satoshis = tx_size * fee_rate
            total_btc = total_satoshis / 100_000_000

            return {
                "tx_size_bytes": tx_size,
                "fee_rate_sat_byte": fee_rate,
                "fee_satoshis": total_satoshis,
                "fee_btc": round(total_btc, 8),
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
        try:
            fee_estimates = self.get_fee_estimate()

            if "error" in fee_estimates:
                return {"error": fee_estimates["error"]}

            urgency_map = {
                "slow": "slow",
                "standard": "standard",
                "fast": "fast",
            }

            key = urgency_map.get(urgency, "standard")
            fee_rate = fee_estimates.get(key, 10)

            return {
                "urgency": urgency,
                "recommended_fee_rate_sat_byte": fee_rate,
                "estimated_time": self._estimate_time(urgency),
            }

        except Exception as error:
            logger.error(f"Error getting optimal fee: {error}")
            return {"error": str(error)}

    def _estimate_time(self, urgency: str) -> str:
        """Estimate transaction confirmation time."""
        times = {
            "slow": "10-30 minutes",
            "standard": "5-10 minutes",
            "fast": "1-5 minutes",
        }
        return times.get(urgency, "unknown")


def get_fee_optimizer() -> BitcoinFeeOptimizer:
    """Get the Bitcoin fee optimizer instance."""
    return BitcoinFeeOptimizer()


###############################################################################
# End of File
###############################################################################