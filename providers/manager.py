"""
Compatibility layer.

This module exists for backward compatibility.

New code should import ProviderFactory from
providers.factory.
"""

from providers.factory import ProviderFactory


def get_provider():
    """
    Return the configured provider.
    """

    return ProviderFactory.get_provider()