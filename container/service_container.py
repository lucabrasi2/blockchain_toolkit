"""
Service Container

Central dependency container for the Universal Blockchain Platform.
"""

from services.ethereum.wallet_service import WalletService


class ServiceContainer:
    """
    Central dependency container.
    """

    def __init__(self):
        """
        Build shared application services.
        """

        self.wallet_service = WalletService()