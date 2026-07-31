"""
Universal Blockchain Platform (UBP)

Module:
    Shared HTTP Client

Purpose:
    Provides a reusable HTTP client for all blockchain providers.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.logger import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """
    Shared HTTP client with connection pooling,
    retries, and default timeout.
    """

    def __init__(
        self,
        timeout=(5, 10),
        retries=2,
    ):
        self.timeout = timeout

        self.session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=0.5,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=frozenset([
                "GET",
                "POST",
            ]),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        logger.info("Shared HTTP client initialized.")

    def get(self, url: str, **kwargs):
        """
        Execute HTTP GET request.
        """
        kwargs.setdefault("timeout", self.timeout)

        logger.debug(f"GET {url}")

        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs):
        """
        Execute HTTP POST request.
        """
        kwargs.setdefault("timeout", self.timeout)

        logger.debug(f"POST {url}")

        return self.session.post(url, **kwargs)

    def close(self):
        """
        Close the shared session.
        """
        self.session.close()


# Singleton instance used across the application.
http_client = HTTPClient()