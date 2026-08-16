"""
Universal Blockchain Platform (UBP)

Module:
wallets.wallet

Purpose:
Enterprise wallet entity model.

This module defines the core wallet object used throughout
the Universal Blockchain Platform.

The Wallet entity is custody-agnostic.

Supported custody models:
    • Non-custodial
    • Custodial

The Wallet entity does not implement key management,
encryption, storage, or blockchain-specific signing.

Those responsibilities belong to their respective layers.

Architecture:

    Wallet
      |
      +-- WalletManager
      |
      +-- StorageManager
      |
      +-- ValidatorManager
      |
      +-- EncryptionManager
      |
      +-- CustodyProvider
             |
             +-- NonCustodialProvider
             |
             +-- CustodialProvider

Author:
Jaramogi Diddy

Project:
Universal Blockchain Platform (UBP)

Version:
2.1 Enterprise
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import Optional

from wallets.exceptions import (
    WalletConfigurationError,
    WalletLockedError,
    WalletValidationError,
)

from wallets.custody.base import (
    CustodyProvider,
    CustodyType,
)


###############################################################################
# Wallet Entity
###############################################################################


class Wallet:
    """
    Core UBP wallet representation.

    A wallet represents a blockchain account identity and
    maintains its lifecycle state.

    The wallet is deliberately custody-agnostic.

    It can operate with:

        • NonCustodialProvider
        • CustodialProvider

    The actual custody implementation is delegated to the
    configured CustodyProvider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        wallet_id: str,
        address: str,
        network: str,
        wallet_type: str = "software",
        metadata: Optional[Dict[str, Any]] = None,
        custody_type: str = CustodyType.NON_CUSTODIAL,
        custody_provider: Optional[CustodyProvider] = None,
    ) -> None:
        """
        Initialize a wallet.

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

        custody_type:
            Wallet custody model.

        custody_provider:
            Optional custody provider implementation.
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

        self.wallet_type = self._validate_wallet_type(
            wallet_type
        )

        self.custody_type = self._validate_custody_type(
            custody_type
        )

        self.custody_provider = custody_provider

        self.metadata = (
            metadata.copy()
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

    ###########################################################################
    # Validation Helpers
    ###########################################################################

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

    def _validate_wallet_type(
        self,
        wallet_type: str,
    ) -> str:
        """
        Validate wallet type.
        """

        if not isinstance(
            wallet_type,
            str,
        ):
            raise WalletConfigurationError(
                "Wallet type must be a string"
            )

        if not wallet_type.strip():
            raise WalletConfigurationError(
                "Wallet type cannot be empty"
            )

        return wallet_type.strip().lower()

    def _validate_custody_type(
        self,
        custody_type: str,
    ) -> str:
        """
        Validate custody model.
        """

        if not isinstance(
            custody_type,
            str,
        ):
            raise WalletConfigurationError(
                "Custody type must be a string"
            )

        custody_type = custody_type.strip().lower()

        supported = {
            CustodyType.NON_CUSTODIAL,
            CustodyType.CUSTODIAL,
        }

        if custody_type not in supported:
            raise WalletConfigurationError(
                f"Unsupported custody type: "
                f"{custody_type}"
            )

        return custody_type

    ###########################################################################
    # Custody Provider
    ###########################################################################

    def set_custody_provider(
        self,
        provider: CustodyProvider,
    ) -> None:
        """
        Attach a custody provider to the wallet.

        The provider's custody type must match the wallet's
        configured custody type.
        """

        if not isinstance(
            provider,
            CustodyProvider,
        ):
            raise WalletConfigurationError(
                "Invalid custody provider."
            )

        if (
            provider.custody_type
            != self.custody_type
        ):
            raise WalletConfigurationError(
                "Custody provider type does not "
                "match wallet custody type."
            )

        self.custody_provider = provider

        self.updated_at = datetime.now(
            timezone.utc
        )

    def has_custody_provider(
        self,
    ) -> bool:
        """
        Determine whether a custody provider is attached.
        """

        return (
            self.custody_provider is not None
        )

    ###########################################################################
    # Wallet Security Lifecycle
    ###########################################################################

    def lock(
        self,
    ) -> None:
        """
        Lock the wallet.

        If a custody provider is attached, its lock
        operation is invoked as well.
        """

        if self.custody_provider is not None:

            self.custody_provider.lock(
                self.wallet_id
            )

        self.is_locked = True

        self.updated_at = datetime.now(
            timezone.utc
        )

    def unlock(
        self,
        **credentials: Any,
    ) -> bool:
        """
        Unlock the wallet.

        When a custody provider is attached, credentials
        are delegated to that provider.

        For backward compatibility, a wallet without a
        custody provider can still be unlocked directly.
        """

        if self.custody_provider is not None:

            unlocked = (
                self.custody_provider.unlock(
                    self.wallet_id,
                    **credentials,
                )
            )

            if not unlocked:
                return False

        self.is_locked = False

        self.updated_at = datetime.now(
            timezone.utc
        )

        return True

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

    ###########################################################################
    # Custody Status
    ###########################################################################

    def get_custody_status(
        self,
    ) -> Dict[str, Any]:
        """
        Return custody status information.
        """

        status = {
            "wallet_id": self.wallet_id,
            "custody_type": self.custody_type,
            "locked": self.is_locked,
            "provider_configured": (
                self.custody_provider is not None
            ),
        }

        if self.custody_provider is not None:

            try:

                provider_status = (
                    self.custody_provider
                    .get_status(
                        self.wallet_id
                    )
                )

                status.update(
                    provider_status
                )

            except Exception:
                # The wallet's own state remains authoritative
                # if the provider cannot provide status.
                pass

        return status

    ###########################################################################
    # Metadata Management
    ###########################################################################

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

    ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert wallet object into dictionary form.

        Sensitive cryptographic material is intentionally
        excluded.

        The custody provider object itself is never serialized.
        """

        return {
            "wallet_id": self.wallet_id,
            "address": self.address,
            "network": self.network,
            "wallet_type": self.wallet_type,
            "custody_type": self.custody_type,
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

        The custody provider must be attached separately
        after deserialization.
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
            custody_type=data.get(
                "custody_type",
                CustodyType.NON_CUSTODIAL,
            ),
        )

        if data.get(
            "is_locked",
            True,
        ):
            wallet.lock()

        else:
            wallet.is_locked = False

            wallet.updated_at = (
                datetime.now(
                    timezone.utc
                )
            )

        return wallet

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
            f"Wallet("
            f"id='{self.wallet_id}', "
            f"network='{self.network}', "
            f"custody='{self.custody_type}', "
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
# End of File
###############################################################################