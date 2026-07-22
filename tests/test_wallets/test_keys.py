"""
Tests for wallets.keys module.
"""

import pytest

from wallets.keys import WalletKey

from wallets.exceptions import (
    WalletValidationError,
    WalletPrivateKeyError,
    WalletPublicKeyError,
)


###############################################################################
# Creation Tests
###############################################################################


def test_wallet_key_creation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public123",
        private_key="private123",
    )

    assert key.algorithm == "ECDSA"
    assert key.network == "ethereum"
    assert key.has_public_key is True
    assert key.has_private_key is True



def test_missing_algorithm():

    with pytest.raises(
        WalletValidationError
    ):

        WalletKey(
            algorithm="",
            network="ethereum",
        )



def test_missing_network():

    with pytest.raises(
        WalletValidationError
    ):

        WalletKey(
            algorithm="ECDSA",
            network="",
        )



###############################################################################
# Key Access Tests
###############################################################################


def test_public_key_access():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        public_key="pubkey",
    )

    assert key.public_key == "pubkey"



def test_private_key_requires_authorization():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key="secret",
    )


    with pytest.raises(
        WalletValidationError
    ):

        key.get_private_key()



def test_private_key_authorized_access():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key="secret",
    )

    assert (
        key.get_private_key(
            authorized=True
        )
        == "secret"
    )



###############################################################################
# Security Tests
###############################################################################


def test_clear_private_key():

    key = WalletKey(
        algorithm="ECDSA",
        network="bitcoin",
        private_key="secret",
    )

    key.clear_private_key()

    assert key.has_private_key is False


    with pytest.raises(
        WalletPrivateKeyError
    ):

        key.get_private_key(
            authorized=True
        )



###############################################################################
# Validation Tests
###############################################################################


def test_key_validation_success():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public",
    )

    assert key.validate() is True



def test_missing_public_key_validation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )


    with pytest.raises(
        WalletPublicKeyError
    ):

        key.validate()



###############################################################################
# Metadata Tests
###############################################################################


def test_metadata_management():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )

    key.update_metadata(
        "purpose",
        "wallet signing",
    )

    assert (
        key.get_metadata("purpose")
        == "wallet signing"
    )



###############################################################################
# Import Export Tests
###############################################################################


def test_key_import_export():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
    )


    key.import_keys(
        public_key="public",
        private_key="private",
    )


    assert (
        key.export_public_key()
        == "public"
    )


    assert (
        key.export_private_key(
            authorized=True
        )
        == "private"
    )



###############################################################################
# Serialization Tests
###############################################################################


def test_key_to_dict():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        public_key="public",
        private_key="private",
    )


    data = key.to_dict()


    assert data["algorithm"] == "ECDSA"

    assert data["network"] == "ethereum"

    assert data["public_key"] == "public"

    assert data["has_private_key"] is True

    assert "created_at" in data



###############################################################################
# Representation Tests
###############################################################################


def test_key_representation():

    key = WalletKey(
        algorithm="ECDSA",
        network="ethereum",
        private_key="secret",
    )


    representation = repr(key)


    assert "secret" not in representation

    assert "ECDSA" in representation
