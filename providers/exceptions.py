"""
providers/exceptions.py

Universal Blockchain Platform (UBP)

Defines the exception hierarchy used throughout the provider
subsystem.
"""

from __future__ import annotations


class ProviderError(Exception):
    """
    Base exception for all provider-related errors.

    All custom provider exceptions should inherit from this class.
    """

    pass


class ProviderConfigurationError(ProviderError):
    """
    Raised when a provider configuration is invalid or incomplete.
    """

    pass


class ProviderConnectionError(ProviderError):
    """
    Raised when a provider cannot establish or maintain a connection.
    """

    pass


class ProviderAuthenticationError(ProviderError):
    """
    Raised when authentication with a provider fails.
    """

    pass
class ProviderNotFoundError(ProviderError):
    """
    Raised when a requested provider cannot be found.
    """

    pass


class ProviderAlreadyRegisteredError(ProviderError):
    """
    Raised when attempting to register a provider that already exists.
    """

    pass


class ProviderRegistrationError(ProviderError):
    """
    Raised when provider registration fails.
    """

    pass


class ProviderInitializationError(ProviderError):
    """
    Raised when a provider cannot be initialized.
    """

    pass


class ProviderHealthCheckError(ProviderError):
    """
    Raised when a provider health check fails.
    """

    pass


class ProviderTimeoutError(ProviderConnectionError):
    """
    Raised when a provider operation exceeds the configured timeout.
    """

    pass
class ProviderUnavailableError(ProviderError):
    """
    Raised when a provider is currently unavailable.
    """

    pass


class ProviderRequestError(ProviderError):
    """
    Raised when a provider request fails.
    """

    pass


class ProviderResponseError(ProviderError):
    """
    Raised when a provider returns an invalid or unexpected response.
    """

    pass


class ProviderFailoverError(ProviderError):
    """
    Raised when automatic provider failover fails.
    """

    pass


class ProviderRateLimitError(ProviderError):
    """
    Raised when a provider rate limit has been exceeded.
    """

    pass


class ProviderUnsupportedOperationError(ProviderError):
    """
    Raised when a provider does not support the requested operation.
    """

    pass