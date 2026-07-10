"""
Ethereum Connection Module.

Obtains the active Web3 connection through the Provider Manager.
"""

from providers.manager import get_provider


def get_connection():
    """
    Return the active Web3 connection.

    Raises:
        ConnectionError: If the active provider cannot establish a connection.
    """

    provider = get_provider()

    if not provider.is_connected():
        raise ConnectionError(
            "Unable to connect to the active blockchain provider."
        )

    return provider.get_web3()