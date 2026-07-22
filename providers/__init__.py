"""
===============================================================================
Universal Blockchain Platform

Module
------
providers.__init__

Public provider interface
===============================================================================
"""


from providers.base import (
    BaseProvider,
    ProviderStatus,
    ProviderType,
)


from providers.factory import (
    ProviderFactory,
)


from providers.exceptions import (
    ProviderError,
    ProviderNotFoundError,
    ProviderUnavailableError,
    ProviderHealthCheckError,
    ProviderConfigurationError,
    ProviderValidationError,
    ProviderUnsupportedOperationError,
    ProviderConnectionError,
    ProviderAuthenticationError,
)


def get_provider(
    name: str | None = None,
    *args,
    **kwargs,
):
    """
    Public provider accessor.
    """

    return ProviderFactory.get_provider(
        name,
        *args,
        **kwargs,
    )



def get_web3(
    name: str | None = None,
):
    """
    Return Web3 instance from provider.

    Used by ethereum services.
    """

    provider = get_provider(
        name
    )

    return provider.web3



__all__ = [

    "BaseProvider",

    "ProviderStatus",

    "ProviderType",

    "ProviderFactory",

    "get_provider",

    "get_web3",

    "ProviderError",

    "ProviderNotFoundError",

    "ProviderUnavailableError",

    "ProviderHealthCheckError",

    "ProviderConfigurationError",

    "ProviderValidationError",

    "ProviderUnsupportedOperationError",

    "ProviderConnectionError",

    "ProviderAuthenticationError",

]