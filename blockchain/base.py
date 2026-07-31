"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
blockchain.base

Purpose
-------
Defines the abstract base class for all blockchain implementations.

Every blockchain supported by the Universal Blockchain Platform must
inherit from BlockchainBase.

The Blockchain layer is intentionally provider-agnostic. Connectivity
is delegated to the ProviderManager, allowing automatic failover,
provider switching and future extensibility without changing blockchain
logic.

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Dict
from typing import Optional

from blockchain.config import BlockchainConfig

from providers.base import BaseProvider
from providers.manager import ProviderManager


class BlockchainBase(ABC):
    """
    Base class for every blockchain implementation.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: BlockchainConfig,
        provider_manager: ProviderManager,
    ) -> None:

        self._config = config

        self._provider_manager = provider_manager

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def config(self) -> BlockchainConfig:
        """
        Return blockchain configuration.
        """

        return self._config

    @property
    def provider_manager(self) -> ProviderManager:
        """
        Return the ProviderManager.
        """

        return self._provider_manager

    @property
    def provider(self) -> BaseProvider:
        """
        Return the currently active provider.
        """

        return self._provider_manager.get_active_provider()

    @property
    def blockchain(self) -> str:
        """
        Blockchain name.
        """

        return self._config.blockchain

    @property
    def network(self) -> str:
        """
        Active blockchain network.
        """

        return self._config.network

    ###########################################################################
    # Lifecycle
    ###########################################################################

    def connect(self) -> None:
        """
        Connect the active provider.
        """

        self.provider.connect()

    def disconnect(self) -> None:
        """
        Disconnect the active provider.
        """

        self.provider.disconnect()

    def reconnect(self) -> None:
        """
        Reconnect the active provider.
        """

        self.disconnect()
        self.connect()

    @property
    def connected(self) -> bool:
        """
        Return connection state.
        """

        return self.provider.connected

    def health_check(self) -> bool:
        """
        Execute provider health check.
        """

        return self.provider.health_check()

    ###########################################################################
    # Blockchain Information
    ###########################################################################

    @abstractmethod
    def chain_id(self) -> int:
        """
        Return blockchain chain ID.
        """

    @abstractmethod
    def latest_block(self) -> Dict[str, Any]:
        """
        Return latest block.
        """

    @abstractmethod
    def get_block(
        self,
        block_identifier: Any,
    ) -> Dict[str, Any]:
        """
        Retrieve a block.
        """

    ###########################################################################
    # Accounts
    ###########################################################################

    @abstractmethod
    def get_balance(
        self,
        address: str,
    ) -> Any:
        """
        Return account balance.
        """

    ###########################################################################
    # Transactions
    ###########################################################################

    @abstractmethod
    def get_transaction(
        self,
        tx_hash: str,
    ) -> Dict[str, Any]:
        """
        Retrieve transaction details.
        """

    @abstractmethod
    def broadcast_transaction(
        self,
        raw_transaction: Any,
    ) -> str:
        """
        Broadcast a signed transaction.
        """

    @abstractmethod
    def get_transaction_receipt(
        self,
        tx_hash: str,
    ) -> Dict[str, Any]:
        """
        Retrieve transaction receipt.
        """

    ###########################################################################
    # Fees
    ###########################################################################

    @abstractmethod
    def estimate_gas(
        self,
        transaction: Dict[str, Any],
    ) -> int:
        """
        Estimate transaction fee.
        """

    @abstractmethod
    def gas_price(self) -> Any:
        """
        Return current network gas price.

        For non-EVM chains this may return the
        equivalent network fee.
        """

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize blockchain.
        """

        return {
            "blockchain": self.blockchain,
            "network": self.network,
            "connected": self.connected,
            "provider": (
                self.provider.provider_name
                if hasattr(self.provider, "provider_name")
                else self.provider.__class__.__name__
            ),
        }

    ###########################################################################
    # Magic Methods
    ###########################################################################

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"blockchain={self.blockchain!r}, "
            f"network={self.network!r}, "
            f"connected={self.connected})"
        )