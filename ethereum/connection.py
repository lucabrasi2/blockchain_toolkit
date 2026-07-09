"""
Ethereum connection module.

Creates a reusable connection to Ethereum using Alchemy.
"""

from web3 import Web3

from config.settings import (
    ALCHEMY_HTTP_URL,
    validate_settings,
)

# Validate configuration before connecting
validate_settings()

# Create the Web3 connection
w3 = Web3(Web3.HTTPProvider(ALCHEMY_HTTP_URL))


def get_connection():
    """
    Return the active Web3 connection.
    """

    if not w3.is_connected():
        raise ConnectionError(
            "Unable to connect to the Ethereum network."
        )

    return w3