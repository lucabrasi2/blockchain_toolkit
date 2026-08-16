"""
Universal Blockchain Platform (UBP)

Module
------
providers.tron.provider

Purpose
-------
Native TRON blockchain provider implementation.

The provider communicates with the TRON HTTP/REST API while
conforming to the current UBP ProviderConfig and BaseProvider
architecture.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
"""

from __future__ import annotations

import time
from typing import Any

import requests

from core.logger import get_logger

from providers.base import BaseProvider
from providers.base import ProviderStatus
from providers.config import ProviderConfig
from providers.exceptions import ProviderConfigurationError
from providers.exceptions import ProviderConnectionError

from providers.tron.constants import TRON_MAINNET
from providers.tron.constants import TRON_MAINNET_URL
from providers.tron.constants import TRON_NILE
from providers.tron.constants import TRON_NILE_URL
from providers.tron.constants import TRON_SHASTA
from providers.tron.constants import TRON_SHASTA_URL


logger = get_logger(__name__)


class TronProvider(BaseProvider):
    """
    Native TRON HTTP provider.

    TRON is handled through its native REST API rather than
    through the EVM/Web3 interface.
    """

    _NETWORK_ENDPOINTS: dict[str, str] = {
        TRON_MAINNET: TRON_MAINNET_URL,
        TRON_SHASTA: TRON_SHASTA_URL,
        TRON_NILE: TRON_NILE_URL,
    }

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        """
        Initialize the TRON provider.
        """

        super().__init__()

        if not isinstance(config, ProviderConfig):
            raise TypeError(
                "TronProvider requires a ProviderConfig."
            )

        self._config = config

        self._network = (
            config.network.strip().lower()
        )

        self._api_key = (
            config.api_key or ""
        )

        self._http_url = (
            config.http_url
            or self._NETWORK_ENDPOINTS.get(
                self._network
            )
        )

        self._ws_url = (
            config.ws_url or ""
        )

        self._timeout = config.timeout

        self._session: requests.Session | None = None

        self._validate_configuration()

        logger.info(
            "Initialized TronProvider (network=%s)",
            self._network,
        )

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def name(self) -> str:
        """
        Return the provider name.
        """

        return "tron"

    @property
    def blockchain(self) -> str:
        """
        Return the supported blockchain.
        """

        return "tron"

    @property
    def network(self) -> str:
        """
        Return the configured TRON network.
        """

        return self._network

    @property
    def provider_type(self):
        """
        Return the UBP provider type.
        """

        from providers.base import ProviderType

        return ProviderType.CLOUD

    ###########################################################################
    # Endpoints
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        Return the TRON HTTP endpoint.
        """

        if not self._http_url:
            raise ProviderConfigurationError(
                "TRON HTTP endpoint is not configured."
            )

        return self._http_url

    @property
    def ws_url(self) -> str:
        """
        Return the TRON WebSocket endpoint.

        Native WebSocket support is not enabled unless
        explicitly configured.
        """

        return self._ws_url

    ###########################################################################
    # Capabilities
    ###########################################################################

    @property
    def supports_websocket(self) -> bool:
        """
        Return whether WebSocket support is available.
        """

        return bool(self._ws_url)

    @property
    def supports_archive(self) -> bool:
        """
        Return whether historical blockchain queries
        are supported by the configured endpoint.
        """

        return True

    @property
    def supports_debug_api(self) -> bool:
        """
        Return whether TRON debug APIs are supported.
        """

        return False

    @property
    def supports_trace_api(self) -> bool:
        """
        Return whether TRON trace APIs are supported.
        """

        return False

    ###########################################################################
    # Configuration
    ###########################################################################

    def _validate_configuration(self) -> None:
        """
        Validate the TRON provider configuration.
        """

        if self._network not in self._NETWORK_ENDPOINTS:
            raise ProviderConfigurationError(
                f"Unsupported TRON network: "
                f"{self._network}. "
                f"Available: "
                f"{sorted(self._NETWORK_ENDPOINTS)}"
            )

        if not self._http_url:
            raise ProviderConfigurationError(
                "TRON HTTP endpoint is not configured."
            )

        if self._timeout <= 0:
            raise ProviderConfigurationError(
                "TRON timeout must be greater than zero."
            )

    def get_config(self) -> dict[str, Any]:
        """
        Return normalized TRON provider configuration.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "timeout": self._timeout,
            "capabilities": {
                "websocket": self.supports_websocket,
                "archive": self.supports_archive,
                "trace": self.supports_trace_api,
                "debug": self.supports_debug_api,
            },
            "authentication_configured": bool(
                self._api_key
            ),
        }

    @property
    def masked_api_key(self) -> str:
        """
        Return a masked API-key representation.
        """

        if not self._api_key:
            return ""

        if len(self._api_key) <= 8:
            return "********"

        return (
            self._api_key[:4]
            + "..."
            + self._api_key[-4:]
        )

    ###########################################################################
    # HTTP Session
    ###########################################################################

    def _build_session(
        self,
    ) -> requests.Session:
        """
        Create a TRON HTTP session.
        """

        session = requests.Session()

        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        if self._api_key:
            session.headers.update(
                {
                    "TRON-PRO-API-KEY": self._api_key,
                }
            )

        return session

    ###########################################################################
    # Connection Lifecycle
    ###########################################################################

    def connect(self) -> bool:
        """
        Establish and verify a TRON HTTP session.
        """

        if self._session is not None:
            if self.health_check():
                return True

        logger.info(
            "Connecting to TRON (%s)...",
            self._network,
        )

        start = time.perf_counter()

        session = self._build_session()

        try:
            response = session.get(
                self.http_url,
                timeout=self._timeout,
            )

            response.raise_for_status()

        except Exception as exc:
            self._statistics.failed_connections += 1
            self._status = ProviderStatus.OFFLINE

            logger.exception(
                "TRON connection failed."
            )

            raise ProviderConnectionError(
                f"Unable to connect to TRON: {exc}"
            ) from exc

        latency = (
            time.perf_counter() - start
        ) * 1000

        self._session = session

        self._statistics.successful_connections += 1
        self._statistics.last_latency_ms = latency
        self._statistics.total_latency_ms += latency

        self._status = ProviderStatus.ONLINE

        logger.info(
            "TRON connected (%.2f ms)",
            latency,
        )

        return True

    def disconnect(self) -> None:
        """
        Close the TRON HTTP session.
        """

        if self._session is not None:
            self._session.close()

        self._session = None

        super().disconnect()

    ###########################################################################
    # Health
    ###########################################################################

    def health_check(self) -> bool:
        """
        Check whether the TRON endpoint is reachable.
        """

        if self._session is None:
            return False

        try:
            response = self._session.get(
                self.http_url,
                timeout=self._timeout,
            )

            healthy = response.ok

            if healthy:
                self._status = ProviderStatus.ONLINE
            else:
                self._status = ProviderStatus.OFFLINE

            return healthy

        except Exception as exc:
            logger.warning(
                "TRON health check failed: %s",
                exc,
            )

            self._status = ProviderStatus.OFFLINE

            return False

    def is_available(self) -> bool:
        """
        Return whether the TRON provider is available.
        """

        try:
            if self._session is None:
                self.connect()

            return self.health_check()

        except Exception as exc:
            logger.warning(
                "TRON provider unavailable: %s",
                exc,
            )

            return False

    ###########################################################################
    # Native TRON HTTP Requests
    ###########################################################################

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Execute a native TRON HTTP request.
        """

        if self._session is None:
            self.connect()

        if self._session is None:
            raise ProviderConnectionError(
                "TRON provider is not connected."
            )

        url = (
            f"{self.http_url.rstrip('/')}/"
            f"{endpoint.lstrip('/')}"
        )

        kwargs.setdefault(
            "timeout",
            self._timeout,
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
            self.record_request(
                successful=False
            )

            logger.exception(
                "TRON request failed."
            )

            raise ProviderConnectionError(
                f"TRON request failed: {exc}"
            ) from exc

        latency = (
            time.perf_counter() - start
        ) * 1000

        self.record_request(
            successful=True
        )

        self._statistics.last_latency_ms = latency
        self._statistics.total_latency_ms += latency

        return response

    ###########################################################################
    # Blockchain Operations
    ###########################################################################

    def get_latest_block(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest TRON block.
        """

        return self._request(
            "GET",
            "/wallet/getnowblock",
        ).json()

    def get_block(
        self,
        block_number: int,
    ) -> dict[str, Any]:
        """
        Retrieve a TRON block by height.
        """

        if not isinstance(
            block_number,
            int,
        ):
            raise TypeError(
                "block_number must be an integer."
            )

        if block_number < 0:
            raise ValueError(
                "block_number cannot be negative."
            )

        return self._request(
            "POST",
            "/wallet/getblockbynum",
            json={
                "num": block_number,
            },
        ).json()

    def get_account(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve TRON account information.
        """

        if not isinstance(
            address,
            str,
        ):
            raise TypeError(
                "address must be a string."
            )

        address = address.strip()

        if not address:
            raise ValueError(
                "address cannot be empty."
            )

        return self._request(
            "POST",
            "/wallet/getaccount",
            json={
                "address": address,
                "visible": True,
            },
        ).json()

    ###########################################################################
    # Transaction Operations
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve a TRON transaction by transaction ID.
        """

        if not isinstance(
            transaction_hash,
            str,
        ):
            raise TypeError(
                "transaction_hash must be a string."
            )

        transaction_hash = transaction_hash.strip()

        if not transaction_hash:
            raise ValueError(
                "transaction_hash cannot be empty."
            )

        return self._request(
            "GET",
            "/wallet/gettransactionbyid",
            params={
                "value": transaction_hash,
            },
        ).json()

    def get_transaction_info(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve detailed information about a TRON transaction.
        """

        if not isinstance(
            transaction_hash,
            str,
        ):
            raise TypeError(
                "transaction_hash must be a string."
            )

        transaction_hash = transaction_hash.strip()

        if not transaction_hash:
            raise ValueError(
                "transaction_hash cannot be empty."
            )

        return self._request(
            "GET",
            "/wallet/gettransactioninfobyid",
            params={
                "value": transaction_hash,
            },
        ).json()

    ###########################################################################
    # Diagnostics
    ###########################################################################

    @property
    def latest_block(self) -> int | None:
        """
        Return the latest TRON block number.
        """

        try:
            data = self.get_latest_block()

            header = data.get(
                "block_header",
                {},
            )

            raw_data = header.get(
                "raw_data",
                {},
            )

            raw_number = raw_data.get(
                "number"
            )

            if raw_number is None:
                return None

            return int(raw_number)

        except Exception:
            return None

    def validate(self) -> bool:
        """
        Validate the TRON provider.
        """

        try:
            self._validate_configuration()

            if not self.is_available():
                return False

            if self.latest_block is None:
                return False

            return True

        except Exception as exc:
            logger.exception(
                "TRON provider validation failed: %s",
                exc,
            )

            return False

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(self) -> dict[str, Any]:
        """
        Return a normalized provider representation.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider_type": self.provider_type.value,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
            "status": self.status.value,
            "capabilities": {
                "websocket": self.supports_websocket,
                "archive": self.supports_archive,
                "trace": self.supports_trace_api,
                "debug": self.supports_debug_api,
            },
        }

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __str__(self) -> str:
        return (
            f"TRON [{self._network}]"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"network={self._network!r}, "
            f"status={self.status.value!r})"
        )