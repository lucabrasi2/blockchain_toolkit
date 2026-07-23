"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.gas_service

Purpose
-------
Ethereum gas price optimization service.

This service provides gas price analysis, estimation,
and optimization recommendations.

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

from typing import Dict, Any, Optional

from core.logger import get_logger
from ethereum.gas import get_gas_optimizer

logger = get_logger(__name__)


class GasService:
    """
    Gas price optimization service.
    """

    def __init__(self):
        """Initialize the Gas Service."""
        self.optimizer = get_gas_optimizer()
        logger.info("GasService initialized.")

    def get_gas_report(self) -> Dict[str, Any]:
        """
        Get a complete gas report.

        Returns
        -------
        Dict[str, Any]
            Gas report.
        """
        logger.info("Generating gas report")

        return {
            "current": self.optimizer.get_gas_price(),
            "recommendations": {
                "slow": self.optimizer.get_optimal_gas_price("slow"),
                "standard": self.optimizer.get_optimal_gas_price("standard"),
                "fast": self.optimizer.get_optimal_gas_price("fast"),
                "instant": self.optimizer.get_optimal_gas_price("instant"),
            },
            "estimate_standard": self.optimizer.estimate_gas_cost(),
            "estimate_fast": self.optimizer.estimate_gas_cost(gas_price_gwei=50),
        }

    def get_gas_price(self) -> Dict[str, Any]:
        """Get current gas price."""
        return self.optimizer.get_gas_price()

    def estimate_gas_cost(self, gas_limit: int = 21000, gas_price_gwei: Optional[float] = None) -> Dict[str, Any]:
        """Estimate gas cost."""
        return self.optimizer.estimate_gas_cost(gas_limit, gas_price_gwei)

    def get_optimal_gas_price(self, urgency: str = "standard") -> Dict[str, Any]:
        """Get optimal gas price."""
        return self.optimizer.get_optimal_gas_price(urgency)


###############################################################################
# End of File
###############################################################################
