"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.config

Purpose
-------
Enterprise provider configuration models.

Defines standardized configuration objects used by
all blockchain providers.

Architecture
------------
UBP Enterprise Connectivity Framework

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import Optional


###############################################################################
# Provider Configuration
###############################################################################


@dataclass(slots=True)
class ProviderConfig:
    """
    Standard configuration shared by every provider.
    """

    ###########################################################################
    # Identity
    ###########################################################################

    provider: str

    blockchain: str

    network: str

    ###########################################################################
    # Connectivity
    ###########################################################################

    endpoint: Optional[str] = None

    websocket_endpoint: Optional[str] = None

    ###########################################################################
    # Authentication
    ###########################################################################

    api_key: Optional[str] = None

    project_id: Optional[str] = None

    access_token: Optional[str] = None

    secret_key: Optional[str] = None

    ###########################################################################
    # Connection Settings
    ###########################################################################

    timeout: int = 30

    max_retries: int = 3

    verify_ssl: bool = True

    ###########################################################################
    # Custom Headers
    ###########################################################################

    headers: Optional[Dict[str, str]] = None
###############################################################################
# Configuration Helpers
###############################################################################

    def validate(self) -> bool:
        """
        Validate provider configuration.

        Returns
        -------
        bool
            True if configuration appears valid.
        """

        if not self.provider:

            return False

        if not self.blockchain:

            return False

        if not self.network:

            return False

        return True



    @property
    def authenticated(self) -> bool:
        """
        Determine whether authentication
        credentials are configured.
        """

        return any(

            (

                self.api_key,

                self.project_id,

                self.access_token,

                self.secret_key,

            )

        )



    @property
    def uses_websocket(self) -> bool:
        """
        Determine whether WebSocket
        connectivity is configured.
        """

        return bool(

            self.websocket_endpoint

        )



    def to_dict(
        self,
    ) -> Dict[str, object]:
        """
        Serialize the configuration.

        Returns
        -------
        dict
            Configuration dictionary.
        """

        return {

            "provider":
                self.provider,

            "blockchain":
                self.blockchain,

            "network":
                self.network,

            "endpoint":
                self.endpoint,

            "websocket_endpoint":
                self.websocket_endpoint,

            "api_key":
                self.api_key,

            "project_id":
                self.project_id,

            "access_token":
                self.access_token,

            "secret_key":
                self.secret_key,

            "timeout":
                self.timeout,

            "max_retries":
                self.max_retries,

            "verify_ssl":
                self.verify_ssl,

            "headers":
                self.headers,

        }
    ###############################################################################
# Factory Methods
###############################################################################

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, object],
    ) -> "ProviderConfig":
        """
        Create a ProviderConfig from a dictionary.

        Parameters
        ----------
        data : Dict[str, object]
            Configuration dictionary.

        Returns
        -------
        ProviderConfig
        """

        return cls(

            provider=str(
                data.get("provider", "")
            ),

            blockchain=str(
                data.get("blockchain", "")
            ),

            network=str(
                data.get("network", "")
            ),

            endpoint=data.get("endpoint"),

            websocket_endpoint=data.get(
                "websocket_endpoint"
            ),

            api_key=data.get("api_key"),

            project_id=data.get("project_id"),

            access_token=data.get(
                "access_token"
            ),

            secret_key=data.get(
                "secret_key"
            ),

            timeout=int(
                data.get("timeout", 30)
            ),

            max_retries=int(
                data.get("max_retries", 3)
            ),

            verify_ssl=bool(
                data.get("verify_ssl", True)
            ),

            headers=data.get("headers"),

        )



###############################################################################
# Object Protocol
###############################################################################

    def __str__(
        self,
    ) -> str:
        """
        Human-readable configuration.
        """

        return (

            f"{self.provider}"

            f" ({self.blockchain})"

            f" [{self.network}]"

        )



    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"ProviderConfig("

            f"provider='{self.provider}', "

            f"blockchain='{self.blockchain}', "

            f"network='{self.network}')"

        )