"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.exceptions

Purpose
-------
Provider subsystem exception hierarchy.
===============================================================================
"""

from __future__ import annotations



###############################################################################
# Base
###############################################################################


class ProviderError(Exception):
    """
    Base provider exception.
    """



###############################################################################
# Discovery / Availability
###############################################################################


class ProviderNotFoundError(
    ProviderError
):
    """
    Provider was not found.
    """



class ProviderUnavailableError(
    ProviderError
):
    """
    Provider exists but is unavailable.
    """



class ProviderHealthCheckError(
    ProviderError
):
    """
    Provider health check failed.
    """



###############################################################################
# Configuration / Validation
###############################################################################


class ProviderConfigurationError(
    ProviderError
):
    """
    Invalid provider configuration.
    """



class ProviderValidationError(
    ProviderError
):
    """
    Provider validation failed.
    """



###############################################################################
# Operations
###############################################################################


class ProviderUnsupportedOperationError(
    ProviderError
):
    """
    Operation is not supported by provider.
    """



class ProviderOperationError(
    ProviderError
):
    """
    General provider operation failure.
    """



###############################################################################
# Connection / Network
###############################################################################


class ProviderConnectionError(
    ProviderError
):
    """
    Connection failure.
    """



class ProviderNetworkError(
    ProviderError
):
    """
    Blockchain network communication failure.
    """



class ProviderTimeoutError(
    ProviderError
):
    """
    Provider request timed out.
    """



###############################################################################
# Authentication / Security
###############################################################################


class ProviderAuthenticationError(
    ProviderError
):
    """
    Authentication failed.
    """



class ProviderPermissionError(
    ProviderError
):
    """
    Provider permission denied.
    """



###############################################################################
# Transaction
###############################################################################


class ProviderTransactionError(
    ProviderError
):
    """
    Transaction processing error.
    """



class ProviderTransactionRejectedError(
    ProviderTransactionError
):
    """
    Transaction rejected.
    """



###############################################################################
# Limits
###############################################################################


class ProviderRateLimitError(
    ProviderError
):
    """
    Provider rate limit exceeded.
    """



###############################################################################
# Public API
###############################################################################


__all__ = [

    "ProviderError",

    "ProviderNotFoundError",

    "ProviderUnavailableError",

    "ProviderHealthCheckError",

    "ProviderConfigurationError",

    "ProviderValidationError",

    "ProviderUnsupportedOperationError",

    "ProviderOperationError",

    "ProviderConnectionError",

    "ProviderNetworkError",

    "ProviderTimeoutError",

    "ProviderAuthenticationError",

    "ProviderPermissionError",

    "ProviderTransactionError",

    "ProviderTransactionRejectedError",

    "ProviderRateLimitError",

]