"""
Universal Blockchain Platform (UBP)

Module
------
wallets.manager

Purpose
-------
Enterprise wallet orchestration layer.

The WalletManager coordinates the wallet subsystem by delegating work to
specialized services responsible for persistence, validation, encryption,
and custody.

The manager intentionally contains very little business logic.

Responsibilities
----------------
- Create wallets
- Validate wallets
- Persist wallets
- Load wallets
- Delete wallets
- Coordinate encryption
- Coordinate backup and restore
- Coordinate custody

The manager does NOT perform:
- Filesystem operations
- JSON serialization
- Cryptographic implementation
- Blockchain communication
- Private-key storage

Architecture
------------

                         WalletManager
                              |
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
   WalletStorage       WalletValidator     EncryptionManager
          |                                     
          ▼
        Wallet
          |
          ▼
   CustodyProvider
      /        \
     ▼          ▼
NonCustodial  Custodial

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise  (Step 4 — Type Contract Fix)
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

from wallets.wallet import Wallet
from wallets.storage import WalletStorage
from wallets.validators import WalletValidator
from wallets.encryption import EncryptionManager

from wallets.custody.base import (
    CustodyProvider,
    CustodyType,
)

from wallets.custody.non_custodial import (
    NonCustodialProvider,
)

from wallets.custody.custodial import (
    CustodialProvider,
)


###############################################################################
# Wallet Manager
###############################################################################


class WalletManager:
    """
    Enterprise wallet orchestration service.

    Coordinates wallet operations while delegating implementation details
    to specialized services.

    The WalletManager is custody-agnostic.

    A manager may operate with either:

        - NonCustodialProvider
        - CustodialProvider

    The manager never handles raw private keys.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        storage: Optional[WalletStorage] = None,
        validator: Optional[WalletValidator] = None,
        encryption: Optional[EncryptionManager] = None,
        custody_provider: Optional[CustodyProvider] = None,
    ) -> None:
        """
        Initialize wallet manager.

        Parameters
        ----------
        storage:
            Wallet persistence backend.

        validator:
            Wallet validation service.

        encryption:
            Wallet encryption service.

        custody_provider:
            Default custody provider.

        Notes
        -----
        If no custody provider is supplied, UBP defaults to the
        non-custodial custody model.
        """

        self.storage = (
            storage
            if storage is not None
            else WalletStorage()
        )

        self.validator = (
            validator
            if validator is not None
            else WalletValidator()
        )

        self.encryption = (
            encryption
            if encryption is not None
            else EncryptionManager()
        )

        self.custody_provider = (
            custody_provider
            if custody_provider is not None
            else NonCustodialProvider()
        )

    ###########################################################################
    # Wallet Creation
    ###########################################################################

    def create_wallet(
        self,
        wallet_id: str,
        address: str,
        network: str,
        wallet_type: str = "software",
        metadata: Optional[Dict[str, Any]] = None,
        custody_type: str = CustodyType.NON_CUSTODIAL,
    ) -> Wallet:
        """
        Create a wallet.

        Parameters
        ----------
        wallet_id:
            Unique wallet identifier.

        address:
            Blockchain wallet address.

        network:
            Blockchain network.

        wallet_type:
            Wallet category.

        metadata:
            Optional wallet metadata.

        custody_type:
            Wallet custody model.

        Returns
        -------
        Wallet
            Newly created wallet.
        """

        normalized_custody_type = (
            custody_type.strip().lower()
            if isinstance(custody_type, str)
            else custody_type
        )

        if normalized_custody_type == (
            CustodyType.NON_CUSTODIAL
        ):
            provider = (
                self.custody_provider
                if isinstance(
                    self.custody_provider,
                    NonCustodialProvider,
                )
                else NonCustodialProvider()
            )

        elif normalized_custody_type == (
            CustodyType.CUSTODIAL
        ):
            provider = (
                self.custody_provider
                if isinstance(
                    self.custody_provider,
                    CustodialProvider,
                )
                else CustodialProvider()
            )

        else:
            raise ValueError(
                f"Unsupported custody type: "
                f"{normalized_custody_type}"
            )

        provider.create_wallet(
            wallet_id=wallet_id,
        )

        wallet = Wallet(
            wallet_id=wallet_id,
            address=address,
            network=network,
            wallet_type=wallet_type,
            metadata=metadata,
            custody_type=normalized_custody_type,
            custody_provider=provider,
        )

        self.validator.validate_wallet(
            wallet
        )

        return wallet

    ###########################################################################
    # Custody Provider Management
    ###########################################################################

    def set_custody_provider(
        self,
        provider: CustodyProvider,
    ) -> None:
        """
        Set the default custody provider.

        Parameters
        ----------
        provider:
            CustodyProvider implementation.
        """

        if not isinstance(
            provider,
            CustodyProvider,
        ):
            raise TypeError(
                "provider must be a CustodyProvider."
            )

        self.custody_provider = provider

    def get_custody_provider(
        self,
    ) -> CustodyProvider:
        """
        Return the configured custody provider.
        """

        return self.custody_provider

    def get_custody_type(
        self,
    ) -> str:
        """
        Return the configured default custody type.
        """

        return self.custody_provider.custody_type

    ###########################################################################
    # Wallet Validation
    ###########################################################################

    def validate_wallet(
        self,
        wallet: Wallet,
    ) -> bool:
        """
        Validate a wallet.

        Parameters
        ----------
        wallet:
            Wallet instance.

        Returns
        -------
        bool
            True if validation succeeds.
        """

        return self.validator.validate_wallet(
            wallet
        )

    def validate_serialized(
        self,
        data: Dict[str, Any],
    ) -> bool:
        """
        Validate serialized wallet data.

        Parameters
        ----------
        data:
            Serialized wallet dictionary.

        Returns
        -------
        bool
            True if validation succeeds.
        """

        return self.validator.validate_serialized(
            data
        )

    ###########################################################################
    # Wallet Custody Operations
    ###########################################################################

    def attach_custody_provider(
        self,
        wallet: Wallet,
        provider: CustodyProvider,
    ) -> Wallet:
        """
        Attach a custody provider to a wallet.

        Parameters
        ----------
        wallet:
            Wallet instance.

        provider:
            Custody provider implementation.

        Returns
        -------
        Wallet
            Updated wallet.
        """

        if not isinstance(
            wallet,
            Wallet,
        ):
            raise TypeError(
                "wallet must be a Wallet instance."
            )

        if not isinstance(
            provider,
            CustodyProvider,
        ):
            raise TypeError(
                "provider must be a CustodyProvider."
            )

        wallet.set_custody_provider(
            provider
        )

        self.validator.validate_wallet(
            wallet
        )

        return wallet

    def lock_wallet(
        self,
        wallet: Wallet,
    ) -> None:
        """
        Lock a wallet.
        """

        if not isinstance(
            wallet,
            Wallet,
        ):
            raise TypeError(
                "wallet must be a Wallet instance."
            )

        wallet.lock()

    def unlock_wallet(
        self,
        wallet: Wallet,
        **credentials: Any,
    ) -> bool:
        """
        Unlock a wallet through its custody provider.
        """

        if not isinstance(
            wallet,
            Wallet,
        ):
            raise TypeError(
                "wallet must be a Wallet instance."
            )

        return wallet.unlock(
            **credentials
        )

    def get_wallet_custody_status(
        self,
        wallet: Wallet,
    ) -> Dict[str, Any]:
        """
        Return custody status for a wallet.
        """

        if not isinstance(
            wallet,
            Wallet,
        ):
            raise TypeError(
                "wallet must be a Wallet instance."
            )

        return wallet.get_custody_status()

    ###########################################################################
    # Persistence
    ###########################################################################

    def save_wallet(
        self,
        wallet: Wallet,
    ) -> None:
        """
        Validate and persist wallet.

        Parameters
        ----------
        wallet:
            Wallet instance.
        """

        self.validator.validate_wallet(
            wallet
        )

        self.storage.save_wallet(
            wallet
        )

    def load_wallet(
        self,
        wallet_id: str,
    ) -> Wallet:
        """
        Load wallet from storage.

        Parameters
        ----------
        wallet_id:
            Wallet identifier.

        Returns
        -------
        Wallet
            Loaded wallet.
        """

        wallet = self.storage.load_wallet(
            wallet_id
        )

        self.validator.validate_wallet(
            wallet
        )

        return wallet

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Delete wallet.

        Persistent deletion remains the responsibility of
        WalletStorage.

        Runtime custody state is removed through the wallet's
        custody provider when available.
        """

        wallet = None

        if self.storage.wallet_exists(
            wallet_id
        ):
            try:
                wallet = self.storage.load_wallet(
                    wallet_id
                )
            except Exception:
                wallet = None

        if (
            wallet is not None
            and wallet.custody_provider is not None
        ):
            try:
                wallet.custody_provider.delete_wallet(
                    wallet_id
                )
            except KeyError:
                pass

        self.storage.delete_wallet(
            wallet_id
        )

    ###########################################################################
    # Storage Operations
    ###########################################################################

    def wallet_exists(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Determine whether wallet exists.
        """

        return self.storage.wallet_exists(
            wallet_id
        )

    def list_wallets(
        self,
    ) -> list[str]:
        """
        Return stored wallet identifiers.
        """

        return self.storage.list_wallets()

    def count_wallets(
        self,
    ) -> int:
        """
        Return number of stored wallets.
        """

        return self.storage.count_wallets()

    def clear_storage(
        self,
    ) -> int:
        """
        Remove all stored wallets.

        Returns
        -------
        int
            Number of wallets deleted.
        """

        return self.storage.clear()

    ###########################################################################
    # Transaction Signing Boundary
    ###########################################################################

    def sign_transaction(
        self,
        wallet: Wallet,
        transaction: Dict[str, Any],
    ) -> str:
        """
        Sign a transaction through the wallet custody provider.

        Blockchain-specific transaction construction belongs
        to the appropriate blockchain layer.

        The WalletManager only coordinates custody.
        """

        if not isinstance(
            wallet,
            Wallet,
        ):
            raise TypeError(
                "wallet must be a Wallet instance."
            )

        wallet.require_unlocked()

        if wallet.custody_provider is None:
            raise RuntimeError(
                "Wallet has no custody provider."
            )

        return wallet.custody_provider.sign_transaction(
            wallet.wallet_id,
            transaction,
        )

    ###########################################################################
    # Backup & Restore
    ###########################################################################

    def backup_wallet(
        self,
        wallet_id: str,
        backup_directory: str,
    ):
        """
        Create backup of a single wallet.

        Parameters
        ----------
        wallet_id:
            Wallet identifier.

        backup_directory:
            Destination directory.

        Returns
        -------
        Path
            Backup file path.
        """

        return self.storage.backup(
            wallet_id,
            backup_directory,
        )

    def backup_storage(
        self,
        backup_directory: str,
    ) -> list:
        """
        Backup complete wallet storage.

        Parameters
        ----------
        backup_directory:
            Destination directory.

        Returns
        -------
        list
            Backup files created.
        """

        backups = []

        for wallet_id in self.list_wallets():

            backup_file = self.storage.backup(
                wallet_id,
                backup_directory,
            )

            backups.append(
                backup_file
            )

        return backups

    def restore_wallet(
        self,
        backup_file: str,
    ) -> Wallet:
        """
        Restore one wallet from backup.

        Parameters
        ----------
        backup_file:
            Backup JSON file.

        Returns
        -------
        Wallet
            Restored wallet.
        """

        wallet = self.storage.restore(
            backup_file
        )

        self.validator.validate_wallet(
            wallet
        )

        return wallet

    def restore_storage(
        self,
        backup_directory: str,
    ) -> list:
        """
        Restore complete wallet storage.

        Parameters
        ----------
        backup_directory:
            Backup directory.

        Returns
        -------
        list
            Restored wallets.
        """

        from pathlib import Path
        from shutil import copy2

        restored = []

        source_directory = Path(
            backup_directory
        )

        if not source_directory.exists():
            return restored

        for backup_file in source_directory.glob(
            "*.json"
        ):

            destination = (
                self.storage.storage_path
                / backup_file.name
            )

            copy2(
                backup_file,
                destination,
            )

            wallet = self.storage.load_wallet(
                backup_file.stem
            )

            self.validator.validate_wallet(
                wallet
            )

            restored.append(
                wallet
            )

        return restored

    ###########################################################################
    # Encryption
    ###########################################################################

    def encrypt_data(
        self,
        data: str | bytes,
        password: str,
        **options: Any,
    ) -> Dict[str, Any]:
        """
        Encrypt arbitrary data.

        Parameters
        ----------
        data:
            Data to encrypt.  Accepts str or bytes.

        password:
            Encryption password.

        options:
            Optional encryption configuration (KDF, iterations, etc.).

        Returns
        -------
        dict
            Encrypted payload dictionary.
        """

        return self.encryption.encrypt(
            data,
            password,
            **options,
        )

    def decrypt_data(
        self,
        encrypted_data: Dict[str, Any],
        password: str,
    ) -> str | bytes:
        """
        Decrypt encrypted data.

        Parameters
        ----------
        encrypted_data:
            Encrypted payload dictionary.

        password:
            Decryption password.

        Returns
        -------
        str | bytes
            Decrypted plaintext.
        """

        return self.encryption.decrypt(
            encrypted_data,
            password,
        )

    ###########################################################################
    # Information
    ###########################################################################

    def info(
        self,
    ) -> Dict[str, Any]:
        """
        Return manager information.

        Returns
        -------
        dict
            Manager metadata.
        """

        return {
            "service":
                "Wallet Manager",

            "version":
                "2.1 Enterprise",

            "wallets":
                self.count_wallets(),

            "storage":
                self.storage.info(),

            "validator":
                self.validator.__class__.__name__,

            "encryption":
                self.encryption.__class__.__name__,

            "custody_provider":
                self.custody_provider.__class__.__name__,

            "custody_type":
                self.custody_provider.custody_type,

            "wallet_count":
                self.count_wallets(),
        }

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"WalletManager("
            f"wallets={self.count_wallets()}, "
            f"storage='{self.storage.storage_path}', "
            f"custody='{self.get_custody_type()}'"
            f")"
        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable description.
        """

        return (
            f"Wallet Manager "
            f"({self.count_wallets()} wallets)"
        )


###############################################################################
# Module Exports
###############################################################################

__all__ = [
    "WalletManager",
]


###############################################################################
# End of wallets.manager
###############################################################################