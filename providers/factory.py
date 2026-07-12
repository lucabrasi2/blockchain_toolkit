"""
Provider Factory

Creates blockchain providers for the Universal Blockchain Platform.
"""

from providers.alchemy import AlchemyProvider


class ProviderFactory:
    """
    Factory responsible for creating blockchain providers.
    """

    @staticmethod
    def get_provider():
        """
        Return the configured blockchain provider.
        """

        return AlchemyProvider()