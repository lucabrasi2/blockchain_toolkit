"""
Provider Manager.
"""

from providers.alchemy import AlchemyProvider


_provider = AlchemyProvider()


def get_provider():
    """
    Return the active provider.
    """

    return _provider