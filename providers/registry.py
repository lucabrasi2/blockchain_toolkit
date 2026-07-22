"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.registry

Purpose
-------
Enterprise provider registry.

Maintains a centralized registry of all blockchain
provider implementations available to UBP.

Architecture
------------
UBP Enterprise Connectivity Framework

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Type

from providers.base import BaseProvider
from providers.exceptions import ProviderNotFoundError

from core.logger import get_logger

logger = get_logger(__name__)


###############################################################################
# Provider Registry
###############################################################################


class ProviderRegistry:
    """
    Central registry for all provider implementations.
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
        alias: List[str] | None = None,
    ) -> None:
        """
        Register a provider class.

        Parameters
        ----------
        name : str
            Canonical provider name.

        provider_class : Type[BaseProvider]
            Provider implementation.

        alias : list[str], optional
            Alternative names.
        """

        key = name.lower()

        cls._providers[key] = provider_class

        if alias:

            for item in alias:

                cls._aliases[item.lower()] = key

        logger.info(
            "Registered provider: %s",
            key,
        )
        ###########################################################################
    # Discovery
    ###########################################################################

    @classmethod
    def get(
        cls,
        name: str,
    ) -> Type[BaseProvider]:
        """
        Return a registered provider class.

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
            If the provider is not registered.
        """

        key = name.lower()

        if key in cls._aliases:

            key = cls._aliases[key]

        if key not in cls._providers:

            raise ProviderNotFoundError(
                f"Unknown provider: {name}"
            )

        return cls._providers[key]



    @classmethod
    def exists(
        cls,
        name: str,
    ) -> bool:
        """
        Determine whether a provider exists.
        """

        key = name.lower()

        if key in cls._aliases:

            key = cls._aliases[key]

        return key in cls._providers


    ###########################################################################
    # Listing
    ###########################################################################

    @classmethod
    def providers(
        cls,
    ) -> List[str]:
        """
        Return registered provider names.
        """

        return sorted(
            cls._providers.keys()
        )

    @classmethod
    def all(
        cls,
    ) -> Dict[str, Type[BaseProvider]]:
        """
        Return all registered providers.

        Returns
        -------
        Dict[str, Type[BaseProvider]]
            Mapping of provider names to their
            implementation classes.
        """

        return dict(
            cls._providers
        )



    @classmethod
    def aliases(
        cls,
    ) -> Dict[str, str]:
        """
        Return registered aliases.
        """

        return dict(
            cls._aliases
        )
        ###########################################################################
    # Removal
    ###########################################################################

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> None:
        """
        Remove a provider from the registry.

        Parameters
        ----------
        name : str
            Provider name.
        """

        key = name.lower()

        if key not in cls._providers:

            raise ProviderNotFoundError(
                f"Provider not registered: {name}"
            )

        #
        # Remove aliases pointing to this provider.
        #

        aliases_to_remove = [

            alias

            for alias, provider in cls._aliases.items()

            if provider == key

        ]


        for alias in aliases_to_remove:

            del cls._aliases[alias]


        del cls._providers[key]


        logger.info(
            "Unregistered provider: %s",
            key,
        )


    ###########################################################################
    # Registry Information
    ###########################################################################

    @classmethod
    def count(
        cls,
    ) -> int:
        """
        Return the number of registered providers.
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

        Mainly intended for testing.
        """

        cls._providers.clear()

        cls._aliases.clear()

        logger.info(
            "Provider registry cleared."
        )


    @classmethod
    def info(
        cls,
    ) -> dict:
        """
        Return registry information.
        """

        return {

            
    "providers":
        cls.providers(),

    "aliases":
        cls.aliases(),

    "count":
        cls.count(),

    "registered":
        list(
            cls.all().keys()
        ),

}
###############################################################################
# End of File
###############################################################################