"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.storage

Purpose
-------
Enterprise wallet storage abstraction.

This module provides persistent storage services for wallet objects.

The storage layer is responsible only for persistence and retrieval.

It does NOT perform:

- encryption
- validation
- blockchain communication
- wallet generation

Architecture
------------

WalletManager
      |
      ▼
WalletStorage
      |
      ├── Save
      ├── Load
      ├── Delete
      ├── Backup
      └── Restore


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


import json


from pathlib import Path


from typing import Dict
from typing import List


from wallets.wallet import Wallet


from wallets.exceptions import (
    WalletNotFoundError,
    WalletValidationError,
)



###############################################################################
# Wallet Storage
###############################################################################


class WalletStorage:
    """
    Enterprise wallet persistence service.

    Responsible only for storing and retrieving wallets.
    """


    ###########################################################################
    # Construction
    ###########################################################################


    def __init__(
        self,
        storage_path: str = "data/wallets",
    ) -> None:
        """
        Initialize wallet storage.

        Parameters
        ----------
        storage_path:
            Directory where wallets are stored.
        """


        if not isinstance(
            storage_path,
            str,
        ):

            raise WalletValidationError(
                "Storage path must be a string."
            )


        if not storage_path.strip():

            raise WalletValidationError(
                "Storage path cannot be empty."
            )


        self.storage_path = Path(
            storage_path
        )


        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )



    ###########################################################################
    # Internal Helpers
    ###########################################################################


    def _wallet_path(
        self,
        wallet_id: str,
    ) -> Path:
        """
        Build wallet file path.
        """


        if not wallet_id:

            raise WalletValidationError(
                "Wallet ID is required."
            )


        return (
            self.storage_path /
            f"{wallet_id}.json"
        )



    def _read_json(
        self,
        path: Path,
    ) -> Dict:
        """
        Read JSON wallet file.
        """


        if not path.exists():

            raise WalletNotFoundError(
                f"Wallet not found: {path.stem}"
            )


        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)



    def _write_json(
        self,
        path: Path,
        data: Dict,
    ) -> None:
        """
        Write JSON wallet file.
        """


        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                sort_keys=True,
            )
        ###########################################################################
    # Wallet Persistence
    ###########################################################################


    def save_wallet(
        self,
        wallet: Wallet,
        overwrite: bool = False,
    ) -> None:
        """
        Persist wallet to storage.

        Parameters
        ----------
        wallet:
            Wallet instance.

        overwrite:
            Allow replacing existing wallet.
        """


        if not isinstance(
            wallet,
            Wallet,
        ):

            raise WalletValidationError(
                "Expected Wallet instance."
            )


        wallet_path = self._wallet_path(
            wallet.wallet_id
        )


        if (
            wallet_path.exists()
            and not overwrite
        ):

            raise WalletValidationError(
                f"Wallet already exists: {wallet.wallet_id}"
            )


        self._write_json(
            wallet_path,
            wallet.to_dict(),
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


        data = self._read_json(
            self._wallet_path(
                wallet_id
            )
        )


        return Wallet.from_dict(
            data
        )



    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Delete wallet from storage.

        Parameters
        ----------
        wallet_id:
            Wallet identifier.
        """


        wallet_path = self._wallet_path(
            wallet_id
        )


        if not wallet_path.exists():

            raise WalletNotFoundError(
                f"Wallet '{wallet_id}' not found."
            )


        wallet_path.unlink()



    def wallet_exists(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Check whether wallet exists.

        Returns
        -------
        bool
        """


        return self._wallet_path(
            wallet_id
        ).exists()
        ###########################################################################
    # Storage Management
    ###########################################################################


    def list_wallets(
        self,
    ) -> List[str]:
        """
        Return all stored wallet identifiers.

        Returns
        -------
        List[str]
            Wallet IDs.
        """


        return sorted(
            path.stem
            for path in self.storage_path.glob(
                "*.json"
            )
        )



    def count_wallets(
        self,
    ) -> int:
        """
        Return number of stored wallets.

        Returns
        -------
        int
            Wallet count.
        """


        return len(
            self.list_wallets()
        )



    def clear(
        self,
    ) -> int:
        """
        Remove every wallet from storage.

        Returns
        -------
        int
            Number of wallets deleted.
        """


        wallet_ids = self.list_wallets()


        deleted = 0


        for wallet_id in wallet_ids:

            self.delete_wallet(
                wallet_id
            )

            deleted += 1


        return deleted



    ###########################################################################
    # Backup & Restore
    ###########################################################################


    def backup(
        self,
        wallet_id: str,
        backup_directory: str,
    ) -> Path:
        """
        Create wallet backup.

        Parameters
        ----------
        wallet_id:
            Wallet identifier.

        backup_directory:
            Backup destination.

        Returns
        -------
        Path
            Backup file.
        """


        from shutil import copy2


        source = self._wallet_path(
            wallet_id
        )


        if not source.exists():

            raise WalletNotFoundError(
                f"Wallet '{wallet_id}' not found."
            )


        destination_dir = Path(
            backup_directory
        )


        destination_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


        destination = (
            destination_dir /
            source.name
        )


        copy2(
            source,
            destination,
        )


        return destination



    def restore(
        self,
        backup_file: str,
    ) -> Wallet:
        """
        Restore wallet from backup.

        Parameters
        ----------
        backup_file:
            Backup JSON file.

        Returns
        -------
        Wallet
            Restored wallet.
        """


        from shutil import copy2


        source = Path(
            backup_file
        )


        if not source.exists():

            raise WalletNotFoundError(
                f"Backup file not found: {backup_file}"
            )


        destination = (
            self.storage_path /
            source.name
        )


        copy2(
            source,
            destination,
        )


        return self.load_wallet(
            source.stem
        )
        ###########################################################################
    # Information
    ###########################################################################


    def info(
        self,
    ) -> Dict[str, object]:
        """
        Return storage information.

        Returns
        -------
        dict
            Storage metadata.
        """


        return {

            "storage_path":
                str(
                    self.storage_path
                ),

            "wallet_count":
                self.count_wallets(),

            "backend":
                "JSON",

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

            f"WalletStorage("
            f"path='{self.storage_path}', "
            f"wallets={self.count_wallets()}"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable description.
        """


        return (

            f"Wallet storage "
            f"({self.count_wallets()} wallets)"

        )



###############################################################################
# Module Exports
###############################################################################


__all__ = [
    "WalletStorage",
]



###############################################################################
# End of wallets.storage
###############################################################################