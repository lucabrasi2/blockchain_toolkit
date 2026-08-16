"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_provider

Purpose
-------
Provider connectivity smoke test.

Tests the current UBP ProviderFactory and
BaseProvider Enterprise API.
"""
import os

import pytest
from providers.factory import ProviderFactory


def test_default_provider():
    """
    Verify that the default provider can be
    constructed through the current factory API.
    """

    factory = ProviderFactory()

    provider = factory.get_provider()

    assert provider is not None
    assert provider.name
    assert provider.blockchain
    assert provider.network


def test_provider_connection():
    """
    Verify provider connectivity and Web3 access.

    Requires a configured Alchemy API key.
    """

    api_key = os.getenv("ALCHEMY_API_KEY")

    if not api_key:
        pytest.skip(
            "ALCHEMY_API_KEY is not configured."
        )

    factory = ProviderFactory()

    provider = factory.get_provider(
        "alchemy",
        api_key=api_key,
        network="mainnet",
    )

    web3 = provider.web3

    assert web3 is not None
    assert web3.is_connected()

    assert isinstance(
        web3.eth.chain_id,
        int,
    )

    assert isinstance(
        web3.eth.block_number,
        int,
    )