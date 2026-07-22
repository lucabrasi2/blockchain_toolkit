"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.manager

Purpose
-------
Enterprise provider manager.

The manager orchestrates multiple providers,
handling health checks, failover, and load balancing.

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

import random
from typing import Dict, List, Optional, Any, Tuple

from providers.base import BaseProvider
from providers.exceptions import ProviderUnavailableError, ProviderNotFoundError
from providers.factory import ProviderFactory
from core.logger import get_logger

logger = get_logger(__name__)


class ProviderManager:
    """
    Enterprise provider manager.

    The manager orchestrates multiple providers,
    handling health checks, failover, and load balancing.

    Features
    --------
    • Provider registration and lifecycle management
    • Automatic health checking
    • Intelligent failover
    • Load balancing based on latency
    • Provider status monitoring
    • Graceful degradation

    Usage
    -----
    >>> manager = ProviderManager()
    >>> manager.register_provider("alchemy", alchemy_provider)
    >>> manager.register_provider("infura", infura_provider)
    >>> provider = manager.get_active_provider()
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(self) -> None:
        """
        Initialize the provider manager.
        """
        self._providers: Dict[str, BaseProvider] = {}
        self._active_provider: Optional[str] = None
        self._default_provider: Optional[str] = None
        self._auto_failover: bool = True
        self._health_check_interval: int = 60  # seconds
        self._health_check_enabled: bool = True

        logger.info("ProviderManager initialized.")

    ###########################################################################
    # Provider Management
    ###########################################################################

    def register_provider(
        self,
        name: str,
        provider: BaseProvider,
        default: bool = False,
    ) -> None:
        """
        Register a provider instance.

        Parameters
        ----------
        name : str
            Provider name.
        provider : BaseProvider
            Provider instance.
        default : bool
            Whether this is the default provider.

        Raises
        ------
        ValueError
            If a provider with the same name is already registered.
        """
        if name in self._providers:
            raise ValueError(f"Provider '{name}' already registered.")

        self._providers[name] = provider

        if default or not self._default_provider:
            self._default_provider = name

        if not self._active_provider:
            self._active_provider = name

        logger.info(f"Registered provider: {name}")

    def unregister_provider(self, name: str) -> None:
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
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider not found: {name}")

        # Close the provider first
        try:
            self._providers[name].close()
        except Exception as error:
            logger.warning(f"Error closing provider {name}: {error}")

        del self._providers[name]

        if self._active_provider == name:
            self._active_provider = self._default_provider

        logger.info(f"Unregistered provider: {name}")

    def get_provider(self, name: Optional[str] = None) -> BaseProvider:
        """
        Get a provider instance.

        Parameters
        ----------
        name : Optional[str]
            Provider name. If None, returns the active provider.

        Returns
        -------
        BaseProvider
            Provider instance.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        if name is None:
            name = self._active_provider or self._default_provider

        if name is None:
            raise ProviderNotFoundError("No provider configured.")

        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider not found: {name}")

        return self._providers[name]

    def get_healthiest_provider(self) -> BaseProvider:
        """
        Get the healthiest available provider.

        Returns
        -------
        BaseProvider
            Healthiest provider instance.

        Raises
        ------
        ProviderUnavailableError
            If no healthy provider is available.
        """
        healthy: List[Tuple[str, BaseProvider]] = []

        for name, provider in self._providers.items():
            try:
                if provider.is_available():
                    healthy.append((name, provider))
            except Exception as error:
                logger.debug(f"Provider {name} health check failed: {error}")
                continue

        # If no healthy providers, return the first registered provider
        if not healthy:
            if self._providers:
                first_name = next(iter(self._providers))
                logger.warning(
                    "No healthy providers found. "
                    f"Returning first registered provider: {first_name}"
                )
                return self._providers[first_name]

            raise ProviderUnavailableError("No healthy providers available.")

        # Sort by latency (if available)
        def get_latency(item: Tuple[str, BaseProvider]) -> float:
            _, provider = item
            if hasattr(provider, "statistics"):
                return provider.statistics.average_latency
            return 999999.0

        healthy.sort(key=get_latency)
        return healthy[0][1]

    def get_active_provider(self) -> BaseProvider:
        """
        Get the active provider with automatic failover.

        Returns
        -------
        BaseProvider
            Active provider instance.

        Raises
        ------
        ProviderUnavailableError
            If no provider is available.
        """
        try:
            # Try to get the active provider
            provider = self.get_provider(self._active_provider)

            # If auto-failover is enabled and provider is unhealthy, try failover
            if self._auto_failover and not provider.is_available():
                logger.warning(
                    f"Active provider '{self._active_provider}' is unavailable. "
                    "Attempting failover..."
                )
                return self.get_healthiest_provider()

            return provider

        except ProviderNotFoundError as error:
            # If the active provider is not found, try the default
            try:
                logger.warning(f"{error}. Falling back to default provider.")
                provider = self.get_provider(self._default_provider)
                return provider
            except ProviderNotFoundError:
                # If no default, try any provider
                if self._providers:
                    first_name = next(iter(self._providers))
                    logger.warning(f"Falling back to first provider: {first_name}")
                    return self._providers[first_name]
                raise ProviderUnavailableError("No providers available.")

    def get_available_providers(self) -> List[str]:
        """
        Get list of available (healthy) providers.

        Returns
        -------
        List[str]
            List of healthy provider names.
        """
        available = []

        for name, provider in self._providers.items():
            try:
                if provider.is_available():
                    available.append(name)
            except Exception:
                continue

        return available

    ###########################################################################
    # Provider Operations
    ###########################################################################

    def set_active_provider(self, name: str) -> None:
        """
        Set the active provider.

        Parameters
        ----------
        name : str
            Provider name.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider not found: {name}")

        self._active_provider = name
        logger.info(f"Active provider set to: {name}")

    def set_default_provider(self, name: str) -> None:
        """
        Set the default provider.

        Parameters
        ----------
        name : str
            Provider name.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider not found: {name}")

        self._default_provider = name
        logger.info(f"Default provider set to: {name}")

    def enable_failover(self, enabled: bool = True) -> None:
        """
        Enable or disable automatic failover.

        Parameters
        ----------
        enabled : bool
            Whether to enable failover.
        """
        self._auto_failover = enabled
        logger.info(f"Auto-failover {'enabled' if enabled else 'disabled'}")

    def enable_health_checks(self, enabled: bool = True) -> None:
        """
        Enable or disable automatic health checks.

        Parameters
        ----------
        enabled : bool
            Whether to enable health checks.
        """
        self._health_check_enabled = enabled
        logger.info(f"Health checks {'enabled' if enabled else 'disabled'}")

    def set_failover_order(self, provider_names: List[str]) -> None:
        """
        Set the order in which providers should be tried during failover.

        Parameters
        ----------
        provider_names : List[str]
            List of provider names in order of preference.

        Raises
        ------
        ValueError
            If any provider name is not registered.
        """
        for name in provider_names:
            if name not in self._providers:
                raise ValueError(f"Provider '{name}' not registered.")

        # This sets the order by ensuring the default is the first in the list
        if provider_names:
            self._default_provider = provider_names[0]
            logger.info(f"Failover order set to: {provider_names}")

    ###########################################################################
    # Health Management
    ###########################################################################

    def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health checks on all providers.

        Returns
        -------
        Dict[str, bool]
            Mapping of provider names to health status.
        """
        results: Dict[str, bool] = {}

        for name, provider in self._providers.items():
            try:
                results[name] = provider.health_check()
            except Exception as error:
                logger.debug(f"Health check failed for {name}: {error}")
                results[name] = False

        return results

    def get_provider_statuses(self) -> Dict[str, Any]:
        """
        Get status information for all providers.

        Returns
        -------
        Dict[str, Any]
            Provider status information.
        """
        statuses: Dict[str, Any] = {}

        for name, provider in self._providers.items():
            statuses[name] = {
                "name": provider.name,
                "status": provider.status.value,
                "chain_id": provider.chain_id,
                "latest_block": provider.latest_block,
                "latency": provider.statistics.average_latency,
                "success_rate": provider.success_rate,
                "uptime": provider.uptime_seconds,
            }

        return statuses

    ###########################################################################
    # Provider Information
    ###########################################################################

    def list_providers(self) -> List[str]:
        """
        List all registered providers.

        Returns
        -------
        List[str]
            List of provider names.
        """
        return list(self._providers.keys())

    def get_provider_count(self) -> int:
        """
        Get the number of registered providers.

        Returns
        -------
        int
            Number of providers.
        """
        return len(self._providers)

    def get_provider_info(self, name: str) -> Dict[str, Any]:
        """
        Get information for a specific provider.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        Dict[str, Any]
            Provider information.

        Raises
        ------
        ProviderNotFoundError
            If the provider is not found.
        """
        provider = self.get_provider(name)
        return provider.get_provider_info()

    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configurations for all providers.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Mapping of provider names to their configurations.
        """
        configs: Dict[str, Dict[str, Any]] = {}

        for name, provider in self._providers.items():
            try:
                configs[name] = provider.get_config()
            except Exception as error:
                configs[name] = {"error": str(error)}

        return configs

    ###########################################################################
    # Load Balancing
    ###########################################################################

    def get_next_provider(self, strategy: str = "round_robin") -> BaseProvider:
        """
        Get the next provider based on load balancing strategy.

        Parameters
        ----------
        strategy : str
            Load balancing strategy: 'round_robin', 'least_latency', 'random'

        Returns
        -------
        BaseProvider
            Selected provider instance.

        Raises
        ------
        ValueError
            If the strategy is unknown.
        """
        if not self._providers:
            raise ProviderUnavailableError("No providers available.")

        if strategy == "random":
            import random
            name = random.choice(list(self._providers.keys()))
            return self._providers[name]

        elif strategy == "least_latency":
            return self.get_healthiest_provider()

        elif strategy == "round_robin":
            # Simple round-robin - rotate through providers
            if not hasattr(self, "_round_robin_index"):
                self._round_robin_index = 0

            providers = list(self._providers.keys())
            name = providers[self._round_robin_index % len(providers)]
            self._round_robin_index = (self._round_robin_index + 1) % len(providers)
            return self._providers[name]

        else:
            raise ValueError(f"Unknown load balancing strategy: {strategy}")

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close_all(self) -> None:
        """
        Close all providers and release resources.
        """
        for name, provider in self._providers.items():
            try:
                provider.close()
                logger.info(f"Closed provider: {name}")
            except Exception as error:
                logger.error(f"Error closing provider {name}: {error}")

        self._providers.clear()
        self._active_provider = None
        self._default_provider = None

        logger.info("All providers closed.")

    def __enter__(self) -> "ProviderManager":
        """
        Enter the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the context manager and clean up.
        """
        self.close_all()


###############################################################################
# Convenience Functions
###############################################################################


def get_provider_manager() -> ProviderManager:
    """
    Get the global provider manager instance.

    Returns
    -------
    ProviderManager
        Global provider manager.
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = ProviderManager()
    return _global_manager


# Global singleton
_global_manager: Optional[ProviderManager] = None


###############################################################################
# End of File
###############################################################################