"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.rest_provider

Purpose
-------
Defines the abstract REST provider used by all REST-based
blockchain providers.

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
from typing import Any

import requests

from core.logger import get_logger

from providers.base import BaseProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
)

logger = get_logger(__name__)


class RestProvider(BaseProvider, ABC):
    """
    Base class for REST-based blockchain providers.

    This class implements the common functionality shared by
    providers communicating over HTTP/HTTPS APIs.

    Examples
    --------
    • TRON
    • Blockchain Explorers
    • REST Gateway Services
    • Custom Enterprise APIs
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config,
    ) -> None:
        """
        Initialize the REST provider.

        Parameters
        ----------
        config
            Provider configuration.
        """

        super().__init__(config)

        self._session: requests.Session | None = None

        self._headers: dict[str, str] = {}

        self._base_url: str | None = config.http_url

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def session(
        self,
    ) -> requests.Session:
        """
        Return the active HTTP session.

        Raises
        ------
        ProviderConnectionError
            If the provider is not connected.
        """

        if self._session is None:

            raise ProviderConnectionError(
                "Provider is not connected."
            )

        return self._session

    @property
    def base_url(
        self,
    ) -> str | None:
        """
        Return the configured base URL.
        """

        return self._base_url

    @property
    def headers(
        self,
    ) -> dict[str, str]:
        """
        Return request headers.
        """

        return self._headers.copy()

    ###########################################################################
    # Connection Lifecycle
    ###########################################################################

    def connect(
        self,
    ) -> None:
        """
        Establish a REST session.
        """

        if not self._base_url:

            raise ProviderConnectionError(
                "No endpoint configured."
            )

        logger.info(
            "Connecting REST provider."
        )

        try:

            self._session = requests.Session()

            self._headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

            if self.config.api_key:

                self._headers["Authorization"] = (
                    f"Bearer {self.config.api_key}"
                )

            self._session.headers.update(
                self._headers
            )

            self._connection = self._session

            self._connected = True

            self._record_connection_success()

            logger.info(
                "REST provider connected successfully."
            )

        except PermissionError as exc:

            self._record_connection_failure()

            logger.exception(
                "REST provider authentication failed."
            )

            raise ProviderAuthenticationError(
                str(exc)
            ) from exc

        except Exception as exc:

            self._record_connection_failure()

            logger.exception(
                "REST provider connection failed."
            )

            raise ProviderConnectionError(
                str(exc)
            ) from exc

    def disconnect(
        self,
    ) -> None:
        """
        Close the REST session.
        """

        logger.info(
            "Disconnecting REST provider."
        )

        if self._session is not None:
            self._session.close()

        self._session = None
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
        Determine whether the provider endpoint
        is reachable.

        Returns
        -------
        bool
            True if the endpoint responds
            successfully.
        """

        if (
            self._session is None
            or self._base_url is None
        ):
            return False

        try:

            response = self._session.get(
                self._base_url,
                timeout=self.config.timeout,
            )

            return response.ok

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

        if (
            self._session is None
            or self._base_url is None
        ):
            raise ProviderConnectionError(
                "Provider is not connected."
            )

        logger.debug(
            "Pinging REST provider."
        )

        start = time.perf_counter()

        try:

            response = self._session.get(
                self._base_url,
                timeout=self.config.timeout,
            )

            response.raise_for_status()

        except Exception as exc:

            self._record_request_failure()

            logger.exception(
                "REST provider ping failed."
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
    # Request Helper
    ###########################################################################

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Execute an HTTP request.

        Parameters
        ----------
        method : str
            HTTP method.

        endpoint : str
            Relative API endpoint.

        Returns
        -------
        requests.Response
            HTTP response.

        Raises
        ------
        ProviderConnectionError
            If the provider is unavailable or the
            request fails.
        """

        if self._session is None:

            raise ProviderConnectionError(
                "Provider is not connected."
            )

        url = (
            f"{self._base_url.rstrip('/')}/"
            f"{endpoint.lstrip('/')}"
        )

        kwargs.setdefault(
            "timeout",
            self.config.timeout,
        )

        start = time.perf_counter()

        try:

            response = self._session.request(
                method=method.upper(),
                url=url,
                **kwargs,
            )

            response.raise_for_status()

        except Exception as exc:

            self._record_request_failure()

            logger.exception(
                "REST request failed."
            )

            raise ProviderConnectionError(
                str(exc)
            ) from exc

        latency = time.perf_counter() - start

        self._record_request_success(
            latency,
        )

        return response

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the provider.

        Returns
        -------
        dict[str, Any]
            Provider information.
        """

        data = super().to_dict()

        data.update(
    {
        "provider_type": "rest",
        "http_url": self._base_url,
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