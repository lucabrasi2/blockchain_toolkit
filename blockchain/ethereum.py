"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
blockchain.ethereum

Purpose
-------
Enterprise Ethereum blockchain service.

This module provides a high-level interface for interacting with
Ethereum-compatible blockchains while remaining independent of the
underlying infrastructure provider.

Architecture
------------
Application
      │
      ▼
EthereumService
      │
      ▼
ProviderManager
      │
      ▼
BaseProvider
      │
      ▼
Alchemy / Infura / QuickNode / Local Node

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

from web3 import Web3

from core.logger import get_logger

from providers.base import BaseProvider
from providers.manager import ProviderManager

logger = get_logger(__name__)


###############################################################################
# Ethereum Service
###############################################################################


class EthereumService:
    """
    Enterprise Ethereum blockchain service.

    This service encapsulates Ethereum business operations and delegates
    connectivity to the ProviderManager. It is therefore independent of the
    underlying provider implementation (Alchemy, Infura, etc.).
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        provider: BaseProvider | None = None,
    ) -> None:
        """
        Initialize the Ethereum service.

        Parameters
        ----------
        provider : BaseProvider, optional
            Explicit provider instance. If omitted, the ProviderManager
            supplies the default provider.
        """

        self._manager = ProviderManager()

        if provider is None:
            self._provider = self._manager.get_provider()
        else:
            self._provider = provider

        logger.info(
            "EthereumService initialized using provider '%s'.",
            self._provider.name,
        )

    ###########################################################################
    # Provider Access
    ###########################################################################

    @property
    def provider(self) -> BaseProvider:
        """
        Return the active blockchain provider.
        """

        return self._provider

    @property
    def web3(self) -> Web3:
        """
        Return the active Web3 instance.
        """

        return self.provider.web3

    ###########################################################################
    # Connection Information
    ###########################################################################

    @property
    def chain_id(self) -> int:
        """
        Connected chain identifier.
        """

        return self.web3.eth.chain_id

    @property
    def latest_block(self) -> int:
        """
        Latest block number.
        """

        return self.web3.eth.block_number

    @property
    def client_version(self) -> str:
        """
        Ethereum client version.
        """

        return self.web3.client_version

    @property
    def is_connected(self) -> bool:
        """
        Determine whether the provider is connected.
        """

        return self.web3.is_connected()

    ###########################################################################
    # Connection Management
    ###########################################################################

    def connect(self) -> Web3:
        """
        Connect to the configured provider.

        Returns
        -------
        Web3
            Active Web3 connection.
        """

        return self.provider.connect()

    def disconnect(self) -> None:
        """
        Disconnect from the provider.
        """

        self.provider.disconnect()

    def reconnect(self) -> Web3:
        """
        Reconnect to the provider.

        Returns
        -------
        Web3
            Active Web3 connection.
        """

        return self.provider.reconnect()

    ###########################################################################
    # Diagnostics
    ###########################################################################

    def health_check(self) -> bool:
        """
        Perform a provider health check.
        """

        return self.provider.health_check()

    def provider_info(self) -> dict[str, Any]:
        """
        Return provider information.
        """

        return self.provider.get_provider_info()
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
            Ethereum wallet address.

        Returns
        -------
        int
            Balance in Wei.
        """

        self.provider.before_request()

        try:

            balance = self.web3.eth.get_balance(
                address
            )

            self.provider.after_request(
                successful=True,
            )

            return balance

        except Exception:

            self.provider.after_request(
                successful=False,
            )

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
            Ethereum wallet address.

        Returns
        -------
        float
            Balance in Ether.
        """

        balance = self.get_balance(
            address,
        )

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
            Block number, block hash, or "latest".

        Returns
        -------
        dict[str, Any]
            Block data.
        """

        self.provider.before_request()

        try:

            block = self.web3.eth.get_block(
                block_identifier,
            )

            self.provider.after_request(
                successful=True,
            )

            return dict(block)

        except Exception:

            self.provider.after_request(
                successful=False,
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
            Transaction information.
        """

        self.provider.before_request()

        try:

            transaction = (
                self.web3.eth.get_transaction(
                    transaction_hash,
                )
            )

            self.provider.after_request(
                successful=True,
            )

            return dict(
                transaction,
            )

        except Exception:

            self.provider.after_request(
                successful=False,
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
        Retrieve a transaction receipt.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction receipt.
        """

        self.provider.before_request()

        try:

            receipt = (
                self.web3.eth.get_transaction_receipt(
                    transaction_hash,
                )
            )

            self.provider.after_request(
                successful=True,
            )

            return dict(
                receipt,
            )

        except Exception:

            self.provider.after_request(
                successful=False,
            )

            logger.exception(
                "Failed to retrieve transaction receipt: %s",
                transaction_hash,
            )

            raise
            ###########################################################################
    # Transaction Utilities
    ###########################################################################

    def get_nonce(
        self,
        address: str,
        block_identifier: str = "pending",
    ) -> int:
        """
        Retrieve the transaction nonce for an account.

        Parameters
        ----------
        address : str
            Ethereum wallet address.

        block_identifier : str, default="pending"
            Block identifier.

        Returns
        -------
        int
            Account nonce.
        """

        self.provider.before_request()

        try:

            nonce = self.web3.eth.get_transaction_count(
                address,
                block_identifier,
            )

            self.provider.after_request(
                successful=True,
            )

            return nonce

        except Exception:

            self.provider.after_request(
                successful=False,
            )

            logger.exception(
                "Failed to retrieve nonce for %s.",
                address,
            )

            raise

    def estimate_gas(
        self,
        transaction: dict[str, Any],
    ) -> int:
        """
        Estimate gas required for a transaction.

        Parameters
        ----------
        transaction : dict[str, Any]
            Transaction dictionary.

        Returns
        -------
        int
            Estimated gas.
        """

        self.provider.before_request()

        try:

            gas = self.web3.eth.estimate_gas(
                transaction,
            )

            self.provider.after_request(
                successful=True,
            )

            return gas

        except Exception:

            self.provider.after_request(
                successful=False,
            )

            logger.exception(
                "Gas estimation failed."
            )

            raise

    ###########################################################################
    # Transaction Broadcasting
    ###########################################################################

    def send_raw_transaction(
        self,
        signed_transaction: bytes,
    ) -> str:
        """
        Broadcast a signed transaction.

        Parameters
        ----------
        signed_transaction : bytes
            Signed raw transaction.

        Returns
        -------
        str
            Transaction hash.
        """

        self.provider.before_request()

        try:

            tx_hash = self.web3.eth.send_raw_transaction(
                signed_transaction,
            )

            self.provider.after_request(
                successful=True,
            )

            return tx_hash.hex()

        except Exception:

            self.provider.after_request(
                successful=False,
            )

            logger.exception(
                "Transaction broadcast failed."
            )

            raise

    def wait_for_transaction_receipt(
        self,
        transaction_hash: str,
        timeout: int = 120,
        poll_latency: float = 0.5,
    ) -> dict[str, Any]:
        """
        Wait for transaction confirmation.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        timeout : int
            Maximum wait time.

        poll_latency : float
            Poll interval.

        Returns
        -------
        dict[str, Any]
            Transaction receipt.
        """

        self.provider.before_request()

        try:

            receipt = self.web3.eth.wait_for_transaction_receipt(
                transaction_hash,
                timeout=timeout,
                poll_latency=poll_latency,
            )

            self.provider.after_request(
                successful=True,
            )

            return dict(receipt)

        except Exception:

            self.provider.after_request(
                successful=False,
            )

            logger.exception(
                "Waiting for receipt failed."
            )

            raise

    ###########################################################################
    # Service Information
    ###########################################################################

    def info(self) -> dict[str, Any]:
        """
        Return service information.
        """

        return {
            "service": "EthereumService",
            "provider": self.provider.name,
            "network": self.provider.network,
            "blockchain": self.provider.blockchain,
            "chain_id": self.chain_id,
            "latest_block": self.latest_block,
            "client_version": self.client_version,
            "connected": self.is_connected,
        }

    ###########################################################################
    # Object Protocol
    ###########################################################################

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"provider='{self.provider.name}', "
            f"network='{self.provider.network}')"
        )


###############################################################################
# End of File
###############################################################################