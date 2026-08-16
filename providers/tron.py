"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.tron

Purpose
-------
Enterprise TRON REST provider implementation.

Uses the TronGrid REST API.

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

from providers.config import ProviderConfig
from providers.rest_provider import RestProvider

logger = get_logger(__name__)


###############################################################################
# Default Endpoints
###############################################################################

NETWORK_ENDPOINTS = {
    "mainnet": "https://api.trongrid.io",
    "shasta": "https://api.shasta.trongrid.io",
    "nile": "https://nile.trongrid.io",
}


class TronProvider(RestProvider):
    """
    Enterprise TRON REST provider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        """
        Initialize the TRON provider.

        Parameters
        ----------
        config : ProviderConfig
            Provider configuration.
        """

        network = config.network.lower()

        if not config.http_url:
            config.http_url = NETWORK_ENDPOINTS.get(
                network,
                NETWORK_ENDPOINTS["mainnet"],
            )

        super().__init__(config)

        #
        # Configure optional TronGrid API key.
        #
        if config.api_key:

            #
            # NOTE:
            # RestProvider.headers returns a COPY.
            # Therefore we update the underlying headers.
            #
            self._headers["TRON-PRO-API-KEY"] = (
                config.api_key
            )

            if self._session is not None:
                self._session.headers.update(
                    self._headers
                )

        logger.info(
            "TRON provider initialized."
        )

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def provider_name(
        self,
    ) -> str:
        """
        Return the provider name.
        """

        return "tron"

    @property
    def blockchain(
        self,
    ) -> str:
        """
        Return the supported blockchain.
        """

        return "tron"

    @property
    def network(
        self,
    ) -> str:
        """
        Return the configured network.
        """

        return self.config.network

    ###########################################################################
    # Blockchain Operations
    ###########################################################################

    def get_latest_block(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest TRON block.

        Returns
        -------
        dict[str, Any]
            Latest block information.
        """

        return (
            self._request(
                "GET",
                "/wallet/getnowblock",
            ).json()
        )

    def get_block(
        self,
        block_number: int,
    ) -> dict[str, Any]:
        """
        Retrieve a block by height.

        Parameters
        ----------
        block_number : int
            Block height.

        Returns
        -------
        dict[str, Any]
            Block information.
        """

        return (
            self._request(
                "POST",
                "/wallet/getblockbynum",
                json={
                    "num": block_number,
                },
            ).json()
        )
        def get_account(
        self,
        address: str,
    ) -> dict[str, Any]:
         """
        Retrieve account information.

        Parameters
        ----------
        address : str
            TRON account address.

        Returns
        -------
        dict[str, Any]
            Account information.
        """

        return (
            self._request(
                "POST",
                "/wallet/getaccount",
                json={
                    "address": address,
                    "visible": True,
                },
            ).json()
        )

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize provider information.

        Returns
        -------
        dict[str, Any]
            Provider information.
        """

        data = super().to_dict()

        data.update(
            {
                "provider": self.provider_name,
                "blockchain": self.blockchain,
                "network": self.network,
                "endpoint": self.base_url,
            }
        )

        return data

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"network={self.network!r}, "
            f"endpoint={self.base_url!r}, "
            f"connected={self.connected})"
        )


###############################################################################
# End of File
###############################################################################