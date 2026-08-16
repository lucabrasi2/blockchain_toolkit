"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.test_custody.test_base

Purpose
-------
Tests for the abstract custody provider interface.

These tests verify the custody contract itself without introducing
blockchain-specific behavior.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
"""

from __future__ import annotations

import pytest

from wallets.custody.base import (
    CustodyProvider,
    CustodyType,
)


###############################################################################
# Test Fixtures
###############################################################################


class DummyCustodyProvider(CustodyProvider):
    """
    Minimal concrete implementation used only for testing the
    CustodyProvider abstract interface.
    """

    def __init__(self) -> None:
        self.wallets: dict[str, dict] = {}

    @property
    def custody_type(self) -> str:
        return CustodyType.NON_CUSTODIAL

    def create_wallet(
        self,
        **options,
    ) -> dict:
        wallet_id = options.get(
            "wallet_id",
            "test-wallet",
        )

        record = {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": "LOCKED",
        }

        self.wallets[wallet_id] = record

        return dict(record)

    def import_wallet(
        self,
        **options,
    ) -> dict:
        wallet_id = options.get(
            "wallet_id",
            "imported-wallet",
        )

        record = {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": "LOCKED",
            "imported": True,
        }

        self.wallets[wallet_id] = record

        return dict(record)

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        self.wallets.pop(
            wallet_id,
            None,
        )

    def lock(
        self,
        wallet_id: str,
    ) -> None:
        self.wallets[wallet_id][
            "status"
        ] = "LOCKED"

    def unlock(
        self,
        wallet_id: str,
        **credentials,
    ) -> bool:
        self.wallets[wallet_id][
            "status"
        ] = "UNLOCKED"

        return True

    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        return (
            self.wallets[wallet_id][
                "status"
            ]
            == "UNLOCKED"
        )

    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict,
    ) -> str:
        return "dummy-signed-transaction"

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        return "dummy-public-key"

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        return "dummy-address"

    def get_status(
        self,
        wallet_id: str,
    ) -> dict:
        return {
            "wallet_id": wallet_id,
            "custody_type": self.custody_type,
            "status": self.wallets[
                wallet_id
            ]["status"],
            "unlocked": self.is_unlocked(
                wallet_id
            ),
        }


###############################################################################
# Abstract Interface Tests
###############################################################################


def test_custody_provider_is_abstract() -> None:
    """
    Verify CustodyProvider cannot be instantiated directly.
    """

    with pytest.raises(TypeError):
        CustodyProvider()


def test_custody_type_constants() -> None:
    """
    Verify the supported custody type constants.
    """

    assert (
        CustodyType.NON_CUSTODIAL
        == "non_custodial"
    )

    assert (
        CustodyType.CUSTODIAL
        == "custodial"
    )


###############################################################################
# Concrete Interface Tests
###############################################################################


def test_dummy_provider_implements_interface() -> None:
    """
    Verify a concrete provider can implement the
    CustodyProvider interface.
    """

    provider = DummyCustodyProvider()

    assert isinstance(
        provider,
        CustodyProvider,
    )

    assert (
        provider.custody_type
        == CustodyType.NON_CUSTODIAL
    )


def test_provider_representation() -> None:
    """
    Verify the base provider representation.
    """

    provider = DummyCustodyProvider()

    representation = repr(
        provider
    )

    assert (
        "DummyCustodyProvider"
        in representation
    )

    assert (
        "non_custodial"
        in representation
    )


###############################################################################
# Lifecycle Contract Tests
###############################################################################


def test_create_wallet_contract() -> None:
    """
    Verify wallet creation returns custody metadata.
    """

    provider = DummyCustodyProvider()

    result = provider.create_wallet(
        wallet_id="wallet-001"
    )

    assert result["wallet_id"] == "wallet-001"

    assert (
        result["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )


def test_import_wallet_contract() -> None:
    """
    Verify wallet import returns custody metadata.
    """

    provider = DummyCustodyProvider()

    result = provider.import_wallet(
        wallet_id="wallet-002"
    )

    assert (
        result["wallet_id"]
        == "wallet-002"
    )

    assert (
        result["imported"]
        is True
    )


def test_lock_unlock_contract() -> None:
    """
    Verify lock and unlock operations.
    """

    provider = DummyCustodyProvider()

    provider.create_wallet(
        wallet_id="wallet-003"
    )

    assert (
        provider.is_unlocked(
            "wallet-003"
        )
        is False
    )

    assert (
        provider.unlock(
            "wallet-003",
            password="test",
        )
        is True
    )

    assert (
        provider.is_unlocked(
            "wallet-003"
        )
        is True
    )

    provider.lock(
        "wallet-003"
    )

    assert (
        provider.is_unlocked(
            "wallet-003"
        )
        is False
    )


def test_signing_contract() -> None:
    """
    Verify the signing interface accepts a transaction payload
    and returns a serialized result.
    """

    provider = DummyCustodyProvider()

    provider.create_wallet(
        wallet_id="wallet-004"
    )

    result = provider.sign_transaction(
        "wallet-004",
        {
            "operation": "test",
        },
    )

    assert isinstance(
        result,
        str,
    )

    assert (
        result
        == "dummy-signed-transaction"
    )


def test_public_information_contract() -> None:
    """
    Verify public-key and address interfaces.
    """

    provider = DummyCustodyProvider()

    provider.create_wallet(
        wallet_id="wallet-005"
    )

    public_key = provider.get_public_key(
        "wallet-005"
    )

    address = provider.get_address(
        "wallet-005",
        "testnet",
    )

    assert (
        public_key
        == "dummy-public-key"
    )

    assert (
        address
        == "dummy-address"
    )


def test_status_contract() -> None:
    """
    Verify custody status reporting.
    """

    provider = DummyCustodyProvider()

    provider.create_wallet(
        wallet_id="wallet-006"
    )

    status = provider.get_status(
        "wallet-006"
    )

    assert (
        status["wallet_id"]
        == "wallet-006"
    )

    assert (
        status["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )

    assert (
        status["status"]
        == "LOCKED"
    )

    assert (
        status["unlocked"]
        is False
    )


def test_delete_wallet_contract() -> None:
    """
    Verify wallet deletion through the custody interface.
    """

    provider = DummyCustodyProvider()

    provider.create_wallet(
        wallet_id="wallet-007"
    )

    assert (
        "wallet-007"
        in provider.wallets
    )

    provider.delete_wallet(
        "wallet-007"
    )

    assert (
        "wallet-007"
        not in provider.wallets
    )


###############################################################################
# End of File
###############################################################################
