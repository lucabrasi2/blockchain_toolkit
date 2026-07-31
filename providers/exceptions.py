"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.exceptions

Purpose
-------
Enterprise provider exception hierarchy.

All provider-related exceptions inherit from ProviderError,
enabling consistent error handling across the platform.

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


class ProviderError(Exception):
    """
    Base exception for all provider-related errors.
    """
    pass


class ProviderConfigurationError(ProviderError):
    """
    Raised when a provider is misconfigured.
    """
    pass


class ProviderConnectionError(ProviderError):
    """
    Raised when a provider cannot be reached.
    """
    pass


class ProviderAuthenticationError(ProviderError):
    """
    Raised when authentication fails.
    """
    pass


class ProviderUnavailableError(ProviderError):
    """
    Raised when a provider is temporarily unavailable.
    """
    pass


class ProviderRateLimitError(ProviderError):
    """
    Raised when rate limits are exceeded.
    """
    pass


class ProviderTimeoutError(ProviderError):
    """
    Raised when a provider request times out.
    """
    pass


class ProviderNotFoundError(ProviderError):
    """
    Raised when a provider is not found in the registry.
    """
    pass


class ProviderHealthCheckError(ProviderError):
    """
    Raised when a provider health check fails.
    """
    pass


class ProviderUnsupportedOperationError(ProviderError):
    """
    Raised when a provider does not support a requested operation.
    """
    pass


class DuplicateRegistrationError(ProviderError):
    """
    Raised when attempting to register a provider that is already registered.
    """
    pass


class ProviderAlreadyRegisteredError(ProviderError):
    """
    Raised when attempting to register a provider that is already registered.
    """
    pass


###############################################################################
# End of File
###############################################################################