"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.web3_provider

Purpose
-------
Defines the abstract Web3 provider used by all EVM-compatible
providers.

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

import time
from abc import ABC
from datetime import datetime

from web3 import HTTPProvider
from web3 import Web3

from core.logger import get_logger

from providers.base import BaseProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
)

logger = get_logger(__name__)


class Web3Provider(BaseProvider, ABC):
    """
    Base class for all Web3-compatible providers.

    This class implements the common functionality shared by
    Ethereum-compatible providers including:

    • Alchemy
    • Infura
    • QuickNode
    • Chainstack
    • Ankr

    Concrete providers are responsible only for constructing
    their endpoint URLs and exposing provider-specific services.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config,
    ) -> None:
        """
        Initialize the Web3 provider.

        Parameters
        ----------
        config
            Provider configuration.
        """

        super().__init__(config)

        self._web3: Web3 | None = None

        self._http_provider: HTTPProvider | None = None

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def web3(
        self,
    ) -> Web3:
        """
        Return the active Web3 instance.

        Raises
        ------
        ProviderConnectionError
            If the provider has not been connected.
        """

        if self._web3 is None:

            raise ProviderConnectionError(
                "Provider is not connected."
            )

        return self._web3

    ###########################################################################
    # Connection Lifecycle
    ###########################################################################

    def connect(
        self,
    ) -> None:
        """
        Establish a connection to the provider.
        """

        if not self.config.http_url:

            raise ProviderConnectionError(
                "No HTTP endpoint configured."
            )

        logger.info(
            "Connecting Web3 provider."
        )

        try:

            self._http_provider = HTTPProvider(
                self.config.http_url,
                request_kwargs={
                    "timeout": self.config.timeout,
                },
            )

            self._web3 = Web3(
                self._http_provider,
            )

            if not self._web3.is_connected():

                raise ProviderConnectionError(
                    "Unable to establish connection."
                )

            self._connection = self._web3

            self._connected = True

            self._record_connection_success()

            logger.info(
                "Web3 provider connected successfully."
            )

        except ProviderConnectionError:

            self._record_connection_failure()

            logger.exception(
                "Web3 provider connection failed."
            )

            raise

        except PermissionError as exc:

            self._record_connection_failure()

            logger.exception(
                "Web3 provider authentication failed."
            )

            raise ProviderAuthenticationError(
                str(exc)
            ) from exc

        except Exception as exc:

            self._record_connection_failure()

            logger.exception(
                "Web3 provider connection failed."
            )

            raise ProviderConnectionError(
                str(exc)
            ) from exc

    def disconnect(
        self,
    ) -> None:
        """
        Disconnect from the provider.
        """

        logger.info(
            "Disconnecting Web3 provider."
        )

        self._web3 = None
        self._http_provider = None

        self._connection = None

        self._connected = False

        self._last_disconnected_at = (
            datetime.utcnow()
        )

    ###########################################################################
    # Health Monitoring
    ###########################################################################

    def health_check(
        self,
    ) -> bool:
        """
        Determine whether the provider is healthy.

        Returns
        -------
        bool
            True if the provider is connected and
            responding.
        """

        if (
            not self._connected
            or self._web3 is None
        ):
            return False

        try:

            self._web3.eth.block_number

            return True

        except Exception:

            return False
        ###########################################################################
    # Diagnostics
    ###########################################################################

    def ping(
        self,
    ) -> float:
        """
        Measure provider latency.

        Returns
        -------
        float
            Round-trip latency in seconds.

        Raises
        ------
        ProviderConnectionError
            If the provider is unavailable.
        """

        if self._web3 is None:

            raise ProviderConnectionError(
                "Provider is not connected."
            )

        logger.debug(
            "Pinging Web3 provider."
        )

        start = time.perf_counter()

        try:

            self._web3.eth.block_number

        except Exception as exc:

            self._record_request_failure()

            logger.exception(
                "Web3 provider ping failed."
            )

            raise ProviderConnectionError(
                str(exc)
            ) from exc

        latency = time.perf_counter() - start

        self._record_request_success(
            latency,
        )

        return latency

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Serialize the provider.

        Returns
        -------
        dict[str, object]
            Provider information.
        """

        data = super().to_dict()

        data.update(
            {
                "provider_type": "web3",
                "http_url": self.config.http_url,
                "ws_url": self.config.ws_url,
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
            f"provider={self.config.provider!r}, "
            f"network={self.config.network!r}, "
            f"connected={self.connected})"
        )


###############################################################################
# End of File
###############################################################################