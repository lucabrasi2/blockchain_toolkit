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

from __future__ import annotations

from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.logger import get_logger

logger = get_logger(__name__)


class BitcoinFeeOptimizer:
    """
    Bitcoin fee optimization service.

    Retrieves current fee estimates from a public Bitcoin fee provider.
    If the provider is unavailable, built-in enterprise defaults are used
    so that the application remains fully operational.
    """

    DEFAULT_FEES = {
        "fast": 20,
        "standard": 10,
        "slow": 5,
        "unit": "sat/byte",
        "source": "default",
        "warning": (
            "Live fee provider unavailable. "
            "Using built-in fee estimates."
        ),
    }

    def __init__(self) -> None:
        self.mempool_url = (
            "https://mempool.space/api/v1/fees/recommended"
        )

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retries disabled.

        Returns
        -------
        requests.Session
        """

        retry = Retry(
            total=0,
            connect=0,
            read=0,
            redirect=0,
            status=0,
        )

        adapter = HTTPAdapter(max_retries=retry)

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def get_fee_estimate(self) -> Dict[str, Any]:
        """
        Retrieve current Bitcoin fee estimates.

        Returns
        -------
        Dict[str, Any]
            Fee estimates in satoshis per byte.
        """

        logger.info(
            "Fetching Bitcoin fee estimates from mempool.space..."
        )

        session = self._create_session()

        try:
            response = session.get(
                self.mempool_url,
                timeout=(3, 5),
            )

            response.raise_for_status()

            data = response.json()

            fees = {
                "fast": data.get("fastestFee", 20),
                "standard": data.get("halfHourFee", 10),
                "slow": data.get("hourFee", 5),
                "unit": "sat/byte",
                "source": "mempool.space",
            }

            logger.info(
                "Bitcoin fee estimates retrieved successfully."
            )

            return fees

        except requests.RequestException as error:

            logger.warning(
                "Unable to reach mempool.space: %s",
                error,
            )

            logger.warning(
                "Using built-in Bitcoin fee estimates."
            )

            return self.DEFAULT_FEES.copy()

        finally:
            session.close()

    def estimate_fee(
        self,
        tx_size: int = 250,
        fee_rate: int = 10,
    ) -> Dict[str, Any]:
        """
        Estimate Bitcoin transaction fee.

        Parameters
        ----------
        tx_size
            Transaction size in bytes.

        fee_rate
            Fee rate in satoshis per byte.

        Returns
        -------
        Dict[str, Any]
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

            logger.exception(
                "Fee estimation failed."
            )

            return {
                "error": str(error)
            }

    def get_optimal_fee(
        self,
        urgency: str = "standard",
    ) -> Dict[str, Any]:
        """
        Return recommended fee for the selected urgency.

        Parameters
        ----------
        urgency
            slow | standard | fast

        Returns
        -------
        Dict[str, Any]
        """

        fee_estimates = self.get_fee_estimate()

        fee_rate = fee_estimates.get(
            urgency,
            fee_estimates["standard"],
        )

        return {
            "urgency": urgency,
            "recommended_fee_rate_sat_byte": fee_rate,
            "estimated_time": self._estimate_time(urgency),
            "source": fee_estimates.get("source"),
            "warning": fee_estimates.get("warning"),
        }

    @staticmethod
    def _estimate_time(
        urgency: str,
    ) -> str:
        """
        Estimate confirmation time.
        """

        return {
            "slow": "10–30 minutes",
            "standard": "5–10 minutes",
            "fast": "1–5 minutes",
        }.get(
            urgency,
            "Unknown",
        )


def get_fee_optimizer() -> BitcoinFeeOptimizer:
    """
    Return Bitcoin fee optimizer instance.
    """

    return BitcoinFeeOptimizer()


###############################################################################
# End of File
###############################################################################