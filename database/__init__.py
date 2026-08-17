"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
database

Purpose
-------
Database integration for the Universal Blockchain Platform.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from database.database import DatabaseManager, get_db_manager
from database.models import (
    # Existing models
    WalletInspection,
    ContractInspection,
    TransactionHistory,
    NodeHealth,
    CacheEntry,
    # New models
    User,
    Wallet,
    UserTransaction,
)

__all__ = [
    "DatabaseManager",
    "get_db_manager",
    # Existing models
    "WalletInspection",
    "ContractInspection",
    "TransactionHistory",
    "NodeHealth",
    "CacheEntry",
    # New models
    "User",
    "Wallet",
    "UserTransaction",
]


###############################################################################
# End of File
###############################################################################