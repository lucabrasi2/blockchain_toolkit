"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.manager

Purpose
-------
Enterprise wallet orchestration layer.

The WalletManager coordinates the wallet subsystem by delegating work to
specialized services responsible for persistence, validation and encryption.

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

The manager does NOT perform:
- Filesystem operations
- JSON serialization
- Cryptographic implementation
- Blockchain communication


Architecture
------------

                WalletManager
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
WalletStorage   WalletValidator   EncryptionManager
      │
      ▼
    Wallet


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
from typing import Dict
from typing import Optional


from wallets.wallet import Wallet
from wallets.storage import WalletStorage
from wallets.validators import WalletValidator
from wallets.encryption import EncryptionManager



###############################################################################
# Wallet Manager
###############################################################################


class WalletManager:
    """
    Enterprise wallet orchestration service.

    Coordinates wallet operations while delegating implementation details
    to specialized services.
    """


    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
        storage: Optional[WalletStorage] = None,
        validator: Optional[WalletValidator] = None,
        encryption: Optional[EncryptionManager] = None,
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

        Returns
        -------
        Wallet
            Newly created wallet.
        """


        wallet = Wallet(
            wallet_id=wallet_id,
            address=address,
            network=network,
            wallet_type=wallet_type,
            metadata=metadata,
        )


        self.validator.validate_wallet(
            wallet
        )


        return wallet
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

        Parameters
        ----------
        wallet_id:
            Wallet identifier.
        """


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
                self.storage.storage_path /
                backup_file.name
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
        data: str,
        password: str,
    ) -> str:
        """
        Encrypt arbitrary data.

        Returns
        -------
        str
            Encrypted data.
        """


        return self.encryption.encrypt(
            data,
            password,
        )



    def decrypt_data(
        self,
        encrypted_data: str,
        password: str,
    ) -> str:
        """
        Decrypt encrypted data.

        Returns
        -------
        str
            Decrypted data.
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
                "2.0 Enterprise",

            "wallets":
                self.count_wallets(),

            "storage":
                self.storage.info(),

            "validator":
                self.validator.__class__.__name__,

            "encryption":
                self.encryption.__class__.__name__,

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
            f"storage='{self.storage.storage_path}'"
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