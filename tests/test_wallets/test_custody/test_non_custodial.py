"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.test_custody.test_non_custodial

Purpose
-------
Tests for the UBP non-custodial custody provider.

These tests verify the custody lifecycle and ensure that
blockchain-specific signing and address derivation remain
outside the custody provider.

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

from wallets.custody.base import CustodyProvider
from wallets.custody.base import CustodyType
from wallets.custody.non_custodial import (
    NonCustodialProvider,
)


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def provider() -> NonCustodialProvider:
    """
    Return a fresh non-custodial provider.
    """

    return NonCustodialProvider()


###############################################################################
# Provider Identity
###############################################################################


def test_provider_is_custody_provider(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify the provider implements CustodyProvider.
    """

    assert isinstance(
        provider,
        CustodyProvider,
    )


def test_provider_custody_type(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify the provider identifies itself as non-custodial.
    """

    assert (
        provider.custody_type
        == CustodyType.NON_CUSTODIAL
    )


###############################################################################
# Wallet Creation
###############################################################################


def test_create_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify non-custodial wallet creation.
    """

    result = provider.create_wallet(
        wallet_id="noncustodial-001"
    )

    assert (
        result["wallet_id"]
        == "noncustodial-001"
    )

    assert (
        result["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )


def test_create_wallet_generates_id(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify a wallet ID can be generated when none is supplied.
    """

    result = provider.create_wallet()

    assert (
        result["wallet_id"]
    )

    assert (
        result["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )


def test_duplicate_wallet_rejected(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify duplicate wallet IDs are rejected.
    """

    provider.create_wallet(
        wallet_id="duplicate-wallet"
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        provider.create_wallet(
            wallet_id="duplicate-wallet"
        )


###############################################################################
# Wallet Import
###############################################################################


def test_import_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify existing wallet import.
    """

    result = provider.import_wallet(
        wallet_id="imported-wallet"
    )

    assert (
        result["wallet_id"]
        == "imported-wallet"
    )

    assert (
        result["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )

    assert (
        result["imported"]
        is True
    )


def test_duplicate_import_rejected(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify duplicate imported wallet IDs are rejected.
    """

    provider.import_wallet(
        wallet_id="imported-duplicate"
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        provider.import_wallet(
            wallet_id="imported-duplicate"
        )


###############################################################################
# Locking
###############################################################################


def test_wallet_starts_locked(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify newly created wallets begin locked.
    """

    provider.create_wallet(
        wallet_id="locked-wallet"
    )

    assert (
        provider.is_unlocked(
            "locked-wallet"
        )
        is False
    )

    status = provider.get_status(
        "locked-wallet"
    )

    assert (
        status["status"]
        == "LOCKED"
    )

    assert (
        status["unlocked"]
        is False
    )


def test_unlock_requires_credentials(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify unlocking requires credentials.
    """

    provider.create_wallet(
        wallet_id="credential-wallet"
    )

    with pytest.raises(
        ValueError,
        match="credentials are required",
    ):
        provider.unlock(
            "credential-wallet"
        )


def test_unlock_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify a wallet can be unlocked.
    """

    provider.create_wallet(
        wallet_id="unlock-wallet"
    )

    result = provider.unlock(
        "unlock-wallet",
        password="test-password",
    )

    assert result is True

    assert (
        provider.is_unlocked(
            "unlock-wallet"
        )
        is True
    )

    status = provider.get_status(
        "unlock-wallet"
    )

    assert (
        status["status"]
        == "UNLOCKED"
    )

    assert (
        status["unlocked"]
        is True
    )


def test_lock_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify a previously unlocked wallet can be locked.
    """

    provider.create_wallet(
        wallet_id="relock-wallet"
    )

    provider.unlock(
        "relock-wallet",
        password="test-password",
    )

    assert (
        provider.is_unlocked(
            "relock-wallet"
        )
        is True
    )

    provider.lock(
        "relock-wallet"
    )

    assert (
        provider.is_unlocked(
            "relock-wallet"
        )
        is False
    )

    status = provider.get_status(
        "relock-wallet"
    )

    assert (
        status["status"]
        == "LOCKED"
    )


###############################################################################
# Signing Boundary
###############################################################################


def test_signing_requires_unlocked_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify signing cannot proceed while the wallet is locked.
    """

    provider.create_wallet(
        wallet_id="sign-locked"
    )

    with pytest.raises(
        PermissionError,
        match="must be unlocked",
    ):
        provider.sign_transaction(
            "sign-locked",
            {
                "operation": "test",
            },
        )


def test_signing_requires_transaction_dictionary(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify transaction input must be a dictionary.

    The wallet is unlocked first so that this test reaches
    transaction validation.
    """

    provider.create_wallet(
        wallet_id="sign-invalid"
    )

    provider.unlock(
        "sign-invalid",
        password="test-password",
    )

    with pytest.raises(
        TypeError,
        match="Transaction must be a dictionary",
    ):
        provider.sign_transaction(
            "sign-invalid",
            "invalid-transaction",
        )


def test_signing_is_delegated_to_blockchain_adapter(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify the non-custodial provider does not fabricate
    blockchain-specific signatures.
    """

    provider.create_wallet(
        wallet_id="sign-adapter"
    )

    provider.unlock(
        "sign-adapter",
        password="test-password",
    )

    with pytest.raises(
        NotImplementedError,
        match="Blockchain-specific signing",
    ):
        provider.sign_transaction(
            "sign-adapter",
            {
                "operation": "test",
            },
        )


###############################################################################
# Public Information Boundary
###############################################################################


def test_public_key_retrieval_is_delegated(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify public-key retrieval remains outside the
    custody provider.
    """

    provider.create_wallet(
        wallet_id="public-key-wallet"
    )

    with pytest.raises(
        NotImplementedError,
        match="Public-key retrieval",
    ):
        provider.get_public_key(
            "public-key-wallet"
        )


def test_address_derivation_is_delegated(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify blockchain-specific address derivation remains
    outside the custody provider.
    """

    provider.create_wallet(
        wallet_id="address-wallet"
    )

    with pytest.raises(
        NotImplementedError,
        match="Blockchain-specific address derivation",
    ):
        provider.get_address(
            "address-wallet",
            "ethereum",
        )


def test_address_requires_blockchain(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify a blockchain identifier is required.
    """

    provider.create_wallet(
        wallet_id="address-validation"
    )

    with pytest.raises(
        ValueError,
        match="Blockchain is required",
    ):
        provider.get_address(
            "address-validation",
            "",
        )


###############################################################################
# Status
###############################################################################


def test_status_report(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify custody status reporting.
    """

    provider.create_wallet(
        wallet_id="status-wallet"
    )

    status = provider.get_status(
        "status-wallet"
    )

    assert (
        status["wallet_id"]
        == "status-wallet"
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


def test_status_after_unlock(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify status changes after unlocking.
    """

    provider.create_wallet(
        wallet_id="status-unlock"
    )

    provider.unlock(
        "status-unlock",
        password="test-password",
    )

    status = provider.get_status(
        "status-unlock"
    )

    assert (
        status["status"]
        == "UNLOCKED"
    )

    assert (
        status["unlocked"]
        is True
    )


###############################################################################
# Deletion
###############################################################################


def test_delete_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify wallet deletion.
    """

    provider.create_wallet(
        wallet_id="delete-wallet"
    )

    provider.delete_wallet(
        "delete-wallet"
    )

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.get_status(
            "delete-wallet"
        )


def test_delete_unlocked_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify deleting an unlocked wallet removes its
    unlocked runtime state.
    """

    provider.create_wallet(
        wallet_id="delete-unlocked"
    )

    provider.unlock(
        "delete-unlocked",
        password="test-password",
    )

    assert (
        provider.is_unlocked(
            "delete-unlocked"
        )
        is True
    )

    provider.delete_wallet(
        "delete-unlocked"
    )

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.is_unlocked(
            "delete-unlocked"
        )


def test_delete_unknown_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify deleting an unknown wallet raises KeyError.
    """

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.delete_wallet(
            "unknown-wallet"
        )


###############################################################################
# Unknown Wallet Validation
###############################################################################


def test_unlock_unknown_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify unlocking an unknown wallet fails.
    """

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.unlock(
            "unknown-wallet",
            password="test-password",
        )


def test_lock_unknown_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify locking an unknown wallet fails.
    """

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.lock(
            "unknown-wallet"
        )


def test_status_unknown_wallet(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify status lookup for an unknown wallet fails.
    """

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider.get_status(
            "unknown-wallet"
        )


###############################################################################
# Representation
###############################################################################


def test_provider_repr(
    provider: NonCustodialProvider,
) -> None:
    """
    Verify developer representation.
    """

    representation = repr(
        provider
    )

    assert (
        "NonCustodialProvider"
        in representation
    )

    assert (
        "non_custodial"
        in representation
    )


###############################################################################
# End of File
###############################################################################
