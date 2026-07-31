"""
core/application.py

Universal Blockchain Platform (UBP)

Application container.

Acts as the central object that exposes the major
subsystems of the platform.
"""

from __future__ import annotations

from typing import Optional

from providers.manager import ProviderManager


class Application:
    """
    Main UBP application container.
    """

    def __init__(
        self,
        provider_manager: Optional[ProviderManager] = None,
    ) -> None:
        """
        Initialize the application.
        """

        self._provider_manager = provider_manager

        self._wallet_manager = None
        self._blockchain_manager = None
        self._transaction_manager = None
        self._contract_manager = None
        self._token_manager = None
        self._service_manager = None

        self._running = False

    @property
    def provider_manager(self) -> Optional[ProviderManager]:
        """
        Return the provider manager.
        """

        return self._provider_manager

    @provider_manager.setter
    def provider_manager(
        self,
        manager: ProviderManager,
    ) -> None:
        """
        Set the provider manager.
        """

        self._provider_manager = manager

    @property
    def wallet_manager(self):
        return self._wallet_manager

    @wallet_manager.setter
    def wallet_manager(self, manager) -> None:
        self._wallet_manager = manager

    @property
    def blockchain_manager(self):
        return self._blockchain_manager

    @blockchain_manager.setter
    def blockchain_manager(self, manager) -> None:
        self._blockchain_manager = manager

    @property
    def transaction_manager(self):
        return self._transaction_manager

    @transaction_manager.setter
    def transaction_manager(self, manager) -> None:
        self._transaction_manager = manager

    @property
    def contract_manager(self):
        return self._contract_manager

    @contract_manager.setter
    def contract_manager(self, manager) -> None:
        self._contract_manager = manager

    @property
    def token_manager(self):
        return self._token_manager

    @token_manager.setter
    def token_manager(self, manager) -> None:
        self._token_manager = manager

    @property
    def service_manager(self):
        return self._service_manager

    @service_manager.setter
    def service_manager(self, manager) -> None:
        self._service_manager = manager

    @property
    def running(self) -> bool:
        """
        Return the application state.
        """

        return self._running

    def start(self) -> None:
        """
        Start the application.
        """

        self._running = True

    def stop(self) -> None:
        """
        Stop the application.
        """

        self._running = False

    def run(self) -> None:
        """
        Run the application.
        """

        self.start()

    def shutdown(self) -> None:
        """
        Shutdown the application.
        """

        self.stop()

    def to_dict(self) -> dict:
        """
        Serialize application state.
        """

        return {
            "running": self.running,
            "provider_manager": self.provider_manager is not None,
            "wallet_manager": self.wallet_manager is not None,
            "blockchain_manager": self.blockchain_manager is not None,
            "transaction_manager": self.transaction_manager is not None,
            "contract_manager": self.contract_manager is not None,
            "token_manager": self.token_manager is not None,
            "service_manager": self.service_manager is not None,
        }

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"running={self.running})"
        )
