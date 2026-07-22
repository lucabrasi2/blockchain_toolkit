"""
===============================================================================
Universal Blockchain Platform (UBP)

Test Module
-----------
tests.wallets.test_wallet

Purpose
-------
Tests Wallet entity behaviour.

===============================================================================
"""


import pytest


from wallets import Wallet


from wallets.exceptions import (
    WalletConfigurationError,
    WalletValidationError,
    WalletLockedError,
)


###############################################################################
# Wallet Creation Tests
###############################################################################


def test_wallet_creation():

    wallet = Wallet(
        wallet_id="wallet_001",
        address="0x123456789",
        network="ethereum",
    )

    assert wallet.wallet_id == "wallet_001"

    assert wallet.network == "ethereum"

    assert wallet.is_locked is True



def test_wallet_missing_id():

    with pytest.raises(
        WalletConfigurationError
    ):

        Wallet(
            wallet_id="",
            address="0x123",
            network="ethereum",
        )



def test_wallet_missing_address():

    with pytest.raises(
        WalletValidationError
    ):

        Wallet(
            wallet_id="wallet_001",
            address="",
            network="ethereum",
        )


###############################################################################
# Lock / Unlock Tests
###############################################################################


def test_wallet_lock_unlock():

    wallet = Wallet(
        wallet_id="wallet_001",
        address="0x123",
        network="ethereum",
    )


    wallet.unlock()

    assert wallet.is_locked is False


    wallet.lock()

    assert wallet.is_locked is True



def test_locked_wallet_protection():

    wallet = Wallet(
        wallet_id="wallet_001",
        address="0x123",
        network="ethereum",
    )


    with pytest.raises(
        WalletLockedError
    ):

        wallet.require_unlocked()


###############################################################################
# Metadata Tests
###############################################################################


def test_wallet_metadata():

    wallet = Wallet(
        wallet_id="wallet_001",
        address="0x123",
        network="ethereum",
    )


    wallet.update_metadata(
        "owner",
        "UBP",
    )


    assert wallet.get_metadata(
        "owner"
    ) == "UBP"



###############################################################################
# Serialization Tests
###############################################################################


def test_wallet_to_dict():

    wallet = Wallet(
        wallet_id="wallet_001",
        address="0x123",
        network="ethereum",
    )


    data = wallet.to_dict()


    assert data["wallet_id"] == "wallet_001"

    assert data["network"] == "ethereum"
