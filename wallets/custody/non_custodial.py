"""
Universal Blockchain Platform (UBP)

Module:
wallets.custody.non_custodial

Purpose:
Non-custodial wallet custody implementation.

Architecture:
    Wallet
      ↓
    CustodyProvider
      ↓
    NonCustodialProvider
      ↓
    Existing wallet key/encryption/storage components

The provider is blockchain-agnostic.

Blockchain-specific address derivation and transaction
serialization/signing should remain outside this module.

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


class NonCustodialProvider(CustodyProvider):
    """
    UBP non-custodial custody provider.

    The user retains control of the wallet's signing authority.

    This class deliberately does not expose private keys through
    its public interface. Key generation, encryption and persistent
    storage are delegated to the existing wallet subsystems.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize the non-custodial provider.
        """

        self._wallets: dict[str, dict[str, Any]] = {}
        self._unlocked_wallets: set[str] = set()

        logger.info(
            "NonCustodialProvider initialized."
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

        return CustodyType.NON_CUSTODIAL

    ###########################################################################
    # Wallet Lifecycle
    ###########################################################################

    def create_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Create a non-custodial wallet record.

        The provider creates the custody identity while leaving
        actual key generation to the wallet key subsystem.

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
        }

        self._wallets[wallet_id] = record

        logger.info(
            "Created non-custodial wallet '%s'.",
            wallet_id,
        )

        return dict(record)

    def import_wallet(
        self,
        **options: Any,
    ) -> dict[str, Any]:
        """
        Import an existing non-custodial wallet.

        Sensitive key material is intentionally not retained
        in the provider's runtime metadata.

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
        }

        self._wallets[wallet_id] = record

        logger.info(
            "Imported non-custodial wallet '%s'.",
            wallet_id,
        )

        return dict(record)

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Remove a wallet from the provider runtime registry.

        Persistent encrypted wallet deletion belongs to the
        wallet storage layer.
        """

        if wallet_id not in self._wallets:
            raise KeyError(
                f"Wallet '{wallet_id}' not found."
            )

        self._unlocked_wallets.discard(
            wallet_id
        )

        del self._wallets[wallet_id]

        logger.info(
            "Deleted non-custodial wallet '%s'.",
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
        Lock wallet signing authority.
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
            "Locked non-custodial wallet '%s'.",
            wallet_id,
        )

    def unlock(
        self,
        wallet_id: str,
        **credentials: Any,
    ) -> bool:
        """
        Unlock wallet signing authority.

        Credential verification will ultimately be delegated to
        the existing encryption/key-management subsystem.

        This initial implementation establishes the custody
        interface without storing credentials in memory.
        """

        self._require_wallet(
            wallet_id
        )

        if not credentials:
            raise ValueError(
                "Unlock credentials are required."
            )

        self._unlocked_wallets.add(
            wallet_id
        )

        self._wallets[wallet_id][
            "status"
        ] = "UNLOCKED"

        logger.info(
            "Unlocked non-custodial wallet '%s'.",
            wallet_id,
        )

        return True

    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Determine whether wallet signing authority
        is currently unlocked.
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
        Sign a transaction through the wallet key subsystem.

        Blockchain-specific transaction serialization and signing
        will be connected through blockchain adapters.

        This method intentionally refuses to fabricate a signed
        transaction.
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

        raise NotImplementedError(
            "Blockchain-specific signing must be "
            "implemented by a wallet blockchain adapter."
        )

    ###########################################################################
    # Public Information
    ###########################################################################

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        """
        Return the wallet public key.

        Public-key retrieval will be delegated to the wallet
        key subsystem once the wallet integration layer is connected.
        """

        self._require_wallet(
            wallet_id
        )

        raise NotImplementedError(
            "Public-key retrieval must be implemented "
            "by the wallet key subsystem."
        )

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        """
        Retrieve a blockchain-specific wallet address.

        Address derivation belongs to the corresponding blockchain
        adapter, not to the custody provider.
        """

        self._require_wallet(
            wallet_id
        )

        if not blockchain:
            raise ValueError(
                "Blockchain is required."
            )

        raise NotImplementedError(
            "Blockchain-specific address derivation "
            "must be implemented by a wallet adapter."
        )

    ###########################################################################
    # Status
    ###########################################################################

    def get_status(
        self,
        wallet_id: str,
    ) -> dict[str, Any]:
        """
        Return custody status information.
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
            f"custody_type={self.custody_type!r}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "NonCustodialProvider",
]


###############################################################################
# End of File
###############################################################################
