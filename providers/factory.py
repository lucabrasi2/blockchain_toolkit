"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.factory

Purpose
-------
Enterprise factory responsible for constructing blockchain providers.

Responsibilities
----------------
- Provider registration
- Provider creation
- Configuration validation
- Runtime provider instantiation
- Provider discovery
- Factory utilities

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

from typing import Any
from typing import Type

from core.logger import get_logger

from providers.base import BaseProvider
from providers.config import ProviderConfig
from providers.registry import ProviderRegistry

from providers.exceptions import (
    ProviderConfigurationError,
    ProviderNotFoundError,
)

logger = get_logger(__name__)


class ProviderFactory:
    """
    Enterprise Provider Factory.

    Responsible for constructing blockchain provider
    instances from ProviderConfig objects.

    The factory never stores provider instances.
    It only creates them.

    Provider lifecycle management belongs to
    ProviderManager.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
    ) -> None:
        """
        Initialize the provider factory.

        Parameters
        ----------
        registry : ProviderRegistry | None
            Registry instance to use. If omitted,
            a new registry is created.
        """

        self._registry = registry or ProviderRegistry()

        logger.info(
            "ProviderFactory initialized."
        )

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def registry(self) -> ProviderRegistry:
        """
        Return the underlying provider registry.
        """

        return self._registry

    ###########################################################################
    # Registration
    ###########################################################################

    def register(
        self,
        name: str,
        provider_class: Type[BaseProvider],
    ) -> None:
        """
        Register a provider implementation.

        Parameters
        ----------
        name : str
            Provider name.

        provider_class : Type[BaseProvider]
            Provider implementation class.
        """

        self._registry.register(
            name,
            provider_class,
        )

        logger.info(
            "Registered provider '%s'.",
            name,
        )

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider implementation.

        Parameters
        ----------
        name : str
            Provider name.
        """

        self._registry.unregister(name)

        logger.info(
            "Unregistered provider '%s'.",
            name,
        )

    ###########################################################################
    # Configuration
    ###########################################################################

    def build_config(
        self,
        provider: str,
        options: dict[str, Any],
    ) -> ProviderConfig:
        """
        Build a ProviderConfig from a dictionary.

        Parameters
        ----------
        provider : str
            Provider name.

        options : dict[str, Any]
            Provider configuration options.

        Returns
        -------
        ProviderConfig
            Provider configuration object.

        Raises
        ------
        ProviderConfigurationError
            If the configuration is invalid.
        """

        provider = provider.strip().lower()

        #
        # Create a copy so the caller's dictionary
        # is never modified.
        #
        configuration = dict(options)

        configuration.setdefault(
            "network",
            "mainnet",
        )

        configuration["provider"] = provider

        try:
            return ProviderConfig(
                **configuration,
            )

        except TypeError as exc:
            raise ProviderConfigurationError(
                f"Invalid configuration for "
                f"provider '{provider}'. "
                f"Error: {exc}"
            ) from exc

    ###########################################################################
    # Validation
    ###########################################################################

    def validate(
        self,
        config: ProviderConfig,
    ) -> None:
        """
        Validate a provider configuration.

        Parameters
        ----------
        config : ProviderConfig
            Provider configuration.

        Raises
        ------
        ProviderConfigurationError
            If configuration is invalid.

        ProviderNotFoundError
            If the provider is not registered.
        """

        if not config.provider:

            raise ProviderConfigurationError(
                "Provider name is required."
            )

        provider = config.provider.strip().lower()

        if not self._registry.contains(provider):

            raise ProviderNotFoundError(
                f"Provider '{provider}' "
                f"is not registered."
            )
        ###########################################################################
    # Provider Creation
    ###########################################################################

    def create(
        self,
        config: ProviderConfig,
    ) -> BaseProvider:
        """
        Create a provider instance.

        Parameters
        ----------
        config : ProviderConfig
            Provider configuration.

        Returns
        -------
        BaseProvider
            Instantiated provider.
        """

        self.validate(config)

        provider_class = self._registry.get(
            config.provider,
        )

        provider = provider_class(config)

        logger.info(
            "Created provider '%s'.",
            config.provider,
        )

        return provider

    def create_from_dict(
        self,
        provider: str,
        options: dict[str, Any],
    ) -> BaseProvider:
        """
        Create a provider from a configuration dictionary.

        Parameters
        ----------
        provider : str
            Provider name.

        options : dict[str, Any]
            Provider configuration options.

        Returns
        -------
        BaseProvider
            Instantiated provider.
        """

        config = self.build_config(
            provider,
            options,
        )

        return self.create(config)

    def create_by_name(
        self,
        provider: str,
        **kwargs: Any,
    ) -> BaseProvider:
        """
        Create a provider using keyword arguments.

        Example
        -------
        factory.create_by_name(
            "alchemy",
            api_key="...",
            network="mainnet",
        )

        Returns
        -------
        BaseProvider
            Instantiated provider.
        """

        return self.create_from_dict(
            provider,
            kwargs,
        )

    ###########################################################################
    # Public Provider Accessor
    ###########################################################################

    def get_provider(
        self,
        name: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> BaseProvider:
        """
        Get or create a provider.

        Parameters
        ----------
        name : str | None
            Provider name. If omitted,
            the default provider is returned.

        Returns
        -------
        BaseProvider
            Provider instance.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not registered.
        """

        #
        # Return the default provider.
        #
        if name is None:

            providers = self.supported_providers()

            if not providers:

                raise ProviderNotFoundError(
                    "No providers registered."
                )

            name = providers[0]

        #
        # Verify registration.
        #
        if not self.is_supported(name):

            raise ProviderNotFoundError(
                f"Provider '{name}' "
                f"is not registered. "
                f"Available: "
                f"{self.supported_providers()}"
            )

        return self.create_by_name(
            name,
            **kwargs,
        )

    ###########################################################################
    # Discovery
    ###########################################################################

    def supported_providers(
        self,
    ) -> list[str]:
        """
        Return registered provider names.

        Returns
        -------
        list[str]
            Sorted provider names.
        """

        return self._registry.list_providers()

    def is_supported(
        self,
        provider: str,
    ) -> bool:
        """
        Determine whether a provider is registered.

        Parameters
        ----------
        provider : str
            Provider name.

        Returns
        -------
        bool
            True if registered.
        """

        return self._registry.contains(
            provider.strip().lower()
        )

    ###########################################################################
    # Registry Utilities
    ###########################################################################

    def get_provider_class(
        self,
        provider: str,
    ) -> Type[BaseProvider]:
        """
        Retrieve a registered provider class.

        Parameters
        ----------
        provider : str
            Provider name.

        Returns
        -------
        Type[BaseProvider]
            Registered provider class.
        """

        return self._registry.get(
            provider.strip().lower()
        )

    def provider_count(
        self,
    ) -> int:
        """
        Return the number of registered providers.

        Returns
        -------
        int
            Number of registered providers.
        """

        return self._registry.count

    def clear(
        self,
    ) -> None:
        """
        Remove every registered provider.

        Normally used only during testing
        or application shutdown.
        """

        count = self._registry.count

        self._registry.clear()

        logger.info(
            "Cleared %d registered provider(s).",
            count,
        )
        ###########################################################################
    # Serialization
    ###########################################################################

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the factory.

        Returns
        -------
        dict[str, Any]
            Factory serialization.
        """

        providers = self.supported_providers()

        return {
            "provider_count": len(providers),
            "registered_providers": providers,
        }

    ###########################################################################
    # Magic Methods
    ###########################################################################

    def __contains__(
        self,
        provider: str,
    ) -> bool:
        """
        Determine whether a provider is registered.

        Enables:

            "alchemy" in factory

        Parameters
        ----------
        provider : str
            Provider name.

        Returns
        -------
        bool
            True if registered.
        """

        return self.is_supported(provider)

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.

        Returns
        -------
        int
            Number of registered providers.
        """

        return self._registry.count

    def __iter__(
        self,
    ):
        """
        Iterate over registered providers.

        Example
        -------
        >>> for name, provider in factory:
        ...     print(name)
        """

        return iter(self._registry)

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.

        Returns
        -------
        str
            Factory representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"providers={self._registry.count}, "
            f"registered={self.supported_providers()}"
            f")"
        )


###############################################################################
# End of File
###############################################################################