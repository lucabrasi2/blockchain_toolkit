"""
providers/rest_provider.py

Universal Blockchain Platform (UBP)

Defines the abstract RestProvider used by all REST-based
blockchain providers.
"""

from __future__ import annotations

import time
from datetime import datetime
from abc import ABC
from typing import Any
from typing import Dict
from typing import Optional

import requests

from providers.base import BaseProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
)


class RestProvider(BaseProvider, ABC):
    """
    Base class for REST-based blockchain providers.

    This class implements the common functionality shared by
    providers that communicate over HTTP/HTTPS APIs.

    Examples:

        • TRON
        • Blockchain Explorers
        • REST Gateway Services
        • Custom Enterprise APIs
    """

    def __init__(self, config):
        super().__init__(config)

        self._session: Optional[requests.Session] = None

        self._headers: Dict[str, str] = {}

        self._base_url: Optional[str] = config.endpoint
        # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def session(self) -> requests.Session:
        """
        Return the active HTTP session.

        Raises
        ------
        ProviderConnectionError
            If the provider has not been connected.
        """

        if self._session is None:
            raise ProviderConnectionError(
                "Provider is not connected."
            )

        return self._session

    @property
    def base_url(self) -> Optional[str]:
        """
        Return the configured base URL.
        """

        return self._base_url

    @property
    def headers(self) -> Dict[str, str]:
        """
        Return the current request headers.
        """

        return self._headers.copy()

    # ---------------------------------------------------------
    # Connection Lifecycle
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Establish a REST session.
        """

        if not self._base_url:
            raise ProviderConnectionError(
                "No endpoint configured."
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

            self._session.headers.update(self._headers)

            self._connection = self._session
            self._connected = True

            self._record_connection_success()

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
        Close the REST session.
        """

        if self._session is not None:
            self._session.close()

        self._session = None
        self._connection = None
        self._connected = False

        self._last_disconnected_at = datetime.utcnow()
        # ---------------------------------------------------------
    # Health Monitoring
    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Check whether the provider endpoint is reachable.

        Returns
        -------
        bool
            True if the endpoint responds successfully.
        """

        if self._session is None or not self._base_url:
            return False

        try:
            response = self._session.get(
                self._base_url,
                timeout=self.config.timeout,
            )

            return response.ok

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

        if self._session is None or not self._base_url:
            raise ProviderConnectionError(
                "Provider is not connected."
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

            raise ProviderConnectionError(
                str(exc)
            ) from exc

        latency = time.perf_counter() - start

        self._record_request_success(latency)

        return latency

    # ---------------------------------------------------------
    # Request Helper
    # ---------------------------------------------------------

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
        method:
            HTTP method.

        endpoint:
            Relative API endpoint.

        Returns
        -------
        requests.Response
        """

        if self._session is None:
            raise ProviderConnectionError(
                "Provider is not connected."
            )

        url = f"{self._base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        kwargs.setdefault(
            "timeout",
            self.config.timeout,
        )

        response = self._session.request(
            method=method.upper(),
            url=url,
            **kwargs,
        )

        response.raise_for_status()

        return response

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Return provider information.
        """

        data = super().to_dict()

        data.update(
            {
                "provider_type": "rest",
                "base_url": self._base_url,
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