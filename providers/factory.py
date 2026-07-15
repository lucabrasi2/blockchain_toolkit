"""
Universal Blockchain Platform (UBP)

Module:
    Provider Factory

Purpose:
    Factory pattern for creating blockchain providers.

Responsibilities:
    • Create provider instances
    • Manage provider types
    • Handle provider configuration

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Optional, Dict, Any

from core.logger import get_logger
from providers.base import BaseProvider
from providers.alchemy import AlchemyProvider


logger = get_logger(__name__)


class ProviderFactory:
    """
    Factory for creating blockchain providers.
    """

    _providers = {
        "alchemy": AlchemyProvider,
        # "infura": InfuraProvider,
        # "quicknode": QuickNodeProvider,
        # "ankr": AnkrProvider,
        # "local": LocalProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_type: str,
        api_key: Optional[str] = None,
        network: str = "mainnet",
        **kwargs
    ) -> BaseProvider:
        """
        Create a provider instance.

        Parameters
        ----------
        provider_type : str
            Type of provider ('alchemy', 'infura', etc.).
        api_key : str, optional
            API key for the provider.
        network : str, optional
            Network to connect to.
        **kwargs
            Additional provider-specific arguments.

        Returns
        -------
        BaseProvider
            Provider instance.

        Raises
        ------
        ValueError
            If the provider type is not supported.
        """
        provider_class = cls._providers.get(provider_type.lower())

        if not provider_class:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        logger.info(f"Creating {provider_type} provider for {network}")

        return provider_class(api_key=api_key, network=network, **kwargs)

    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get list of available provider types.

        Returns
        -------
        list
            List of provider type names.
        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new provider type.

        Parameters
        ----------
        name : str
            Provider name.
        provider_class : type
            Provider class.
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered provider: {name}")