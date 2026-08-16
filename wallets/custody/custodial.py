"""
Universal Blockchain Platform (UBP)

Module:
wallets.custody.custodial

Purpose:
Custodial wallet custody abstraction.

Architecture:
    Wallet
      ↓
    CustodyProvider
      ↓
    CustodialProvider
      ↓
    Future HSM / MPC / secure signing backend

This module defines the custodial boundary without
coupling the wallet layer to a particular HSM, MPC,
cloud KMS, or external custody vendor.

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.0.0
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from core.logger import get_logger

from wallets.custody.base import (
    CustodyProvider,
    CustodyType,
)


logger = get_logger(__name__)


class CustodialProvider(CustodyProvider):
    """
    Custodial wallet provider.

    The platform controls signing authority through a
    dedicated custody backend.

    IMPORTANT
    ---------
    This class is an architectural custody interface.
    It does not store raw private keys and does not
    implement production custody by itself.

    A future production implementation may connect this
    interface to an HSM, MPC system, KMS, or dedicated
    custody service.
    """

    def __init__(
        self,
        backend: Any | None = None,
    ) -> None:
        """
        Initialize the custodial provider.

        Parameters
        ----------
        backend : Any | None
            Optional secure signing backend.

        Notes
        -----
        The backend is intentionally abstract. UBP does
        not assume a particular custody technology.
        """

        self._backend = backend

        self._wallets: dict[
            str,
            dict[str, Any],
        ] = {}

        self._unlocked_wallets: set[str] = set()

        logger.info(
            "CustodialProvider initialized."
        )

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def custody_type(
        self,
    ) -> str:
        """
        Return the custody model.
        """

        return CustodyType.CUSTODIAL

    ###########################################################################
    # Backend
    ###########################################################################

    @property
    def backend(
        self,
    ) -> Any | None:
        """
        Return the configured custody backend.

        The backend itself is responsible for secure
        key management and signing.
        """

        return self._backend

    ###########################################################################
    # Wallet Lifecycle
    ###########################################################################

    def create_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Create a custodial wallet record.

        Production key generation should eventually be
        delegated to the secure custody backend.

        Parameters
        ----------
        options : Any
            Wallet creation options.

        Returns
        -------
        dict[str, Any]
            Wallet metadata.
        """

        wallet_id = str(
            options.get(
                "wallet_id",
                uuid4(),
            )
        )

        if wallet_id in self._wallets:
            raise ValueError(
                f"Wallet '{wallet_id}' already exists."
            )

        record = {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": "LOCKED",
            "backend": (
                self._backend.__class__.__name__
                if self._backend is not None
                else None
            ),
        }

        self._wallets[wallet_id] = record

        logger.info(
            "Created custodial wallet '%s'.",
            wallet_id,
        )

        return dict(record)

    def import_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Import an existing custodial wallet.

        Production implementations should perform import
        through the secure custody backend.

        Raw private keys must never be persisted directly
        by this class.

        Parameters
        ----------
        options : Any
            Import configuration.

        Returns
        -------
        dict[str, Any]
            Wallet metadata.
        """

        wallet_id = str(
            options.get(
                "wallet_id",
                uuid4(),
            )
        )

        if wallet_id in self._wallets:
            raise ValueError(
                f"Wallet '{wallet_id}' already exists."
            )

        record = {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": "LOCKED",
            "imported": True,
            "backend": (
                self._backend.__class__.__name__
                if self._backend is not None
                else None
            ),
        }

        self._wallets[wallet_id] = record

        logger.info(
            "Imported custodial wallet '%s'.",
            wallet_id,
        )

        return dict(record)

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Delete or deactivate a custodial wallet.

        Production implementations should coordinate
        deletion/deactivation with the custody backend.
        """

        self._require_wallet(
            wallet_id
        )

        self._unlocked_wallets.discard(
            wallet_id
        )

        del self._wallets[wallet_id]

        logger.info(
            "Deleted custodial wallet '%s'.",
            wallet_id,
        )

    ###########################################################################
    # Locking
    ###########################################################################

    def lock(
        self,
        wallet_id: str,
    ) -> None:
        """
        Lock custodial wallet signing authority.
        """

        self._require_wallet(
            wallet_id
        )

        self._unlocked_wallets.discard(
            wallet_id
        )

        self._wallets[wallet_id][
            "status"
        ] = "LOCKED"

        logger.info(
            "Locked custodial wallet '%s'.",
            wallet_id,
        )

    def unlock(
        self,
        wallet_id: str,
        **credentials: Any,
    ) -> bool:
        """
        Request access to custodial signing authority.

        Credentials are passed to the secure backend when
        a backend is available.

        This class never stores credentials.
        """

        self._require_wallet(
            wallet_id
        )

        if not credentials:
            raise ValueError(
                "Unlock credentials are required."
            )

        if self._backend is None:
            raise RuntimeError(
                "No custodial backend is configured."
            )

        unlock_method = getattr(
            self._backend,
            "unlock",
            None,
        )

        if not callable(
            unlock_method
        ):
            raise RuntimeError(
                "Custodial backend does not "
                "support unlock operations."
            )

        unlocked = bool(
            unlock_method(
                wallet_id,
                **credentials,
            )
        )

        if unlocked:

            self._unlocked_wallets.add(
                wallet_id
            )

            self._wallets[wallet_id][
                "status"
            ] = "UNLOCKED"

        return unlocked

    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Determine whether signing authority is available.
        """

        self._require_wallet(
            wallet_id
        )

        return wallet_id in (
            self._unlocked_wallets
        )

    ###########################################################################
    # Signing
    ###########################################################################

    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign a transaction using the secure custody backend.

        The custodial provider never receives or exposes
        raw private key material.
        """

        self._require_wallet(
            wallet_id
        )

        if not self.is_unlocked(
            wallet_id
        ):
            raise PermissionError(
                "Wallet must be unlocked before signing."
            )

        if not isinstance(
            transaction,
            dict,
        ):
            raise TypeError(
                "Transaction must be a dictionary."
            )

        if self._backend is None:
            raise RuntimeError(
                "No custodial signing backend is configured."
            )

        sign_method = getattr(
            self._backend,
            "sign_transaction",
            None,
        )

        if not callable(
            sign_method
        ):
            raise RuntimeError(
                "Custodial backend does not "
                "support transaction signing."
            )

        signed_transaction = sign_method(
            wallet_id,
            transaction,
        )

        if not isinstance(
            signed_transaction,
            str,
        ):
            raise TypeError(
                "Custodial backend must return "
                "a serialized signed transaction."
            )

        return signed_transaction

    ###########################################################################
    # Public Information
    ###########################################################################

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        """
        Retrieve a public key from the custody backend.
        """

        self._require_wallet(
            wallet_id
        )

        if self._backend is None:
            raise RuntimeError(
                "No custodial backend is configured."
            )

        method = getattr(
            self._backend,
            "get_public_key",
            None,
        )

        if not callable(method):
            raise RuntimeError(
                "Custodial backend does not "
                "support public-key retrieval."
            )

        return str(
            method(wallet_id)
        )

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        """
        Retrieve a blockchain-specific address.

        Address derivation remains the responsibility of
        the blockchain adapter or secure custody backend.
        """

        self._require_wallet(
            wallet_id
        )

        if not blockchain:
            raise ValueError(
                "Blockchain is required."
            )

        if self._backend is None:
            raise RuntimeError(
                "No custodial backend is configured."
            )

        method = getattr(
            self._backend,
            "get_address",
            None,
        )

        if not callable(method):
            raise RuntimeError(
                "Custodial backend does not "
                "support address retrieval."
            )

        return str(
            method(
                wallet_id,
                blockchain,
            )
        )

    ###########################################################################
    # Status
    ###########################################################################

    def get_status(
        self,
        wallet_id: str,
    ) -> dict[str, Any]:
        """
        Return custodial wallet status.
        """

        self._require_wallet(
            wallet_id
        )

        return {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": self._wallets[
                wallet_id
            ]["status"],
            "unlocked": (
                wallet_id
                in self._unlocked_wallets
            ),
            "backend_configured": (
                self._backend is not None
            ),
        }

    ###########################################################################
    # Internal Helpers
    ###########################################################################

    def _require_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Verify that a wallet exists.
        """

        if wallet_id not in self._wallets:
            raise KeyError(
                f"Wallet '{wallet_id}' not found."
            )

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
            f"wallets={len(self._wallets)}, "
            f"custody_type={self.custody_type!r}, "
            f"backend_configured="
            f"{self._backend is not None}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "CustodialProvider",
]


###############################################################################
# End of File
###############################################################################
