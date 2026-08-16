"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.registry

Purpose
-------
Enterprise provider registry.

The registry maintains a catalog of all available
provider implementations and their metadata.

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

from __future__ import annotations

from typing import Type

from core.logger import get_logger

from providers.base import BaseProvider
from providers.exceptions import (
    DuplicateRegistrationError,
    ProviderNotFoundError,
)

logger = get_logger(__name__)


class ProviderRegistry:
    """
    Enterprise provider registry.

    Maintains a catalog of provider implementations and
    their aliases.
    """

    _providers: dict[str, Type[BaseProvider]] = {}
    _aliases: dict[str, str] = {}

    ###########################################################################
    # Registration
    ###########################################################################

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
        alias: list[str] | None = None,
    ) -> None:
        """
        Register a provider class.

        Parameters
        ----------
        name : str
            Provider name.

        provider_class : Type[BaseProvider]
            Provider implementation.

        alias : list[str] | None
            Optional provider aliases.

        Raises
        ------
        DuplicateRegistrationError
            If the provider is already registered.
        """

        name_lower = name.strip().lower()

        if name_lower in cls._providers:

            raise DuplicateRegistrationError(
                f"Provider '{name}' is already registered."
            )

        cls._providers[name_lower] = provider_class

        if alias:

            for item in alias:
                cls._aliases[item.strip().lower()] = name_lower

        logger.info(
            "Registered provider '%s'.",
            name_lower,
        )

    ###########################################################################
    # Lookup
    ###########################################################################

    @classmethod
    def get(
        cls,
        name: str,
    ) -> Type[BaseProvider]:
        """
        Retrieve a registered provider class.

        Parameters
        ----------
        name : str
            Provider name or alias.

        Returns
        -------
        Type[BaseProvider]
            Registered provider class.

        Raises
        ------
        ProviderNotFoundError
            If the provider cannot be found.
        """

        key = name.strip().lower()

        if key in cls._aliases:
            key = cls._aliases[key]

        if key not in cls._providers:

            raise ProviderNotFoundError(
                f"Provider '{name}' not found. "
                f"Available: {cls.list_providers()}"
            )

        return cls._providers[key]

    @classmethod
    def contains(
        cls,
        name: str,
    ) -> bool:
        """
        Determine whether a provider is registered.

        Parameters
        ----------
        name : str
            Provider name or alias.

        Returns
        -------
        bool
            True if the provider exists.
        """

        key = name.strip().lower()

        if key in cls._aliases:
            key = cls._aliases[key]

        return key in cls._providers
        ###########################################################################
    # Listing
    ###########################################################################

    @classmethod
    def list_providers(
        cls,
    ) -> list[str]:
        """
        Return registered provider names.

        Returns
        -------
        list[str]
            Registered provider names.
        """

        return sorted(cls._providers.keys())

    @classmethod
    def list_aliases(
        cls,
    ) -> dict[str, str]:
        """
        Return registered provider aliases.

        Returns
        -------
        dict[str, str]
            Mapping of alias to provider name.
        """

        return cls._aliases.copy()

    @classmethod
    def is_registered(
        cls,
        name: str,
    ) -> bool:
        """
        Determine whether a provider is registered.

        Parameters
        ----------
        name : str
            Provider name or alias.

        Returns
        -------
        bool
            True if the provider exists.
        """

        key = name.strip().lower()

        return (
            key in cls._providers
            or key in cls._aliases
        )

    ###########################################################################
    # Unregistration
    ###########################################################################

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> None:
        """
        Unregister a provider.

        Parameters
        ----------
        name : str
            Provider name or alias.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not registered.
        """

        key = name.strip().lower()

        if key in cls._aliases:
            key = cls._aliases[key]

        if key not in cls._providers:

            raise ProviderNotFoundError(
                f"Provider '{name}' not found."
            )

        del cls._providers[key]

        #
        # Remove aliases that reference this provider.
        #
        aliases_to_remove = [
            alias
            for alias, provider in cls._aliases.items()
            if provider == key
        ]

        for alias in aliases_to_remove:
            del cls._aliases[alias]

        logger.info(
            "Unregistered provider '%s'.",
            key,
        )

    ###########################################################################
    # Registry Management
    ###########################################################################

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Remove every registered provider.
        """

        cls._providers.clear()
        cls._aliases.clear()

        logger.info(
            "Provider registry cleared."
        )

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def count(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return len(type(self)._providers)

    ###########################################################################
    # Magic Methods
    ###########################################################################

    def __iter__(
        self,
    ):
        """
        Iterate over registered providers.
        """

        return iter(
            type(self)._providers.items()
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return self.count


###############################################################################
# End of File
###############################################################################