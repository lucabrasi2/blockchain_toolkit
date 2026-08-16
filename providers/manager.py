"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.manager

Purpose
-------
Enterprise provider manager responsible for the complete lifecycle
of blockchain providers.

Responsibilities
----------------
• Provider registration
• Provider creation
• Provider activation
• Default provider management
• Backup provider management
• Automatic failover
• Connection management
• Health monitoring
• Runtime statistics
• Graceful shutdown

Architecture
------------
UBP Enterprise Connectivity Framework

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

from datetime import datetime

from core.logger import get_logger

from providers.base import BaseProvider
from providers.config import ProviderConfig
from providers.factory import ProviderFactory
from providers.registry import ProviderRegistry

from providers.exceptions import (
    ProviderAlreadyRegisteredError,
    ProviderError,
    ProviderNotFoundError,
)

logger = get_logger(__name__)


class ProviderManager:
    """
    Enterprise provider manager.

    Coordinates the lifecycle of blockchain providers
    used throughout the Universal Blockchain Platform.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        factory: ProviderFactory | None = None,
        registry: ProviderRegistry | None = None,
    ) -> None:
        """
        Initialize the provider manager.

        Parameters
        ----------
        factory : ProviderFactory | None
            Provider factory.

        registry : ProviderRegistry | None
            Provider registry.
        """

        self._registry = (
            registry
            if registry is not None
            else ProviderRegistry()
        )

        self._factory = (
            factory
            if factory is not None
            else ProviderFactory(self._registry)
        )

        self._providers: dict[str, BaseProvider] = {}

        self._default_provider: str | None = None

        self._active_provider: str | None = None

        self._backup_provider: str | None = None

        self._failover_enabled = False

        #
        # Leave utcnow() unchanged for consistency
        # with the current provider framework.
        #
        self._created_at = datetime.utcnow()

        self._statistics = {
            "providers_registered": 0,
            "providers_removed": 0,
            "connections": 0,
            "disconnections": 0,
            "failovers": 0,
            "health_checks": 0,
        }

        logger.info(
            "ProviderManager initialized."
        )

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def registry(self) -> ProviderRegistry:
        """
        Return the provider registry.
        """
        return self._registry

    @property
    def factory(self) -> ProviderFactory:
        """
        Return the provider factory.
        """
        return self._factory

    @property
    def providers(self) -> dict[str, BaseProvider]:
        """
        Return managed providers.
        """
        return self._providers

    @property
    def provider_names(self) -> list[str]:
        """
        Return provider names.
        """
        return sorted(self._providers.keys())

    @property
    def count(self) -> int:
        """
        Return the number of managed providers.
        """
        return len(self._providers)

    @property
    def active_provider_name(self) -> str | None:
        """
        Return the active provider name.
        """
        return self._active_provider

    @property
    def backup_provider_name(self) -> str | None:
        """
        Return the backup provider name.
        """
        return self._backup_provider

    @property
    def default_provider_name(self) -> str | None:
        """
        Return the default provider name.
        """
        return self._default_provider

    @property
    def failover_enabled(self) -> bool:
        """
        Return whether automatic failover is enabled.
        """
        return self._failover_enabled

    ###########################################################################
    # Provider Registration
    ###########################################################################

    def register_provider(
        self,
        name: str,
        provider: BaseProvider,
        *,
        default: bool = False,
        backup: bool = False,
    ) -> None:
        """
        Register an already-created provider instance.
        """

        name = name.strip().lower()

        if name in self._providers:

            raise ProviderAlreadyRegisteredError(
                f"Provider '{name}' is already registered."
            )

        self._providers[name] = provider

        self._statistics["providers_registered"] += 1

        if default or self._default_provider is None:
            self._default_provider = name

        if self._active_provider is None:
            self._active_provider = name

        if backup:
            self._backup_provider = name

        logger.info(
            "Registered provider '%s'.",
            name,
        )

    ###########################################################################
    # Provider Creation
    ###########################################################################

    def create_provider(
        self,
        config: ProviderConfig,
        *,
        default: bool = False,
        backup: bool = False,
    ) -> BaseProvider:
        """
        Create and register a provider.

        Parameters
        ----------
        config : ProviderConfig
            Provider configuration.

        Returns
        -------
        BaseProvider
            Newly created provider.
        """

        provider = self._factory.create(config)

        self.register_provider(
            config.provider,
            provider,
            default=default,
            backup=backup,
        )

        return provider

    ###########################################################################
    # Lookup
    ###########################################################################

    def has_provider(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a provider is managed.
        """

        return name.lower() in self._providers

    def get_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Retrieve a managed provider.
        """

        try:
            return self._providers[name.lower()]

        except KeyError as exc:

            raise ProviderNotFoundError(
                f"Provider '{name}' not found."
            ) from exc

    def get_active_provider(
        self,
    ) -> BaseProvider:
        """
        Return the active provider.
        """

        if self._active_provider is None:

            raise ProviderError(
                "No active provider configured."
            )

        return self.get_provider(
            self._active_provider,
        )

    def get_backup_provider(
        self,
    ) -> BaseProvider | None:
        """
        Return the backup provider.
        """

        if self._backup_provider is None:
            return None

        return self.get_provider(
            self._backup_provider,
        )
        ###########################################################################
    # Provider Activation
    ###########################################################################

    def set_active_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Set the active provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        BaseProvider
            Active provider.
        """

        provider = self.get_provider(name)

        self._active_provider = name.lower()

        logger.info(
            "Active provider set to '%s'.",
            self._active_provider,
        )

        return provider

    def set_default_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Set the default provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        BaseProvider
            Default provider.
        """

        provider = self.get_provider(name)

        self._default_provider = name.lower()

        logger.info(
            "Default provider set to '%s'.",
            self._default_provider,
        )

        return provider

    def set_backup_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Set the backup provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        BaseProvider
            Backup provider.
        """

        provider = self.get_provider(name)

        self._backup_provider = name.lower()

        logger.info(
            "Backup provider set to '%s'.",
            self._backup_provider,
        )

        return provider

    def switch_provider(
        self,
        name: str,
    ) -> BaseProvider:
        """
        Switch to another registered provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        BaseProvider
            Newly active provider.
        """

        provider = self.set_active_provider(name)

        logger.info(
            "Provider switched to '%s'.",
            name.lower(),
        )

        return provider

    ###########################################################################
    # Provider Removal
    ###########################################################################

    def unregister_provider(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider from management.

        Parameters
        ----------
        name : str
            Provider name.
        """

        name = name.strip().lower()

        provider = self.get_provider(name)

        if provider.connected:
            provider.disconnect()

        del self._providers[name]

        self._statistics["providers_removed"] += 1

        if self._active_provider == name:
            self._active_provider = None

        if self._default_provider == name:
            self._default_provider = None

        if self._backup_provider == name:
            self._backup_provider = None

        logger.info(
            "Provider '%s' removed.",
            name,
        )

    ###########################################################################
    # Failover
    ###########################################################################

    def enable_failover(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Enable or disable automatic provider failover.

        Parameters
        ----------
        enabled : bool
            Enable automatic failover.
        """

        self._failover_enabled = enabled

        logger.info(
            "Automatic failover %s.",
            "enabled" if enabled else "disabled",
        )

    def disable_failover(
        self,
    ) -> None:
        """
        Disable automatic provider failover.
        """

        self.enable_failover(False)

    def perform_failover(
        self,
    ) -> BaseProvider | None:
        """
        Switch to the configured backup provider.

        Returns
        -------
        BaseProvider | None
            Backup provider if failover succeeds,
            otherwise None.
        """

        if not self._failover_enabled:
            return None

        if self._backup_provider is None:
            return None

        backup = self.get_backup_provider()

        if backup is None:
            return None

        self._active_provider = self._backup_provider

        self._statistics["failovers"] += 1

        logger.warning(
            "Automatic failover activated. "
            "Current provider: %s",
            self._active_provider,
        )

        return backup

       ###########################################################################
    # Health Monitoring
    ###########################################################################

    def health_check(
        self,
        name: str,
    ) -> bool:
        """
        Execute a health check for a managed provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        bool
            True if the provider is healthy.
        """

        provider = self.get_provider(name)

        self._statistics["health_checks"] += 1

        healthy = provider.health_check()

        if (
            not healthy
            and self._failover_enabled
            and self._active_provider == name.lower()
        ):
            self.perform_failover()

        return healthy

    def health_check_all(
        self,
    ) -> dict[str, bool]:
        """
        Execute health checks for all managed providers.

        Returns
        -------
        dict[str, bool]
            Health status for every provider.
        """

        results: dict[str, bool] = {}

        for name in self.provider_names:
            results[name] = self.health_check(name)

        return results

    ###########################################################################
    # Connection Management
    ###########################################################################

    def connect(
        self,
        name: str,
    ) -> None:
        """
        Connect a managed provider.

        Parameters
        ----------
        name : str
            Provider name.
        """

        provider = self.get_provider(name)

        if provider.connected:
            return

        provider.connect()

        self._statistics["connections"] += 1

    def disconnect(
        self,
        name: str,
    ) -> None:
        """
        Disconnect a managed provider.

        Parameters
        ----------
        name : str
            Provider name.
        """

        provider = self.get_provider(name)

        if not provider.connected:
            return

        provider.disconnect()

        self._statistics["disconnections"] += 1

    def connect_all(
        self,
    ) -> None:
        """
        Connect every registered provider.
        """

        for name in self.provider_names:
            self.connect(name)

    def disconnect_all(
        self,
    ) -> None:
        """
        Disconnect every registered provider.
        """

        for name in self.provider_names:
            self.disconnect(name)

    ###########################################################################
    # Shutdown
    ###########################################################################

    def close(
        self,
        name: str,
    ) -> None:
        """
        Close a managed provider.

        Alias for disconnect().
        """

        self.disconnect(name)

    def close_all(
        self,
    ) -> None:
        """
        Gracefully disconnect every registered provider.
        """

        logger.info(
            "Closing all providers."
        )

        for name in list(self.provider_names):

            try:
                self.disconnect(name)

            except Exception:

                logger.exception(
                    "Failed to close provider '%s'.",
                    name,
                )

        logger.info(
            "All providers closed."
        )

    ###########################################################################
    # Runtime Statistics
    ###########################################################################

    def provider_statistics(
        self,
    ) -> dict[str, object]:
        """
        Return provider manager statistics.

        Returns
        -------
        dict[str, object]
            Provider manager statistics.
        """

        return {
            "created_at": self._created_at.isoformat(),
            "registered_providers": self.count,
            "active_provider": self._active_provider,
            "default_provider": self._default_provider,
            "backup_provider": self._backup_provider,
            "failover_enabled": self._failover_enabled,
            "statistics": dict(self._statistics),
        }

    ###########################################################################
    # Utilities
    ###########################################################################

    def list_providers(
        self,
    ) -> list[str]:
        """
        Return registered provider names.

        Returns
        -------
        list[str]
            Registered provider names.
        """

        return self.provider_names

    def clear(
        self,
    ) -> None:
        """
        Remove every managed provider.
        """

        self.close_all()

        self._providers.clear()

        self._active_provider = None
        self._default_provider = None
        self._backup_provider = None

        logger.info(
            "Provider manager cleared."
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Serialize the provider manager.

        Returns
        -------
        dict[str, object]
            Serialized manager.
        """

        return {
            "providers": self.provider_names,
            "active_provider": self._active_provider,
            "default_provider": self._default_provider,
            "backup_provider": self._backup_provider,
            "failover_enabled": self._failover_enabled,
            "statistics": self.provider_statistics(),
        }

    ###########################################################################
    # Magic Methods
    ###########################################################################

    def __len__(
        self,
    ) -> int:
        """
        Return the number of managed providers.
        """

        return self.count

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Support the 'in' operator.
        """

        return self.has_provider(name)

    def __iter__(
        self,
    ):
        """
        Iterate over managed providers.
        """

        return iter(self._providers.items())

    def __enter__(
        self,
    ) -> "ProviderManager":
        """
        Enter context manager.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """
        Exit context manager.
        """

        self.close_all()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"providers={self.count}, "
            f"active={self._active_provider!r}, "
            f"default={self._default_provider!r}, "
            f"backup={self._backup_provider!r}, "
            f"failover={self._failover_enabled})"
        )
        