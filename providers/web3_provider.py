"""
providers/web3_provider.py

Universal Blockchain Platform (UBP)

Defines the abstract Web3Provider used by all EVM-compatible
providers.
"""

from __future__ import annotations

import time
from datetime import datetime
from abc import ABC
from datetime import datetime
from typing import Optional

from web3 import HTTPProvider
from web3 import Web3

from providers.base import BaseProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
)


class Web3Provider(BaseProvider, ABC):
    """
    Base class for all Web3-compatible providers.

    This class implements the common functionality shared by
    Ethereum-compatible providers such as:

        • Alchemy
        • Infura
        • QuickNode
        • Chainstack
        • Ankr

    Concrete providers are responsible only for constructing
    their endpoint URLs and supplying provider-specific services.
    """

    def __init__(self, config):
        super().__init__(config)

        self._web3: Optional[Web3] = None

        self._http_provider: Optional[HTTPProvider] = None
        # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def web3(self) -> Web3:
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

    # ---------------------------------------------------------
    # Connection Lifecycle
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Establish a connection to the provider.
        """

        if not self.config.endpoint:
            raise ProviderConnectionError(
                "No endpoint configured."
            )

        try:
            self._http_provider = HTTPProvider(
                self.config.endpoint,
                request_kwargs={
                    "timeout": self.config.timeout,
                },
            )

            self._web3 = Web3(self._http_provider)

            if not self._web3.is_connected():
                raise ProviderConnectionError(
                    "Unable to establish connection."
                )

            self._connection = self._web3
            self._connected = True

            self._record_connection_success()

        except ProviderConnectionError:
            self._record_connection_failure()
            raise

        except PermissionError as exc:
            self._record_connection_failure()
            raise ProviderAuthenticationError(
                str(exc)
            ) from exc

        except Exception as exc:
            self._record_connection_failure()
            raise ProviderConnectionError(
                str(exc)
            ) from exc

    def disconnect(self) -> None:
        """
        Disconnect from the provider.
        """

        self._web3 = None
        self._http_provider = None
        self._connection = None
        self._connected = False

        self._last_disconnected_at = datetime.utcnow()
        # ---------------------------------------------------------
    # Health Monitoring
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Check whether the provider is healthy.

        Returns
        -------
        bool
            True if the provider is connected and responding.
        """

        if not self._connected or self._web3 is None:
            return False

        try:
            self._web3.eth.block_number
            return True

        except Exception:
            return False

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    def ping(self) -> float:
        """
        Measure provider latency.

        Returns
        -------
        float
            Latency in seconds.
        """

        if self._web3 is None:
            raise ProviderConnectionError(
                "Provider is not connected."
            )

        start = time.perf_counter()

        try:
            self._web3.eth.block_number

        except Exception as exc:
            self._record_request_failure()
            raise ProviderConnectionError(
                str(exc)
            ) from exc

        latency = time.perf_counter() - start

        self._record_request_success(latency)

        return latency

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Return provider information.
        """

        data = super().to_dict()

        data.update(
            {
                "provider_type": "web3",
                "endpoint": self.config.endpoint,
                "websocket_endpoint": self.config.websocket_endpoint,
            }
        )

        return data

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"provider={self.config.provider!r}, "
            f"network={self.config.network!r}, "
            f"connected={self.connected})"
        )
    