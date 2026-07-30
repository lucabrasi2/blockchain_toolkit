"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.factory

Purpose
-------
Enterprise provider factory.

The factory is responsible for:

    • Registering provider implementations
    • Creating provider instances
    • Listing available providers

It intentionally contains no provider implementations.
===============================================================================
"""

from __future__ import annotations

from typing import Dict
from typing import Type

from core.logger import get_logger

from providers.base import BaseProvider

from providers.exceptions import (
    ProviderConfigurationError,
    ProviderNotFoundError,
)

logger = get_logger(__name__)


###############################################################################
# Provider Factory
###############################################################################


class ProviderFactory:
    """
    Enterprise provider registry.
    """

    _providers: Dict[
        str,
        Type[BaseProvider],
    ] = {}

    ###########################################################################
    # Registration
    ###########################################################################

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
    ) -> None:
        """
        Register a provider implementation.
        """

        if not name:

            raise ProviderConfigurationError(
                "Provider name required."
            )

        cls._providers[
            name.lower()
        ] = provider_class

        logger.info(
            "Registered provider '%s'.",
            name.lower(),
        )

    register_provider = register
        ###########################################################################
    # Provider Creation
    ###########################################################################

    @classmethod
    def create(
        cls,
        name: str,
        *args,
        **kwargs,
    ) -> BaseProvider:
        """
        Create a provider instance.

        Parameters
        ----------
        name : str
            Registered provider name.

        Returns
        -------
        BaseProvider
            Provider instance.
        """

        provider_name = name.lower()

        if provider_name not in cls._providers:

            raise ProviderNotFoundError(
                f"Provider '{name}' is not registered."
            )

        provider_class = cls._providers[
            provider_name
        ]

        logger.info(
            "Creating provider '%s'.",
            provider_name,
        )

        return provider_class(
            *args,
            **kwargs,
        )

    @classmethod
    def get_provider(
        cls,
        name: str,
        *args,
        **kwargs,
    ) -> BaseProvider:
        """
        Alias for create().
        """

        return cls.create(
            name,
            *args,
            **kwargs,
        )

    ###########################################################################
    # Registry Information
    ###########################################################################

    @classmethod
    def supported_providers(
        cls,
    ) -> list[str]:
        """
        Return registered provider names.
        """

        return sorted(
            cls._providers.keys()
        )

    available_providers = supported_providers

    @classmethod
    def provider_count(
        cls,
    ) -> int:
        """
        Number of registered providers.
        """

        return len(
            cls._providers
        )

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Remove all registered providers.
        """

        cls._providers.clear()

        logger.info(
            "Provider registry cleared."
        )

    @classmethod
    def info(
        cls,
    ) -> dict[str, object]:
        """
        Return provider registry information.
        """

        return {
            "provider_count": cls.provider_count(),
            "providers": cls.supported_providers(),
        }
    ###############################################################################
# Provider Registration
###############################################################################

from providers.alchemy import AlchemyProvider
from providers.infura import InfuraProvider


ProviderFactory.register(
    "alchemy",
    AlchemyProvider,
)

ProviderFactory.register(
    "infura",
    InfuraProvider,
)


###############################################################################
# Public Exports
###############################################################################

__all__ = [
    "ProviderFactory",
]