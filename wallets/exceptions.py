"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.exceptions

Purpose
-------
Enterprise wallet exception hierarchy.

This module defines all wallet-related exceptions used throughout the
Universal Blockchain Platform (UBP). A dedicated exception hierarchy
allows wallet-specific failures to be handled independently from provider,
blockchain, or transaction errors.

Architecture
------------
Exception
    │
    └── WalletError
            │
            ├── WalletConfigurationError
            ├── WalletCreationError
            ├── WalletConnectionError
            ├── WalletValidationError
            ├── WalletNotFoundError
            ├── WalletAlreadyExistsError
            ├── WalletLockedError
            ├── WalletAuthenticationError
            ├── WalletPermissionError
            └── ...

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


###############################################################################
# Base Wallet Exception
###############################################################################


class WalletError(Exception):
    """
    Base class for all wallet-related exceptions.
    """

    pass


###############################################################################
# Configuration Exceptions
###############################################################################


class WalletConfigurationError(WalletError):
    """
    Wallet configuration is invalid.
    """

    pass


###############################################################################
# Wallet Lifecycle Exceptions
###############################################################################


class WalletCreationError(WalletError):
    """
    Wallet creation failed.
    """

    pass


class WalletInitializationError(WalletError):
    """
    Wallet initialization failed.
    """

    pass


class WalletAlreadyExistsError(WalletError):
    """
    Wallet already exists.
    """

    pass


class WalletNotFoundError(WalletError):
    """
    Wallet could not be located.
    """

    pass


###############################################################################
# Connectivity Exceptions
###############################################################################


class WalletConnectionError(WalletError):
    """
    Wallet failed to connect.
    """

    pass


class WalletTimeoutError(WalletError):
    """
    Wallet operation timed out.
    """

    pass


class WalletUnavailableError(WalletError):
    """
    Wallet service is unavailable.
    """

    pass

###############################################################################
# Validation Exceptions
###############################################################################


class WalletValidationError(WalletError):
    """
    Wallet validation failed.
    """

    pass


class WalletAddressError(WalletValidationError):
    """
    Wallet address is invalid.
    """

    pass


class WalletPrivateKeyError(WalletValidationError):
    """
    Invalid or unsupported private key.
    """

    pass


class WalletPublicKeyError(WalletValidationError):
    """
    Invalid or unsupported public key.
    """

    pass


###############################################################################
# Authentication & Security Exceptions
###############################################################################


class WalletAuthenticationError(WalletError):
    """
    Wallet authentication failed.
    """

    pass


class WalletPermissionError(WalletError):
    """
    Wallet operation is not permitted.
    """

    pass


class WalletLockedError(WalletError):
    """
    Wallet is locked.
    """

    pass


class WalletEncryptionError(WalletError):
    """
    Wallet encryption failed.
    """

    pass


class WalletDecryptionError(WalletError):
    """
    Wallet decryption failed.
    """

    pass


###############################################################################
# Wallet Operations
###############################################################################


class WalletBalanceError(WalletError):
    """
    Failed to retrieve wallet balance.
    """

    pass


class WalletSigningError(WalletError):
    """
    Transaction signing failed.
    """

    pass


class WalletImportError(WalletError):
    """
    Wallet import failed.
    """

    pass


class WalletExportError(WalletError):
    """
    Wallet export failed.
    """

    pass


class WalletBackupError(WalletError):
    """
    Wallet backup failed.
    """

    pass


class WalletRestoreError(WalletError):
    """
    Wallet restoration failed.
    """

    pass

###############################################################################
# Exception Utilities
###############################################################################


class WalletExceptionContext:
    """
    Provides structured context information for wallet exceptions.

    Used for logging, monitoring, and enterprise audit systems.

    Example:
        context = WalletExceptionContext(
            wallet_id="wallet_001",
            operation="sign_transaction"
        )
    """

    def __init__(
        self,
        wallet_id: str | None = None,
        operation: str | None = None,
        network: str | None = None,
    ):
        self.wallet_id = wallet_id
        self.operation = operation
        self.network = network

    def as_dict(self) -> dict:
        """
        Convert exception context into dictionary format.
        """

        return {
            "wallet_id": self.wallet_id,
            "operation": self.operation,
            "network": self.network,
        }


###############################################################################
# Exception Export Registry
###############################################################################

__all__ = [

    # Base
    "WalletError",

    # Configuration
    "WalletConfigurationError",

    # Lifecycle
    "WalletCreationError",
    "WalletInitializationError",
    "WalletAlreadyExistsError",
    "WalletNotFoundError",

    # Connectivity
    "WalletConnectionError",
    "WalletTimeoutError",
    "WalletUnavailableError",

    # Validation
    "WalletValidationError",
    "WalletAddressError",
    "WalletPrivateKeyError",
    "WalletPublicKeyError",

    # Authentication & Security
    "WalletAuthenticationError",
    "WalletPermissionError",
    "WalletLockedError",
    "WalletEncryptionError",
    "WalletDecryptionError",

    # Operations
    "WalletBalanceError",
    "WalletSigningError",
    "WalletImportError",
    "WalletExportError",
    "WalletBackupError",
    "WalletRestoreError",

    # Utilities
    "WalletExceptionContext",
]
###############################################################################
# End of wallets.exceptions
###############################################################################