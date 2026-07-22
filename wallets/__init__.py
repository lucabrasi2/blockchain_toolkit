"""
===============================================================================
Universal Blockchain Platform (UBP)

Package
-------
wallets

Purpose
-------
Enterprise wallet subsystem.

This package exposes the public wallet interfaces that have been fully
implemented and tested.

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
# Wallet Core
###############################################################################

from wallets.wallet import Wallet

###############################################################################
# Key Management
###############################################################################

from wallets.keys import WalletKey

###############################################################################
# Security
###############################################################################

from wallets.encryption import EncryptionManager

###############################################################################
# Storage
###############################################################################

from wallets.storage import WalletStorage

###############################################################################
# Package Metadata
###############################################################################

__version__ = "2.0 Enterprise"

__author__ = "Jaramogi Diddy"

###############################################################################
# Public Package Interface
###############################################################################

__all__ = [
    "Wallet",
    "WalletKey",
    "EncryptionManager",
    "WalletStorage",
]