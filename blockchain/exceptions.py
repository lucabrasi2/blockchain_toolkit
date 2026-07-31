"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
blockchain.exceptions

Purpose
-------
Defines the exception hierarchy for the Blockchain subsystem.

The Blockchain subsystem uses these exceptions to provide a
consistent error-handling model across all supported blockchain
implementations.

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
===============================================================================
"""

from __future__ import annotations


class BlockchainError(Exception):
    """
    Base exception for all blockchain-related errors.

    Every blockchain exception should inherit from this class.
    """

    pass


# ============================================================================
# Configuration
# ============================================================================

class BlockchainConfigurationError(BlockchainError):
    """
    Raised when blockchain configuration is invalid.
    """

    pass


# ============================================================================
# Registry
# ============================================================================

class BlockchainAlreadyRegisteredError(BlockchainError):
    """
    Raised when attempting to register an already registered blockchain.
    """

    pass


class BlockchainNotFoundError(BlockchainError):
    """
    Raised when a requested blockchain is not registered.
    """

    pass


# ============================================================================
# Connection
# ============================================================================

class BlockchainConnectionError(BlockchainError):
    """
    Raised when a blockchain connection cannot be established.
    """

    pass


class BlockchainDisconnectedError(BlockchainError):
    """
    Raised when an operation requires an active connection but the
    blockchain is disconnected.
    """

    pass


class BlockchainTimeoutError(BlockchainConnectionError):
    """
    Raised when communication with a blockchain exceeds the allowed
    timeout period.
    """

    pass


# ============================================================================
# Network
# ============================================================================

class NetworkNotSupportedError(BlockchainError):
    """
    Raised when the requested network is not supported.
    """

    pass


class ChainIdMismatchError(BlockchainError):
    """
    Raised when the connected blockchain reports an unexpected chain ID.
    """

    pass


# ============================================================================
# Blocks
# ============================================================================

class BlockNotFoundError(BlockchainError):
    """
    Raised when a requested block cannot be found.
    """

    pass


# ============================================================================
# Transactions
# ============================================================================

class TransactionNotFoundError(BlockchainError):
    """
    Raised when a transaction cannot be found.
    """

    pass


class TransactionBroadcastError(BlockchainError):
    """
    Raised when a transaction cannot be broadcast to the network.
    """

    pass


class TransactionReceiptError(BlockchainError):
    """
    Raised when a transaction receipt cannot be retrieved.
    """

    pass


# ============================================================================
# Accounts
# ============================================================================

class AccountNotFoundError(BlockchainError):
    """
    Raised when a blockchain account cannot be found.
    """

    pass


class BalanceRetrievalError(BlockchainError):
    """
    Raised when an account balance cannot be retrieved.
    """

    pass


# ============================================================================
# Smart Contracts
# ============================================================================

class ContractError(BlockchainError):
    """
    Base exception for smart contract operations.
    """

    pass


class ContractDeploymentError(ContractError):
    """
    Raised when deployment of a smart contract fails.
    """

    pass


class ContractExecutionError(ContractError):
    """
    Raised when execution of a smart contract fails.
    """

    pass


# ============================================================================
# Gas
# ============================================================================

class GasEstimationError(BlockchainError):
    """
    Raised when gas estimation fails.
    """

    pass


class GasPriceError(BlockchainError):
    """
    Raised when the current gas price cannot be determined.
    """

    pass


# ============================================================================
# Provider Integration
# ============================================================================

class ProviderUnavailableError(BlockchainError):
    """
    Raised when no blockchain provider is available.
    """

    pass


class ProviderHealthError(BlockchainError):
    """
    Raised when the active provider fails a health check.
    """

    pass