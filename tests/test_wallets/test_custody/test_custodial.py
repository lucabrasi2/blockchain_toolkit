"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.test_custody.test_custodial

Purpose
-------
Tests for the UBP custodial custody provider.

These tests verify the actual CustodialProvider contract:
- internal wallet lifecycle
- custody identity
- backend boundary
- locking and unlocking
- transaction-signing delegation
- public-key delegation
- address delegation
- status reporting
- deletion
- validation

The tests intentionally do not require real HSM, MPC, KMS,
or external custody infrastructure.

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
from wallets.custody.custodial import CustodialProvider


###############################################################################
# Dummy Backend
###############################################################################


class DummyCustodyBackend:
    """
    Test-only backend.

    This represents the future secure custody boundary.
    It deliberately does not contain real cryptographic logic.
    """

    def __init__(self) -> None:
        self.unlock_calls: list[tuple[str, dict]] = []
        self.sign_calls: list[tuple[str, dict]] = []
        self.public_key_calls: list[str] = []
        self.address_calls: list[tuple[str, str]] = []

    def unlock(
        self,
        wallet_id: str,
        **credentials,
    ) -> bool:
        self.unlock_calls.append(
            (
                wallet_id,
                dict(credentials),
            )
        )

        return True

    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict,
    ) -> str:
        self.sign_calls.append(
            (
                wallet_id,
                dict(transaction),
            )
        )

        return "dummy-signed-transaction"

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        self.public_key_calls.append(
            wallet_id
        )

        return "dummy-public-key"

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        self.address_calls.append(
            (
                wallet_id,
                blockchain,
            )
        )

        return "dummy-address"


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def backend() -> DummyCustodyBackend:
    """
    Return a fresh dummy custody backend.
    """

    return DummyCustodyBackend()


@pytest.fixture
def provider() -> CustodialProvider:
    """
    Return a custodial provider without a backend.

    This is useful for testing the provider's internal wallet
    lifecycle and backend-required boundaries.
    """

    return CustodialProvider()


@pytest.fixture
def provider_with_backend(
    backend: DummyCustodyBackend,
) -> CustodialProvider:
    """
    Return a custodial provider connected to the dummy backend.
    """

    return CustodialProvider(
        backend=backend
    )


###############################################################################
# Identity
###############################################################################


def test_provider_is_custody_provider(
    provider: CustodialProvider,
) -> None:
    """
    Verify CustodialProvider implements CustodyProvider.
    """

    assert isinstance(
        provider,
        CustodyProvider,
    )


def test_provider_custody_type(
    provider: CustodialProvider,
) -> None:
    """
    Verify the provider identifies itself as custodial.
    """

    assert (
        provider.custody_type
        == CustodyType.CUSTODIAL
    )


def test_provider_without_backend_is_valid(
    provider: CustodialProvider,
) -> None:
    """
    Verify the provider may be initialized before a secure
    custody backend is configured.
    """

    assert (
        provider.backend
        is None
    )


def test_provider_with_backend(
    provider_with_backend: CustodialProvider,
    backend: DummyCustodyBackend,
) -> None:
    """
    Verify the configured backend is exposed through the
    backend property.
    """

    assert (
        provider_with_backend.backend
        is backend
    )


###############################################################################
# Wallet Creation
###############################################################################


def test_create_wallet(
    provider: CustodialProvider,
) -> None:
    """
    Verify a custodial wallet record can be created.
    """

    result = provider.create_wallet(
        wallet_id="custodial-001"
    )

    assert (
        result["wallet_id"]
        == "custodial-001"
    )

    assert (
        result["custody_type"]
        == CustodyType.CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )

    assert (
        result["backend"]
        is None
    )


def test_create_wallet_with_backend(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify wallet metadata identifies the configured backend.
    """

    result = provider_with_backend.create_wallet(
        wallet_id="custodial-002"
    )

    assert (
        result["wallet_id"]
        == "custodial-002"
    )

    assert (
        result["backend"]
        == "DummyCustodyBackend"
    )


def test_create_wallet_generates_identifier(
    provider: CustodialProvider,
) -> None:
    """
    Verify the provider generates an identifier when one is
    not explicitly supplied.
    """

    result = provider.create_wallet()

    assert result["wallet_id"]

    assert isinstance(
        result["wallet_id"],
        str,
    )

    assert (
        result["custody_type"]
        == CustodyType.CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )


def test_duplicate_wallet_rejected(
    provider: CustodialProvider,
) -> None:
    """
    Verify duplicate wallet identifiers are rejected.
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
    provider: CustodialProvider,
) -> None:
    """
    Verify an imported custodial wallet record.
    """

    result = provider.import_wallet(
        wallet_id="imported-001"
    )

    assert (
        result["wallet_id"]
        == "imported-001"
    )

    assert (
        result["custody_type"]
        == CustodyType.CUSTODIAL
    )

    assert (
        result["status"]
        == "LOCKED"
    )

    assert (
        result["imported"]
        is True
    )


def test_import_wallet_generates_identifier(
    provider: CustodialProvider,
) -> None:
    """
    Verify imported wallets can receive generated identifiers.
    """

    result = provider.import_wallet()

    assert result["wallet_id"]

    assert (
        result["imported"]
        is True
    )


def test_duplicate_import_rejected(
    provider: CustodialProvider,
) -> None:
    """
    Verify duplicate imported wallet identifiers are rejected.
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
    provider: CustodialProvider,
) -> None:
    """
    Verify newly created wallets start locked.
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


def test_lock_wallet(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify locking an existing wallet keeps it locked.
    """

    provider_with_backend.create_wallet(
        wallet_id="lock-wallet"
    )

    provider_with_backend.lock(
        "lock-wallet"
    )

    assert (
        provider_with_backend.is_unlocked(
            "lock-wallet"
        )
        is False
    )


def test_unlock_requires_credentials(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify credentials are required for unlocking.
    """

    provider_with_backend.create_wallet(
        wallet_id="credential-wallet"
    )

    with pytest.raises(
        ValueError,
        match="Unlock credentials are required",
    ):
        provider_with_backend.unlock(
            "credential-wallet"
        )


def test_unlock_requires_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify unlocking fails when no custody backend exists.
    """

    provider.create_wallet(
        wallet_id="no-backend-wallet"
    )

    with pytest.raises(
        RuntimeError,
        match="No custodial backend is configured",
    ):
        provider.unlock(
            "no-backend-wallet",
            password="test-password",
        )


def test_unlock_delegates_to_backend(
    provider_with_backend: CustodialProvider,
    backend: DummyCustodyBackend,
) -> None:
    """
    Verify unlock credentials are delegated to the backend.
    """

    provider_with_backend.create_wallet(
        wallet_id="backend-unlock"
    )

    result = provider_with_backend.unlock(
        "backend-unlock",
        password="test-password",
    )

    assert result is True

    assert (
        provider_with_backend.is_unlocked(
            "backend-unlock"
        )
        is True
    )

    assert len(
        backend.unlock_calls
    ) == 1

    wallet_id, credentials = (
        backend.unlock_calls[0]
    )

    assert (
        wallet_id
        == "backend-unlock"
    )

    assert (
        credentials["password"]
        == "test-password"
    )


def test_lock_after_unlock(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify a wallet can be locked after successful unlocking.
    """

    provider_with_backend.create_wallet(
        wallet_id="relock-wallet"
    )

    provider_with_backend.unlock(
        "relock-wallet",
        password="test-password",
    )

    assert (
        provider_with_backend.is_unlocked(
            "relock-wallet"
        )
        is True
    )

    provider_with_backend.lock(
        "relock-wallet"
    )

    assert (
        provider_with_backend.is_unlocked(
            "relock-wallet"
        )
        is False
    )


###############################################################################
# Signing Boundary
###############################################################################


def test_signing_requires_unlocked_wallet(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify signing is unavailable while the wallet is locked.
    """

    provider_with_backend.create_wallet(
        wallet_id="sign-locked"
    )

    with pytest.raises(
        PermissionError,
        match="must be unlocked",
    ):
        provider_with_backend.sign_transaction(
            "sign-locked",
            {
                "operation": "test",
            },
        )


def test_signing_requires_dictionary(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify transaction payloads must be dictionaries.
    """

    provider_with_backend.create_wallet(
        wallet_id="invalid-transaction"
    )

    provider_with_backend.unlock(
        "invalid-transaction",
        password="test-password",
    )

    with pytest.raises(
        TypeError,
        match="Transaction must be a dictionary",
    ):
        provider_with_backend.sign_transaction(
            "invalid-transaction",
            "invalid-transaction",
        )


def test_signing_requires_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify signing requires a configured backend.
    """

    provider.create_wallet(
        wallet_id="sign-no-backend"
    )

    # The wallet must first be unlocked. Without a backend,
    # unlocking itself is unavailable, so the signing boundary
    # is represented by the locked-wallet protection.
    with pytest.raises(
        PermissionError,
        match="must be unlocked",
    ):
        provider.sign_transaction(
            "sign-no-backend",
            {
                "operation": "test",
            },
        )


def test_sign_transaction_delegates_to_backend(
    provider_with_backend: CustodialProvider,
    backend: DummyCustodyBackend,
) -> None:
    """
    Verify transaction signing is delegated to the backend.
    """

    provider_with_backend.create_wallet(
        wallet_id="sign-wallet"
    )

    provider_with_backend.unlock(
        "sign-wallet",
        password="test-password",
    )

    transaction = {
        "operation": "test",
        "amount": 100,
    }

    result = provider_with_backend.sign_transaction(
        "sign-wallet",
        transaction,
    )

    assert (
        result
        == "dummy-signed-transaction"
    )

    assert len(
        backend.sign_calls
    ) == 1

    wallet_id, received_transaction = (
        backend.sign_calls[0]
    )

    assert (
        wallet_id
        == "sign-wallet"
    )

    assert (
        received_transaction
        == transaction
    )


###############################################################################
# Public Information
###############################################################################


def test_public_key_requires_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify public-key retrieval requires a custody backend.
    """

    provider.create_wallet(
        wallet_id="public-key-no-backend"
    )

    with pytest.raises(
        RuntimeError,
        match="No custodial backend is configured",
    ):
        provider.get_public_key(
            "public-key-no-backend"
        )


def test_public_key_delegates_to_backend(
    provider_with_backend: CustodialProvider,
    backend: DummyCustodyBackend,
) -> None:
    """
    Verify public-key retrieval is delegated to the backend.
    """

    provider_with_backend.create_wallet(
        wallet_id="public-key-wallet"
    )

    result = provider_with_backend.get_public_key(
        "public-key-wallet"
    )

    assert (
        result
        == "dummy-public-key"
    )

    assert (
        backend.public_key_calls
        == ["public-key-wallet"]
    )


def test_address_requires_blockchain(
    provider: CustodialProvider,
) -> None:
    """
    Verify blockchain identification is required.
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


def test_address_requires_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify address retrieval requires a custody backend.
    """

    provider.create_wallet(
        wallet_id="address-no-backend"
    )

    with pytest.raises(
        RuntimeError,
        match="No custodial backend is configured",
    ):
        provider.get_address(
            "address-no-backend",
            "ethereum",
        )


def test_address_delegates_to_backend(
    provider_with_backend: CustodialProvider,
    backend: DummyCustodyBackend,
) -> None:
    """
    Verify blockchain address retrieval is delegated.
    """

    provider_with_backend.create_wallet(
        wallet_id="address-wallet"
    )

    result = provider_with_backend.get_address(
        "address-wallet",
        "ethereum",
    )

    assert (
        result
        == "dummy-address"
    )

    assert (
        backend.address_calls
        == [
            (
                "address-wallet",
                "ethereum",
            )
        ]
    )


###############################################################################
# Status
###############################################################################


def test_status_without_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify status accurately reports the absence of a backend.
    """

    provider.create_wallet(
        wallet_id="status-no-backend"
    )

    status = provider.get_status(
        "status-no-backend"
    )

    assert (
        status["wallet_id"]
        == "status-no-backend"
    )

    assert (
        status["custody_type"]
        == CustodyType.CUSTODIAL
    )

    assert (
        status["status"]
        == "LOCKED"
    )

    assert (
        status["unlocked"]
        is False
    )

    assert (
        status["backend_configured"]
        is False
    )


def test_status_with_backend(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify status reports backend availability.
    """

    provider_with_backend.create_wallet(
        wallet_id="status-backend"
    )

    status = provider_with_backend.get_status(
        "status-backend"
    )

    assert (
        status["backend_configured"]
        is True
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
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify status changes after successful unlocking.
    """

    provider_with_backend.create_wallet(
        wallet_id="status-unlock"
    )

    provider_with_backend.unlock(
        "status-unlock",
        password="test-password",
    )

    status = provider_with_backend.get_status(
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

    assert (
        status["backend_configured"]
        is True
    )


###############################################################################
# Deletion
###############################################################################


def test_delete_wallet(
    provider: CustodialProvider,
) -> None:
    """
    Verify an existing wallet can be deleted.
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
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify deletion removes the unlocked runtime state.
    """

    provider_with_backend.create_wallet(
        wallet_id="delete-unlocked"
    )

    provider_with_backend.unlock(
        "delete-unlocked",
        password="test-password",
    )

    assert (
        provider_with_backend.is_unlocked(
            "delete-unlocked"
        )
        is True
    )

    provider_with_backend.delete_wallet(
        "delete-unlocked"
    )

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider_with_backend.is_unlocked(
            "delete-unlocked"
        )


def test_delete_unknown_wallet(
    provider: CustodialProvider,
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


def test_lock_unknown_wallet(
    provider: CustodialProvider,
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


def test_unlock_unknown_wallet(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify unlocking an unknown wallet fails before reaching
    the backend.
    """

    with pytest.raises(
        KeyError,
        match="not found",
    ):
        provider_with_backend.unlock(
            "unknown-wallet",
            password="test-password",
        )


def test_status_unknown_wallet(
    provider: CustodialProvider,
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


def test_provider_repr_without_backend(
    provider: CustodialProvider,
) -> None:
    """
    Verify representation without a backend.
    """

    representation = repr(
        provider
    )

    assert (
        "CustodialProvider"
        in representation
    )

    assert (
        "wallets=0"
        in representation
    )

    assert (
        "custodial"
        in representation
    )

    assert (
        "backend_configured=False"
        in representation
    )


def test_provider_repr_with_backend(
    provider_with_backend: CustodialProvider,
) -> None:
    """
    Verify representation with a backend.
    """

    representation = repr(
        provider_with_backend
    )

    assert (
        "CustodialProvider"
        in representation
    )

    assert (
        "backend_configured=True"
        in representation
    )


###############################################################################
# End of File
###############################################################################
