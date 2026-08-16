"""
Universal Blockchain Platform (UBP)

Module:
wallets.custody.base

Purpose:
Abstract custody interface for UBP wallets.

Architecture:
    Wallet
      ↓
    CustodyProvider
      ↓
    Non-Custodial / Custodial implementation

The custody layer is intentionally blockchain-agnostic.

It must not contain Ethereum, Bitcoin, TRON,
or any other blockchain-specific logic.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.0.0
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from core.logger import get_logger


logger = get_logger(__name__)


class CustodyType:
    """
    Supported wallet custody models.
    """

    NON_CUSTODIAL = "non_custodial"
    CUSTODIAL = "custodial"


class CustodyProvider(ABC):
    """
    Abstract interface for wallet custody providers.

    A custody provider controls how wallet key material
    is accessed and how transaction-signing authority
    is provided.

    The wallet itself does not need to know whether
    the underlying custody model is custodial or
    non-custodial.

    Implementations must never expose private key
    material unnecessarily.
    """

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    @abstractmethod
    def custody_type(self) -> str:
        """
        Return the custody model.

        Returns
        -------
        str
            CustodyType.NON_CUSTODIAL or
            CustodyType.CUSTODIAL.
        """

        raise NotImplementedError

    ###########################################################################
    # Wallet Lifecycle
    ###########################################################################

    @abstractmethod
    def create_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Create wallet key material.

        Implementations determine how the underlying
        key material is generated and protected.

        Returns
        -------
        dict[str, Any]
            Wallet creation metadata.

        Notes
        -----
        Sensitive key material should not be returned
        unless explicitly required by the implementation.
        """

        raise NotImplementedError

    @abstractmethod
    def import_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Import existing wallet material.

        Implementations determine how imported material
        is validated and protected.

        Returns
        -------
        dict[str, Any]
            Wallet import metadata.
        """

        raise NotImplementedError

    @abstractmethod
    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Delete or deactivate wallet custody data.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.
        """

        raise NotImplementedError

    ###########################################################################
    # Locking
    ###########################################################################

    @abstractmethod
    def lock(
        self,
        wallet_id: str,
    ) -> None:
        """
        Lock wallet signing authority.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.
        """

        raise NotImplementedError

    @abstractmethod
    def unlock(
        self,
        wallet_id: str,
        **credentials: Any,
    ) -> bool:
        """
        Unlock wallet signing authority.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        credentials : Any
            Credentials required by the custody
            implementation.

        Returns
        -------
        bool
            True if the wallet was successfully unlocked.
        """

        raise NotImplementedError

    @abstractmethod
    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Determine whether wallet signing authority
        is currently unlocked.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        Returns
        -------
        bool
            True when signing authority is available.
        """

        raise NotImplementedError

    ###########################################################################
    # Signing
    ###########################################################################

    @abstractmethod
    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign a blockchain transaction.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        transaction : dict[str, Any]
            Blockchain transaction payload.

        Returns
        -------
        str
            Serialized signed transaction.

        Notes
        -----
        The custody provider owns signing authority.
        The wallet layer should not need direct access
        to private key material.
        """

        raise NotImplementedError

    ###########################################################################
    # Public Information
    ###########################################################################

    @abstractmethod
    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        """
        Retrieve the wallet public key.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        Returns
        -------
        str
            Public key.
        """

        raise NotImplementedError

    @abstractmethod
    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        """
        Derive or retrieve a blockchain address.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        blockchain : str
            Blockchain identifier.

        Returns
        -------
        str
            Blockchain address.
        """

        raise NotImplementedError

    ###########################################################################
    # Status
    ###########################################################################

    @abstractmethod
    def get_status(
        self,
        wallet_id: str,
    ) -> dict[str, Any]:
        """
        Return custody status information.

        Parameters
        ----------
        wallet_id : str
            Wallet identifier.

        Returns
        -------
        dict[str, Any]
            Custody status report.
        """

        raise NotImplementedError

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"custody_type={self.custody_type!r}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "CustodyType",
    "CustodyProvider",
]


###############################################################################
# End of File
###############################################################################
