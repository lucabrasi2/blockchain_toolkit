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

from typing import Dict, List, Optional, Type

from providers.base import BaseProvider
from providers.exceptions import ProviderNotFoundError
from core.logger import get_logger

logger = get_logger(__name__)


class ProviderRegistry:
    """
    Enterprise provider registry.
    """

    _providers: Dict[str, Type[BaseProvider]] = {}
    _aliases: Dict[str, str] = {}

    ###########################################################################
    # Registration
    ###########################################################################

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
        alias: Optional[List[str]] = None,
    ) -> None:
        """
        Register a provider class.

        Parameters
        ----------
        name : str
            Provider name.
        provider_class : Type[BaseProvider]
            Provider class.
        alias : Optional[List[str]]
            Alternative names for the provider.

        Raises
        ------
        DuplicateRegistrationError
            If the provider is already registered.
        """
        from providers.exceptions import DuplicateRegistrationError

        name_lower = name.lower()

        if name_lower in cls._providers:
            raise DuplicateRegistrationError(
                f"Provider '{name}' is already registered."
            )

        cls._providers[name_lower] = provider_class

        if alias:
            for a in alias:
                cls._aliases[a.lower()] = name_lower

        logger.info(f"Registered provider: {name}")

    @classmethod
    def get(cls, name: str) -> Type[BaseProvider]:
        """
        Get a provider class by name.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        Type[BaseProvider]
            Provider class.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        key = name.lower()

        # Check if it's an alias
        if key in cls._aliases:
            key = cls._aliases[key]

        if key not in cls._providers:
            available = cls.list_providers()
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. "
                f"Available: {available}"
            )

        return cls._providers[key]

    @classmethod
    def contains(cls, name: str) -> bool:
        """
        Check if a provider is registered.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        bool
            True if registered.
        """
        key = name.lower()

        if key in cls._aliases:
            key = cls._aliases[key]

        return key in cls._providers

    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered providers.

        Returns
        -------
        List[str]
            List of provider names.
        """
        return sorted(cls._providers.keys())

    @classmethod
    def list_aliases(cls) -> Dict[str, str]:
        """
        List all provider aliases.

        Returns
        -------
        Dict[str, str]
            Mapping of alias to provider name.
        """
        return cls._aliases.copy()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a provider is registered.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        bool
            True if registered.
        """
        key = name.lower()
        return key in cls._providers or key in cls._aliases

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a provider.

        Parameters
        ----------
        name : str
            Provider name.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        key = name.lower()

        if key in cls._aliases:
            key = cls._aliases[key]

        if key not in cls._providers:
            raise ProviderNotFoundError(f"Provider '{name}' not found.")

        del cls._providers[key]

        # Remove any aliases pointing to this provider
        to_remove = [k for k, v in cls._aliases.items() if v == key]
        for alias in to_remove:
            del cls._aliases[alias]

        logger.info(f"Unregistered provider: {name}")

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers."""
        cls._providers.clear()
        cls._aliases.clear()
        logger.info("Provider registry cleared.")

    @property
    def count(self) -> int:
        """Return the number of registered providers."""
        return len(self._providers)

    def __iter__(self):
        """Iterate over registered providers."""
        return iter(self._providers.items())

    def __len__(self) -> int:
        return self.count


###############################################################################
# End of File
###############################################################################