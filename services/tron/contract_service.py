"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.tron.contract_service

Purpose
-------
Business logic for TRON contract operations.

Responsibilities
----------------
• Validate TRON addresses
• Detect smart contracts
• Detect TRC-20 token contracts
• Retrieve contract metadata
• Generate controller-friendly contract reports

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

from tron.contracts import (
    get_trc20_metadata,
    is_contract,
    is_trc20,
)

from tron.wallets import (
    get_trx_balance,
    is_valid_address,
)


###############################################################################
# Logger
###############################################################################

logger = get_logger(__name__)


###############################################################################
# TRON Contract Service
###############################################################################


class TronContractService:
    """
    TRON contract business logic service.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
    ) -> None:
        """
        Initialize the TRON Contract Service.
        """

        logger.info(
            "TronContractService initialized."
        )

    ###########################################################################
    # Contract Report
    ###########################################################################

    def get_contract_report(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Generate a complete TRON contract report.

        Parameters
        ----------
        address : str
            TRON contract address.

        Returns
        -------
        dict[str, Any]
            Contract report.
        """

        logger.info(
            "Generating TRON contract report for: %s",
            address,
        )

        try:

            ###################################################################
            # Validate Address
            ###################################################################

            if not is_valid_address(
                address,
            ):

                logger.warning(
                    "Invalid TRON address: %s",
                    address,
                )

                return {
                    "address": address,
                    "error": "Invalid TRON address",
                    "is_valid": False,
                }

            ###################################################################
            # Detect Contract Type
            ###################################################################

            contract = is_contract(
                address,
            )

            trc20 = (
                is_trc20(
                    address,
                )
                if contract
                else False
            )

            ###################################################################
            # Retrieve TRX Balance
            ###################################################################

            balance_trx = 0.0
            balance_sun = 0

            try:

                balance = get_trx_balance(
                    address,
                )

                if isinstance(
                    balance,
                    dict,
                ):

                    balance_trx = balance.get(
                        "trx",
                        0.0,
                    )

                    balance_sun = balance.get(
                        "sun",
                        0,
                    )

            except Exception:

                logger.exception(
                    "Unable to retrieve TRON balance."
                )

            ###################################################################
            # Build Base Report
            ###################################################################

            report: dict[str, Any] = {
                "address": address,

                "is_contract": contract,

                "classification": (
                    "TRC-20 Token"
                    if trc20
                    else (
                        "Contract"
                        if contract
                        else "EOA"
                    )
                ),

                "contract_type": (
                    "TRC-20"
                    if trc20
                    else (
                        "Smart Contract"
                        if contract
                        else "N/A"
                    )
                ),

                "bytecode_size": 0,

                "balance_trx": balance_trx,

                "balance_sun": balance_sun,

                "energy": 0,

                "bandwidth": 0,
            }

            ###################################################################
            # TRC-20 Metadata
            ###################################################################

            if trc20:

                try:

                    metadata = get_trc20_metadata(
                        address,
                    )

                    report.update(
                        {
                            "name": metadata.get(
                                "name",
                                "Unknown",
                            ),

                            "symbol": metadata.get(
                                "symbol",
                                "Unknown",
                            ),

                            "decimals": metadata.get(
                                "decimals",
                                6,
                            ),

                            "total_supply": metadata.get(
                                "total_supply",
                                0,
                            ),

                            "owner": metadata.get(
                                "owner",
                            ),

                            "standard": "TRC-20",

                            "metadata": metadata,
                        }
                    )

                except Exception:

                    logger.exception(
                        "Unable to retrieve TRC-20 metadata."
                    )

            ###################################################################
            # Return Report
            ###################################################################

            logger.info(
                "TRON contract report generated successfully."
            )

            return report

        except Exception:

            logger.exception(
                "Failed to generate TRON contract report."
            )

            raise
        