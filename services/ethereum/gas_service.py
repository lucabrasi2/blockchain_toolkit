"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.ethereum.gas_service

Purpose
-------
Ethereum gas price optimization service.

Responsibilities
----------------
• Retrieve current gas prices
• Generate gas optimization reports
• Estimate transaction costs
• Recommend optimal gas prices

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

from __future__ import annotations

from typing import Any

from core.logger import get_logger
from ethereum.gas import get_gas_optimizer

logger = get_logger(__name__)


class GasService:
    """
    Ethereum gas price optimization service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the Gas Service.
        """

        self.optimizer = get_gas_optimizer()

        logger.info(
            "GasService initialized."
        )

    ###########################################################################
    # Gas Report
    ###########################################################################

    def get_gas_report(
        self,
    ) -> dict[str, Any]:
        """
        Generate a complete gas report.

        Returns
        -------
        dict[str, Any]
            Gas analysis report.
        """

        logger.info(
            "Generating gas report."
        )

        try:

            report: dict[str, Any] = {

                "current": (
                    self.optimizer.get_gas_price()
                ),

                "recommendations": {

                    "slow": (
                        self.optimizer
                        .get_optimal_gas_price(
                            "slow",
                        )
                    ),

                    "standard": (
                        self.optimizer
                        .get_optimal_gas_price(
                            "standard",
                        )
                    ),

                    "fast": (
                        self.optimizer
                        .get_optimal_gas_price(
                            "fast",
                        )
                    ),

                    "instant": (
                        self.optimizer
                        .get_optimal_gas_price(
                            "instant",
                        )
                    ),
                },

                "estimate_standard": (
                    self.optimizer
                    .estimate_gas_cost()
                ),

                "estimate_fast": (
                    self.optimizer
                    .estimate_gas_cost(
                        gas_price_gwei=50,
                    )
                ),
            }

            logger.info(
                "Gas report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate gas report."
            )

            raise


###############################################################################
# End of Part 1
###############################################################################
    ###########################################################################
    # Current Gas Price
    ###########################################################################

    def get_gas_price(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the current gas price.

        Returns
        -------
        dict[str, Any]
            Current gas price information.
        """

        logger.info(
            "Retrieving current gas price."
        )

        try:

            result = (
                self.optimizer.get_gas_price()
            )

            logger.info(
                "Current gas price retrieved successfully."
            )

            return result

        except Exception:

            logger.exception(
                "Failed to retrieve current gas price."
            )

            raise

    ###########################################################################
    # Gas Cost Estimation
    ###########################################################################

    def estimate_gas_cost(
        self,
        gas_limit: int = 21_000,
        gas_price_gwei: float | None = None,
    ) -> dict[str, Any]:
        """
        Estimate transaction gas cost.

        Parameters
        ----------
        gas_limit : int
            Transaction gas limit.

        gas_price_gwei : float | None
            Optional gas price override.

        Returns
        -------
        dict[str, Any]
            Gas estimation.
        """

        logger.info(
            "Estimating gas cost."
        )

        try:

            result = (
                self.optimizer.estimate_gas_cost(
                    gas_limit=gas_limit,
                    gas_price_gwei=gas_price_gwei,
                )
            )

            logger.info(
                "Gas cost estimated successfully."
            )

            return result

        except Exception:

            logger.exception(
                "Failed to estimate gas cost."
            )

            raise

    ###########################################################################
    # Optimal Gas Price
    ###########################################################################

    def get_optimal_gas_price(
        self,
        urgency: str = "standard",
    ) -> dict[str, Any]:
        """
        Retrieve the recommended gas price.

        Parameters
        ----------
        urgency : str
            Transaction urgency.

        Returns
        -------
        dict[str, Any]
            Recommended gas price.
        """

        logger.info(
            "Retrieving optimal gas price "
            "for urgency '%s'.",
            urgency,
        )

        try:

            result = (
                self.optimizer.get_optimal_gas_price(
                    urgency,
                )
            )

            logger.info(
                "Optimal gas price retrieved successfully."
            )

            return result

        except Exception:

            logger.exception(
                "Failed to retrieve optimal gas price "
                "for urgency '%s'.",
                urgency,
            )

            raise


###############################################################################
# End of File
###############################################################################