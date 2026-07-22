"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.models

Purpose
-------
Enterprise wallet domain models.

This module defines the core data models used throughout the UBP wallet
framework. These models provide strongly-typed objects that replace
unstructured dictionaries and establish a common interface for all
supported blockchains.

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

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


###############################################################################
# Wallet Enumerations
###############################################################################


class WalletType(Enum):
    """
    Wallet classification.
    """

    HOT = "hot"
    COLD = "cold"
    HARDWARE = "hardware"
    MULTISIG = "multisig"
    CUSTODIAL = "custodial"
    NON_CUSTODIAL = "non_custodial"


class WalletStatus(Enum):
    """
    Wallet operational status.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    ARCHIVED = "archived"


###############################################################################
# Wallet Information
###############################################################################


@dataclass(slots=True)
class WalletInfo:
    """
    General wallet information.

    This model contains descriptive information about a wallet but
    intentionally excludes balances and transaction history.
    """

    address: str

    blockchain: str

    network: str

    provider: str

    wallet_type: WalletType = WalletType.HOT

    status: WalletStatus = WalletStatus.ACTIVE

    label: str | None = None

    description: str | None = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    tags: list[str] = field(
        default_factory=list
    )


###############################################################################
# Wallet Metadata
###############################################################################


@dataclass(slots=True)
class WalletMetadata:
    """
    Runtime metadata describing the current blockchain connection.
    """

    blockchain: str

    network: str

    provider: str

    chain_id: int

    connected: bool

    latest_block: int | None = None

    client_version: str | None = None

    node_endpoint: str | None = None

    websocket_enabled: bool = False

    synchronization: float | None = None

    extra: dict[str, Any] = field(
        default_factory=dict
    )

    ###############################################################################
# Wallet Balance
###############################################################################


@dataclass(slots=True)
class WalletBalance:
    """
    Wallet balance information.

    Represents the native cryptocurrency balance for a wallet.
    """

    address: str

    blockchain: str

    network: str

    symbol: str

    balance_raw: int

    balance: float

    decimals: int = 18

    block_number: int | None = None

    last_updated: datetime = field(
        default_factory=datetime.utcnow
    )


###############################################################################
# Token Balance
###############################################################################


@dataclass(slots=True)
class TokenBalance:
    """
    Fungible token balance.

    Examples
    --------
    - ERC-20
    - TRC-20
    - BEP-20
    - SPL Tokens
    """

    contract_address: str

    token_name: str

    token_symbol: str

    decimals: int

    balance_raw: int

    balance: float

    owner_address: str

    blockchain: str

    network: str

    verified: bool = False

    logo_url: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


###############################################################################
# Transaction Summary
###############################################################################


@dataclass(slots=True)
class TransactionSummary:
    """
    Lightweight transaction summary.

    Suitable for wallet history, explorers and dashboards.
    """

    transaction_hash: str

    blockchain: str

    network: str

    sender: str

    receiver: str

    value: float

    symbol: str

    block_number: int | None = None

    nonce: int | None = None

    gas_used: int | None = None

    gas_price: int | None = None

    fee: float | None = None

    timestamp: datetime | None = None

    confirmations: int = 0

    successful: bool = True

    pending: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    ###############################################################################
# Signed Transaction
###############################################################################


@dataclass(slots=True)
class SignedTransaction:
    """
    Signed blockchain transaction.

    Represents a transaction that has been signed and is ready
    for broadcasting to the blockchain network.
    """

    transaction_hash: str

    raw_transaction: bytes

    sender: str

    receiver: str | None = None

    nonce: int = 0

    signature: str | None = None

    blockchain: str = ""

    network: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


###############################################################################
# Wallet Statistics
###############################################################################


@dataclass(slots=True)
class WalletStatistics:
    """
    Wallet operational statistics.
    """

    total_transactions: int = 0

    successful_transactions: int = 0

    failed_transactions: int = 0

    pending_transactions: int = 0

    total_received: float = 0.0

    total_sent: float = 0.0

    total_fees_paid: float = 0.0

    last_transaction_at: datetime | None = None

    first_transaction_at: datetime | None = None


###############################################################################
# Wallet Health
###############################################################################


@dataclass(slots=True)
class WalletHealth:
    """
    Wallet operational health.

    Used by monitoring and diagnostics modules.
    """

    address: str

    blockchain: str

    network: str

    provider: str

    connected: bool

    synchronized: bool

    latest_block: int

    latency_ms: float | None = None

    last_checked: datetime = field(
        default_factory=datetime.utcnow
    )

    issues: list[str] = field(
        default_factory=list
    )


###############################################################################
# Module Exports
###############################################################################

__all__ = [

    # Enums
    "WalletType",
    "WalletStatus",

    # Models
    "WalletInfo",
    "WalletMetadata",
    "WalletBalance",
    "TokenBalance",
    "TransactionSummary",
    "SignedTransaction",
    "WalletStatistics",
    "WalletHealth",
]
###############################################################################
# End of File
###############################################################################