"""
Universal Blockchain Platform (UBP)

Module
------
wallets.blockchain.base

Purpose
-------
Abstract blockchain wallet interface for UBP.

Architecture
------------
Wallet
    |
    +-- CustodyProvider
    |
    +-- BlockchainWallet
             |
             +-- EthereumWallet
             +-- BitcoinWallet
             +-- TronWallet

Responsibilities
----------------
- Define the common blockchain-wallet contract
- Define wallet address operations
- Define balance operations
- Define transaction preparation
- Define transaction broadcasting
- Define transaction inspection
- Define blockchain/network identity

Not Responsible For
-------------------
- Private-key storage
- Custody implementation
- Blockchain-specific cryptographic implementation
- Provider management
- Persistent wallet storage

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


###############################################################################
# Blockchain Wallet
###############################################################################


class BlockchainWallet(ABC):
    """
    Abstract interface for blockchain-specific wallet implementations.

    The wallet abstraction provides a common interface for different
    blockchains while keeping blockchain-specific implementation details
    inside their respective wallet classes.
    """

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    @abstractmethod
    def blockchain(self) -> str:
        """
        Return the blockchain identifier.

        Returns
        -------
        str
            Blockchain name.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def network(self) -> str:
        """
        Return the blockchain network.

        Returns
        -------
        str
            Network identifier.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def wallet_id(self) -> str:
        """
        Return the UBP wallet identifier.

        Returns
        -------
        str
            Wallet identifier.
        """

        raise NotImplementedError

    ###########################################################################
    # Address
    ###########################################################################

    @abstractmethod
    def get_address(self) -> str:
        """
        Return the blockchain wallet address.

        Returns
        -------
        str
            Blockchain address.
        """

        raise NotImplementedError

    ###########################################################################
    # Balance
    ###########################################################################

    @abstractmethod
    def get_balance(self) -> dict[str, Any]:
        """
        Retrieve the wallet balance.

        Returns
        -------
        dict[str, Any]
            Balance information.

        Notes
        -----
        The concrete implementation determines the blockchain-specific
        balance representation.
        """

        raise NotImplementedError

    ###########################################################################
    # Transaction Preparation
    ###########################################################################

    @abstractmethod
    def prepare_transaction(
        self,
        transaction: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare a blockchain transaction.

        Parameters
        ----------
        transaction : dict[str, Any]
            Transaction request.

        Returns
        -------
        dict[str, Any]
            Blockchain-ready transaction payload.
        """

        raise NotImplementedError

    ###########################################################################
    # Transaction Signing
    ###########################################################################

    @abstractmethod
    def sign_transaction(
        self,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign a prepared blockchain transaction.

        Parameters
        ----------
        transaction : dict[str, Any]
            Prepared transaction payload.

        Returns
        -------
        str
            Serialized signed transaction.

        Notes
        -----
        Signing authority is supplied by the custody layer.
        The blockchain wallet must not assume ownership of private-key
        storage.
        """

        raise NotImplementedError

    ###########################################################################
    # Transaction Broadcasting
    ###########################################################################

    @abstractmethod
    def broadcast_transaction(
        self,
        signed_transaction: str,
    ) -> dict[str, Any]:
        """
        Broadcast a signed transaction to the blockchain.

        Parameters
        ----------
        signed_transaction : str
            Serialized signed transaction.

        Returns
        -------
        dict[str, Any]
            Broadcast result.
        """

        raise NotImplementedError

    ###########################################################################
    # Transaction Inspection
    ###########################################################################

    @abstractmethod
    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction information.

        Parameters
        ----------
        transaction_hash : str
            Blockchain transaction identifier.

        Returns
        -------
        dict[str, Any]
            Transaction information.
        """

        raise NotImplementedError

    ###########################################################################
    # Transaction Status
    ###########################################################################

    @abstractmethod
    def get_transaction_status(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction status.

        Parameters
        ----------
        transaction_hash : str
            Blockchain transaction identifier.

        Returns
        -------
        dict[str, Any]
            Transaction status information.
        """

        raise NotImplementedError

    ###########################################################################
    # Blockchain State
    ###########################################################################

    @abstractmethod
    def get_latest_block(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest blockchain block information.

        Returns
        -------
        dict[str, Any]
            Latest block information.
        """

        raise NotImplementedError

    ###########################################################################
    # Wallet Status
    ###########################################################################

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Return wallet status information.

        Returns
        -------
        dict[str, Any]
            Wallet status report.
        """

        raise NotImplementedError

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"wallet_id={self.wallet_id!r}, "
            f"blockchain={self.blockchain!r}, "
            f"network={self.network!r}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "BlockchainWallet",
]


###############################################################################
# End of File
###############################################################################
