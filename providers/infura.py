"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.infura

Purpose
-------
Enterprise Infura blockchain provider implementation.

This module provides connectivity to Ethereum-compatible networks
through Infura infrastructure.

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

from typing import Any

from core.logger import get_logger

from providers.base import ProviderType
from providers.web3_provider import Web3Provider

from providers.config import ProviderConfig

logger = get_logger(__name__)


###############################################################################
# Infura Provider
###############################################################################


class InfuraProvider(Web3Provider):
    """
    Enterprise Infura provider.

    This provider supplies Ethereum-compatible blockchain
    connectivity through Infura infrastructure.

    Connection lifecycle, statistics, health monitoring,
    retries and diagnostics are inherited from BaseProvider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        """
        Initialize the Infura provider.

        Parameters
        ----------
        config : ProviderConfig
            Validated provider configuration.
        """

        super().__init__()

        self._config = config

        logger.info(
            "Initialized InfuraProvider "
            "(network=%s)",
            self._config.network,
        )

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        """
        Provider name.
        """
        return "Infura"

    @property
    def blockchain(self) -> str:
        """
        Blockchain supported by the configured network.
        """

        network = self._config.network.lower()

        if "polygon" in network:
            return "Polygon"

        if "arbitrum" in network or "arb" in network:
            return "Arbitrum"

        if "optimism" in network:
            return "Optimism"

        if "base" in network:
            return "Base"

        return "Ethereum"

    @property
    def network(self) -> str:
        """
        Network name.
        """
        return self._config.network

    @property
    def provider_type(self) -> ProviderType:
        """
        Infrastructure classification.
        """
        return ProviderType.CLOUD

    ###########################################################################
    # Endpoint Configuration
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        Infura HTTP endpoint.
        """

        if self._config.endpoint:
            return self._config.endpoint

        return (
            f"https://{self._config.network}"
            f".infura.io/v3/"
            f"{self._config.api_key}"
        )

    @property
    def ws_url(self) -> str:
        """
        Infura WebSocket endpoint.
        """

        return (
            f"wss://{self._config.network}"
            f".infura.io/ws/v3/"
            f"{self._config.api_key}"
        )
        ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(self) -> dict[str, Any]:
        """
        Return provider configuration.

        Sensitive values such as API keys are never exposed.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider_type": self.provider_type.value,
            "http_enabled": True,
            "websocket_enabled": bool(self.ws_url),
            "api_key_configured": bool(self._config.api_key),
            "endpoint_override": bool(self._config.endpoint),
        }

    ###########################################################################
    # Provider Information
    ###########################################################################

    def get_provider_info(self) -> dict[str, Any]:
        """
        Return normalized provider information.
        """

        information = super().get_provider_info()

        information.update(
            {
                "service": "Infura",
                "api_key_configured": bool(self._config.api_key),
                "endpoint_override": bool(self._config.endpoint),
            }
        )

        return information

    ###########################################################################
    # Endpoint Validation
    ###########################################################################

    def validate_endpoint(self) -> bool:
        """
        Validate the configured Infura endpoint.
        """

        logger.debug(
            "Validating Infura endpoint for %s.",
            self.network,
        )

        return self.health_check()

    ###########################################################################
    # Blockchain Queries
    ###########################################################################

    def get_block_number(self) -> int:
        """
        Return the latest block number.

        Returns
        -------
        int
            Latest blockchain height.
        """

        self.before_request()

        try:
            block_number = self.web3.eth.block_number

            self.after_request(successful=True)

            return block_number

        except Exception:
            self.after_request(successful=False)

            logger.exception(
                "Failed to retrieve latest block number."
            )

            raise

    ###########################################################################
    # Account Operations
    ###########################################################################

    def get_balance(
        self,
        address: str,
    ) -> int:
        """
        Retrieve an account balance.

        Parameters
        ----------
        address : str
            Ethereum-compatible wallet address.

        Returns
        -------
        int
            Balance in Wei.
        """

        self.before_request()

        try:
            balance = self.web3.eth.get_balance(address)

            self.after_request(successful=True)

            return balance

        except Exception:
            self.after_request(successful=False)

            logger.exception(
                "Failed to retrieve balance for %s.",
                address,
            )

            raise

    def get_balance_eth(
        self,
        address: str,
    ) -> float:
        """
        Retrieve an account balance in Ether.

        Parameters
        ----------
        address : str
            Ethereum-compatible wallet address.

        Returns
        -------
        float
            Balance in Ether.
        """

        balance = self.get_balance(address)

        return float(
            self.web3.from_wei(
                balance,
                "ether",
            )
        )
        ###########################################################################
    # Block Operations
    ###########################################################################

    def get_block(
        self,
        block_identifier: Any = "latest",
    ) -> dict[str, Any]:
        """
        Retrieve block information.

        Parameters
        ----------
        block_identifier : Any
            Block number, block hash or "latest".

        Returns
        -------
        dict[str, Any]
            Block information.
        """

        self.before_request()

        try:
            block = self.web3.eth.get_block(
                block_identifier
            )

            self.after_request(
                successful=True
            )

            return dict(block)

        except Exception:

            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve block: %s",
                block_identifier,
            )

            raise

    ###########################################################################
    # Transaction Operations
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction information.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction details.
        """

        self.before_request()

        try:
            transaction = self.web3.eth.get_transaction(
                transaction_hash
            )

            self.after_request(
                successful=True
            )

            return dict(transaction)

        except Exception:

            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve transaction: %s",
                transaction_hash,
            )

            raise

    def get_transaction_receipt(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction receipt.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction receipt.
        """

        self.before_request()

        try:
            receipt = self.web3.eth.get_transaction_receipt(
                transaction_hash
            )

            self.after_request(
                successful=True
            )

            return dict(receipt)

        except Exception:

            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve receipt: %s",
                transaction_hash,
            )

            raise

    ###########################################################################
    # Infura Features
    ###########################################################################

    def get_network_version(self) -> str:
        """
        Return the connected network version.

        Returns
        -------
        str
            Ethereum network version.
        """

        self.before_request()

        try:
            version = str(
                self.web3.net.version
            )

            self.after_request(
                successful=True
            )

            return version

        except Exception:

            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve network version."
            )

            raise

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """
        Release provider resources.
        """

        logger.info(
            "Closing Infura provider."
        )

        super().close()


###############################################################################
# End of File
###############################################################################