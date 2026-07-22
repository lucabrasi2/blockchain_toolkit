"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.wallet

Purpose
-------
Enterprise wallet entity model.

This module defines the core wallet object used throughout the Universal
Blockchain Platform.

Responsibilities
----------------
- Represent wallet identity
- Maintain wallet state
- Manage wallet metadata
- Handle wallet locking lifecycle
- Provide serialization support


Architecture
------------

Wallet

    |
    ├── WalletManager
    |
    ├── StorageManager
    |
    ├── ValidatorManager
    |
    └── EncryptionManager


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


from datetime import datetime, timezone

from typing import Any, Dict, Optional


from wallets.exceptions import (
    WalletConfigurationError,
    WalletValidationError,
    WalletLockedError,
)


###############################################################################
# Wallet Entity
###############################################################################


class Wallet:
    """
    Core wallet representation.

    A wallet represents a blockchain account identity.
    """



    def __init__(
        self,
        wallet_id: str,
        address: str,
        network: str,
        wallet_type: str = "software",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize wallet.

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
            Additional wallet information.
        """


        self.wallet_id = self._validate_wallet_id(
            wallet_id
        )


        self.address = self._validate_address(
            address
        )


        self.network = self._validate_network(
            network
        )


        self.wallet_type = wallet_type


        self.metadata = (
            metadata
            if metadata is not None
            else {}
        )


        self.created_at = datetime.now(
            timezone.utc
        )


        self.updated_at = datetime.now(
            timezone.utc
        )


        self.is_locked = True
    
        ###############################################################################
    # Validation Helpers
    ###############################################################################

    def _validate_wallet_id(
        self,
        wallet_id: str,
    ) -> str:
        """
        Validate wallet identifier.
        """

        if not isinstance(
            wallet_id,
            str,
        ):

            raise WalletConfigurationError(
                "Wallet ID must be a string"
            )


        if not wallet_id.strip():

            raise WalletConfigurationError(
                "Wallet ID cannot be empty"
            )


        return wallet_id.strip()



    def _validate_address(
        self,
        address: str,
    ) -> str:
        """
        Validate wallet address.
        """

        if not isinstance(
            address,
            str,
        ):

            raise WalletValidationError(
                "Wallet address must be a string"
            )


        if not address.strip():

            raise WalletValidationError(
                "Wallet address cannot be empty"
            )


        return address.strip()



    def _validate_network(
        self,
        network: str,
    ) -> str:
        """
        Validate blockchain network.
        """

        if not isinstance(
            network,
            str,
        ):

            raise WalletValidationError(
                "Network must be a string"
            )


        if not network.strip():

            raise WalletValidationError(
                "Network cannot be empty"
            )


        return network.lower().strip()



    ###############################################################################
    # Wallet Security Lifecycle
    ###############################################################################

    def lock(
        self,
    ) -> None:
        """
        Lock wallet.

        Locked wallets should not expose sensitive operations.
        """

        self.is_locked = True

        self.updated_at = datetime.now(
            timezone.utc
        )



    def unlock(
        self,
    ) -> None:
        """
        Unlock wallet.
        """

        self.is_locked = False

        self.updated_at = datetime.now(
            timezone.utc
        )



    def require_unlocked(
        self,
    ) -> None:
        """
        Ensure wallet is unlocked.

        Raises
        ------
        WalletLockedError
            If wallet is locked.
        """

        if self.is_locked:

            raise WalletLockedError(
                "Wallet is locked"
            )



    ###############################################################################
    # Metadata Management
    ###############################################################################

    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or update wallet metadata.
        """

        if not isinstance(
            key,
            str,
        ):

            raise WalletValidationError(
                "Metadata key must be a string"
            )


        if not key.strip():

            raise WalletValidationError(
                "Metadata key cannot be empty"
            )


        self.metadata[key] = value


        self.updated_at = datetime.now(
            timezone.utc
        )



    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )
        ###############################################################################
    # Serialization
    ###############################################################################

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert wallet object into dictionary form.

        Sensitive cryptographic material is intentionally excluded.
        """

        return {

            "wallet_id": self.wallet_id,

            "address": self.address,

            "network": self.network,

            "wallet_type": self.wallet_type,

            "metadata": self.metadata.copy(),

            "created_at": self.created_at.isoformat(),

            "updated_at": self.updated_at.isoformat(),

            "is_locked": self.is_locked,

        }



    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Wallet":
        """
        Recreate wallet object from dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):

            raise WalletValidationError(
                "Wallet data must be a dictionary"
            )


        wallet = cls(
            wallet_id=data.get(
                "wallet_id"
            ),

            address=data.get(
                "address"
            ),

            network=data.get(
                "network"
            ),

            wallet_type=data.get(
                "wallet_type",
                "software",
            ),

            metadata=data.get(
                "metadata",
                {},
            ),
        )


        if data.get(
            "is_locked",
            True,
        ):

            wallet.lock()

        else:

            wallet.unlock()


        return wallet



    ###############################################################################
    # Representation
    ###############################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (

            f"Wallet("
            f"id='{self.wallet_id}', "
            f"network='{self.network}', "
            f"locked={self.is_locked}"
            f")"

        )



    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (

            f"{self.network} wallet "
            f"{self.wallet_id}"

        )
    ###############################################################################
# Module Exports
###############################################################################

__all__ = [
    "Wallet",
]
###############################################################################
# End of wallets.wallet
###############################################################################