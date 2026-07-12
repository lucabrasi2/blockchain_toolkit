"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Custom Exceptions
Author  : William Seme

Defines all custom exceptions used throughout UBP.
"""


class UBPException(Exception):
    """
    Base exception for the Universal Blockchain Platform.
    """

    def __init__(self, message="An unexpected UBP error occurred."):
        super().__init__(message)


class ConfigurationError(UBPException):
    """
    Raised when application configuration is invalid.
    """

    def __init__(self, message="Application configuration error."):
        super().__init__(message)


class BlockchainConnectionError(UBPException):
    """
    Raised when a blockchain connection cannot be established.
    """

    def __init__(self, message="Unable to connect to blockchain provider."):
        super().__init__(message)


class InvalidWalletAddressError(UBPException):
    """
    Raised when a wallet address is invalid.
    """

    def __init__(self, message="Invalid wallet address."):
        super().__init__(message)


class WalletNotFoundError(UBPException):
    """
    Raised when a wallet cannot be found.
    """

    def __init__(self, message="Wallet not found."):
        super().__init__(message)


class TransactionError(UBPException):
    """
    Raised when a transaction cannot be processed.
    """

    def __init__(self, message="Transaction processing failed."):
        super().__init__(message)


class TokenError(UBPException):
    """
    Raised when token information cannot be retrieved.
    """

    def __init__(self, message="Token operation failed."):
        super().__init__(message)