"""
Universal Blockchain Platform (UBP)
Module:
tests.test_transactions.test_transaction
Purpose:
Tests for the core Transaction entity.
Project:
Universal Blockchain Platform (UBP)
"""
from __future__ import annotations

import pytest

from transactions.exceptions import (
    TransactionStateError,
    TransactionValidationError,
)
from transactions.transaction import (
    Transaction,
)


###############################################################################
# Test Fixtures
###############################################################################

def create_transaction() -> Transaction:
    """
    Create a valid Transaction instance for testing.
    """
    return Transaction(
        sender="sender-address",
        receiver="receiver-address",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
    )


###############################################################################
# Construction Tests
###############################################################################

def test_transaction_creation() -> None:
    """
    Verify a valid transaction can be created.
    """
    transaction = create_transaction()
    assert isinstance(
        transaction,
        Transaction,
    )
    assert transaction.sender == "sender-address"
    assert transaction.receiver == "receiver-address"
    assert transaction.amount == 100.0
    assert transaction.asset == "BTC"
    assert transaction.network == "bitcoin"


def test_transaction_generates_transaction_id() -> None:
    """
    Verify a transaction ID is generated when one is not supplied.
    """
    transaction = create_transaction()
    assert isinstance(
        transaction.transaction_id,
        str,
    )
    assert transaction.transaction_id


def test_transaction_accepts_custom_transaction_id() -> None:
    """
    Verify a caller-supplied transaction ID is preserved.
    """
    transaction = Transaction(
        sender="sender-address",
        receiver="receiver-address",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
        transaction_id="tx-001",
    )
    assert transaction.transaction_id == "tx-001"


def test_transaction_initial_state() -> None:
    """
    Verify newly created transactions begin in the created state.
    """
    transaction = create_transaction()
    assert transaction.status == "created"


def test_transaction_initial_signature_is_empty() -> None:
    """
    Verify a newly created transaction has no signature.
    """
    transaction = create_transaction()
    assert transaction.signature is None


def test_transaction_initial_metadata_is_empty() -> None:
    """
    Verify metadata defaults to an empty dictionary.
    """
    transaction = create_transaction()
    assert transaction.metadata == {}


def test_transaction_accepts_metadata() -> None:
    """
    Verify transaction metadata supplied during construction is preserved.
    """
    metadata = {
        "purpose": "test transaction",
        "reference": "UBP-001",
    }
    transaction = Transaction(
        sender="sender-address",
        receiver="receiver-address",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
        metadata=metadata,
    )
    assert transaction.metadata == metadata


###############################################################################
# Validation Tests
###############################################################################

def test_transaction_rejects_empty_sender() -> None:
    """
    Verify an empty sender is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Sender cannot be empty",
    ):
        Transaction(
            sender="",
            receiver="receiver-address",
            amount=100.0,
            asset="BTC",
            network="bitcoin",
        )


def test_transaction_rejects_empty_receiver() -> None:
    """
    Verify an empty receiver is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Receiver cannot be empty",
    ):
        Transaction(
            sender="sender-address",
            receiver="",
            amount=100.0,
            asset="BTC",
            network="bitcoin",
        )


def test_transaction_rejects_zero_amount() -> None:
    """
    Verify a zero transaction amount is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be greater than zero",
    ):
        Transaction(
            sender="sender-address",
            receiver="receiver-address",
            amount=0,
            asset="BTC",
            network="bitcoin",
        )


def test_transaction_rejects_negative_amount() -> None:
    """
    Verify a negative transaction amount is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be greater than zero",
    ):
        Transaction(
            sender="sender-address",
            receiver="receiver-address",
            amount=-1.0,
            asset="BTC",
            network="bitcoin",
        )


def test_transaction_rejects_empty_asset() -> None:
    """
    Verify an empty asset is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Asset cannot be empty",
    ):
        Transaction(
            sender="sender-address",
            receiver="receiver-address",
            amount=100.0,
            asset="",
            network="bitcoin",
        )


def test_transaction_rejects_empty_network() -> None:
    """
    Verify an empty network is rejected.
    """
    with pytest.raises(
        TransactionValidationError,
        match="Network cannot be empty",
    ):
        Transaction(
            sender="sender-address",
            receiver="receiver-address",
            amount=100.0,
            asset="BTC",
            network="",
        )


###############################################################################
# Transaction State Tests
###############################################################################

def test_valid_created_to_validated_transition() -> None:
    """
    Verify a created transaction can transition to validated.
    """
    transaction = create_transaction()
    assert transaction.validate_state_transition(
        "validated"
    ) is True
    transaction.update_status(
        "validated"
    )
    assert transaction.status == "validated"


def test_validated_to_signed_transition() -> None:
    """
    Verify a validated transaction can transition to signed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    assert transaction.validate_state_transition(
        "signed"
    ) is True
    transaction.update_status(
        "signed"
    )
    assert transaction.status == "signed"


def test_signed_to_broadcast_transition() -> None:
    """
    Verify a signed transaction can transition to broadcast.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    assert transaction.validate_state_transition(
        "broadcast"
    ) is True
    transaction.update_status(
        "broadcast"
    )
    assert transaction.status == "broadcast"


def test_broadcast_to_confirmed_transition() -> None:
    """
    Verify a broadcast transaction can transition to confirmed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    transaction.update_status(
        "broadcast"
    )
    assert transaction.validate_state_transition(
        "confirmed"
    ) is True
    transaction.update_status(
        "confirmed"
    )
    assert transaction.status == "confirmed"


def test_created_to_failed_transition() -> None:
    """
    Verify a created transaction can transition to failed.
    """
    transaction = create_transaction()
    assert transaction.validate_state_transition(
        "failed"
    ) is True
    transaction.update_status(
        "failed"
    )
    assert transaction.status == "failed"


def test_validated_to_failed_transition() -> None:
    """
    Verify a validated transaction can transition to failed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    assert transaction.validate_state_transition(
        "failed"
    ) is True
    transaction.update_status(
        "failed"
    )
    assert transaction.status == "failed"


def test_signed_to_failed_transition() -> None:
    """
    Verify a signed transaction can transition to failed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    assert transaction.validate_state_transition(
        "failed"
    ) is True
    transaction.update_status(
        "failed"
    )
    assert transaction.status == "failed"


def test_broadcast_to_failed_transition() -> None:
    """
    Verify a broadcast transaction can transition to failed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    transaction.update_status(
        "broadcast"
    )
    assert transaction.validate_state_transition(
        "failed"
    ) is True
    transaction.update_status(
        "failed"
    )
    assert transaction.status == "failed"


###############################################################################
# Invalid State Transition Tests
###############################################################################

def test_created_cannot_transition_directly_to_signed() -> None:
    """
    Verify created cannot transition directly to signed.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from created to signed",
    ):
        transaction.validate_state_transition(
            "signed"
        )


def test_created_cannot_transition_directly_to_broadcast() -> None:
    """
    Verify created cannot transition directly to broadcast.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from created to broadcast",
    ):
        transaction.validate_state_transition(
            "broadcast"
        )


def test_created_cannot_transition_directly_to_confirmed() -> None:
    """
    Verify created cannot transition directly to confirmed.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from created to confirmed",
    ):
        transaction.validate_state_transition(
            "confirmed"
        )


def test_validated_cannot_transition_to_broadcast() -> None:
    """
    Verify validated cannot transition directly to broadcast.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from validated to broadcast",
    ):
        transaction.validate_state_transition(
            "broadcast"
        )


def test_validated_cannot_transition_to_confirmed() -> None:
    """
    Verify validated cannot transition directly to confirmed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from validated to confirmed",
    ):
        transaction.validate_state_transition(
            "confirmed"
        )


def test_signed_cannot_transition_directly_to_confirmed() -> None:
    """
    Verify signed cannot transition directly to confirmed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from signed to confirmed",
    ):
        transaction.validate_state_transition(
            "confirmed"
        )


def test_confirmed_transaction_cannot_transition() -> None:
    """
    Verify confirmed is a terminal transaction state.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.update_status(
        "signed"
    )
    transaction.update_status(
        "broadcast"
    )
    transaction.update_status(
        "confirmed"
    )
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from confirmed to",
    ):
        transaction.validate_state_transition(
            "failed"
        )


def test_failed_transaction_cannot_transition() -> None:
    """
    Verify failed is a terminal transaction state.
    """
    transaction = create_transaction()
    transaction.update_status(
        "failed"
    )
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from failed to",
    ):
        transaction.validate_state_transition(
            "confirmed"
        )


###############################################################################
# Invalid State Value Tests
###############################################################################

def test_update_status_rejects_invalid_state() -> None:
    """
    Verify update_status rejects an unknown transaction state.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError,
        match="Invalid transaction state",
    ):
        transaction.update_status(
            "unknown"
        )


def test_validate_state_transition_rejects_invalid_state() -> None:
    """
    Verify invalid target states are rejected.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError,
        match="Cannot move transaction from created to unknown",
    ):
        transaction.validate_state_transition(
            "unknown"
        )


def test_invalid_transition_does_not_change_state() -> None:
    """
    Verify an invalid transition leaves the current state unchanged.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionStateError
    ):
        transaction.validate_state_transition(
            "confirmed"
        )
    assert transaction.status == "created"


###############################################################################
# Transaction Signing Tests
###############################################################################

def test_transaction_can_be_signed_from_created_state() -> None:
    """
    Verify a created transaction can receive a signature.
    """
    transaction = create_transaction()
    transaction.sign(
        "signed-transaction-data"
    )
    assert transaction.signature == (
        "signed-transaction-data"
    )
    assert transaction.status == "signed"


def test_transaction_can_be_signed_from_validated_state() -> None:
    """
    Verify a validated transaction can receive a signature.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.sign(
        "signed-transaction-data"
    )
    assert transaction.signature == (
        "signed-transaction-data"
    )
    assert transaction.status == "signed"


def test_sign_rejects_empty_signature() -> None:
    """
    Verify an empty signature is rejected.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionValidationError,
        match="Signature cannot be empty",
    ):
        transaction.sign(
            ""
        )


def test_sign_rejects_none_signature() -> None:
    """
    Verify a None signature is rejected.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionValidationError,
        match="Signature cannot be empty",
    ):
        transaction.sign(
            None  # type: ignore[arg-type]
        )


def test_signed_transaction_cannot_be_signed_again() -> None:
    """
    Verify an already signed transaction cannot be signed again.
    """
    transaction = create_transaction()
    transaction.sign(
        "first-signature"
    )
    with pytest.raises(
        TransactionStateError,
        match="Transaction cannot be signed in current state",
    ):
        transaction.sign(
            "second-signature"
        )


def test_broadcast_transaction_cannot_be_signed() -> None:
    """
    Verify a broadcast transaction cannot be signed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.sign(
        "signed-transaction-data"
    )
    transaction.update_status(
        "broadcast"
    )
    with pytest.raises(
        TransactionStateError,
        match="Transaction cannot be signed in current state",
    ):
        transaction.sign(
            "another-signature"
        )


def test_confirmed_transaction_cannot_be_signed() -> None:
    """
    Verify a confirmed transaction cannot be signed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    transaction.sign(
        "signed-transaction-data"
    )
    transaction.update_status(
        "broadcast"
    )
    transaction.update_status(
        "confirmed"
    )
    with pytest.raises(
        TransactionStateError,
        match="Transaction cannot be signed in current state",
    ):
        transaction.sign(
            "another-signature"
        )


def test_failed_transaction_cannot_be_signed() -> None:
    """
    Verify a failed transaction cannot be signed.
    """
    transaction = create_transaction()
    transaction.update_status(
        "failed"
    )
    with pytest.raises(
        TransactionStateError,
        match="Transaction cannot be signed in current state",
    ):
        transaction.sign(
            "signed-transaction-data"
        )


def test_failed_sign_attempt_does_not_add_signature() -> None:
    """
    Verify a rejected signing operation does not modify the signature.
    """
    transaction = create_transaction()
    with pytest.raises(
        TransactionValidationError
    ):
        transaction.sign(
            ""
        )
    assert transaction.signature is None
    assert transaction.status == "created"


def test_signing_preserves_transaction_identity() -> None:
    """
    Verify signing does not change the transaction ID.
    """
    transaction = create_transaction()
    original_id = transaction.transaction_id
    transaction.sign(
        "signed-transaction-data"
    )
    assert transaction.transaction_id == original_id


def test_signing_preserves_transaction_data() -> None:
    """
    Verify signing does not modify the core transaction fields.
    """
    transaction = create_transaction()
    original_sender = transaction.sender
    original_receiver = transaction.receiver
    original_amount = transaction.amount
    original_asset = transaction.asset
    original_network = transaction.network
    transaction.sign(
        "signed-transaction-data"
    )
    assert transaction.sender == original_sender
    assert transaction.receiver == original_receiver
    assert transaction.amount == original_amount
    assert transaction.asset == original_asset
    assert transaction.network == original_network


###############################################################################
# Transaction Serialization Tests
###############################################################################

def test_transaction_to_dict_returns_dictionary() -> None:
    """
    Verify transaction serialization returns a dictionary.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert isinstance(
        data,
        dict,
    )


def test_transaction_to_dict_contains_transaction_id() -> None:
    """
    Verify serialized transaction contains its transaction ID.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["transaction_id"] == (
        transaction.transaction_id
    )


def test_transaction_to_dict_contains_sender() -> None:
    """
    Verify serialized transaction contains the sender.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["sender"] == "sender-address"


def test_transaction_to_dict_contains_receiver() -> None:
    """
    Verify serialized transaction contains the receiver.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["receiver"] == "receiver-address"


def test_transaction_to_dict_contains_amount() -> None:
    """
    Verify serialized transaction contains the amount.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["amount"] == 100.0


def test_transaction_to_dict_contains_asset() -> None:
    """
    Verify serialized transaction contains the asset.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["asset"] == "BTC"


def test_transaction_to_dict_contains_network() -> None:
    """
    Verify serialized transaction contains the network.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["network"] == "bitcoin"


def test_transaction_to_dict_contains_status() -> None:
    """
    Verify serialized transaction contains its current status.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["status"] == "created"


def test_transaction_to_dict_contains_empty_signature() -> None:
    """
    Verify an unsigned transaction serializes with no signature.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert data["signature"] is None


def test_transaction_to_dict_contains_signature_after_signing() -> None:
    """
    Verify serialized transaction contains its signature after signing.
    """
    transaction = create_transaction()
    transaction.sign(
        "signed-transaction-data"
    )
    data = transaction.to_dict()
    assert data["signature"] == (
        "signed-transaction-data"
    )
    assert data["status"] == "signed"


def test_transaction_to_dict_contains_timestamp() -> None:
    """
    Verify serialized transaction contains a timestamp.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    assert "timestamp" in data
    assert isinstance(
        data["timestamp"],
        str,
    )
    assert data["timestamp"]


def test_transaction_to_dict_contains_metadata() -> None:
    """
    Verify serialized transaction contains metadata.
    """
    metadata = {
        "purpose": "test transaction",
        "reference": "UBP-001",
    }
    transaction = Transaction(
        sender="sender-address",
        receiver="receiver-address",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
        metadata=metadata,
    )
    data = transaction.to_dict()
    assert data["metadata"] == metadata


def test_transaction_to_dict_preserves_metadata_values() -> None:
    """
    Verify metadata values survive serialization unchanged.
    """
    metadata = {
        "reference": "TX-001",
        "purpose": "wallet transfer",
        "priority": "normal",
    }
    transaction = Transaction(
        sender="sender-address",
        receiver="receiver-address",
        amount=250.0,
        asset="BTC",
        network="bitcoin",
        metadata=metadata,
    )
    data = transaction.to_dict()
    assert data["metadata"]["reference"] == "TX-001"
    assert data["metadata"]["purpose"] == "wallet transfer"
    assert data["metadata"]["priority"] == "normal"


def test_transaction_to_dict_reflects_state_changes() -> None:
    """
    Verify serialization reflects the current transaction state.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    data = transaction.to_dict()
    assert data["status"] == "validated"
    transaction.sign(
        "signed-transaction-data"
    )
    data = transaction.to_dict()
    assert data["status"] == "signed"
    assert data["signature"] == (
        "signed-transaction-data"
    )


def test_transaction_to_dict_contains_expected_fields() -> None:
    """
    Verify the complete serialized transaction structure.
    """
    transaction = create_transaction()
    data = transaction.to_dict()
    expected_fields = {
        "transaction_id",
        "sender",
        "receiver",
        "amount",
        "asset",
        "network",
        "status",
        "signature",
        "timestamp",
        "metadata",
    }
    assert set(data.keys()) == expected_fields


def test_transaction_to_dict_does_not_modify_transaction() -> None:
    """
    Verify serialization does not modify the transaction object.
    """
    transaction = create_transaction()
    original_id = transaction.transaction_id
    original_status = transaction.status
    original_signature = transaction.signature
    original_metadata = transaction.metadata.copy()
    data = transaction.to_dict()
    assert data["transaction_id"] == original_id
    assert transaction.status == original_status
    assert transaction.signature == original_signature
    assert transaction.metadata == original_metadata


###############################################################################
# Transaction Information Tests
###############################################################################

def test_transaction_info_returns_dictionary() -> None:
    """
    Verify transaction information is returned as a dictionary.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert isinstance(
        result,
        dict,
    )


def test_transaction_info_contains_service() -> None:
    """
    Verify transaction information identifies the service.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["service"] == "Transaction Entity"


def test_transaction_info_contains_version() -> None:
    """
    Verify transaction information contains the entity version.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["version"] == "2.0 Enterprise"


def test_transaction_info_contains_transaction_id() -> None:
    """
    Verify transaction information contains the transaction ID.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["transaction_id"] == (
        transaction.transaction_id
    )


def test_transaction_info_contains_network() -> None:
    """
    Verify transaction information contains the network.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["network"] == "bitcoin"


def test_transaction_info_contains_asset() -> None:
    """
    Verify transaction information contains the asset.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["asset"] == "BTC"


def test_transaction_info_contains_status() -> None:
    """
    Verify transaction information contains the current status.
    """
    transaction = create_transaction()
    result = transaction.info()
    assert result["status"] == "created"


def test_transaction_info_reflects_status_changes() -> None:
    """
    Verify transaction information reflects the current lifecycle state.
    """
    transaction = create_transaction()
    transaction.update_status(
        "validated"
    )
    result = transaction.info()
    assert result["status"] == "validated"
    transaction.sign(
        "signed-transaction-data"
    )
    result = transaction.info()
    assert result["status"] == "signed"


def test_transaction_info_contains_expected_fields() -> None:
    """
    Verify the complete transaction information structure.
    """
    transaction = create_transaction()
    result = transaction.info()
    expected_fields = {
        "service",
        "version",
        "transaction_id",
        "network",
        "asset",
        "status",
    }
    assert set(result.keys()) == expected_fields


###############################################################################
# Transaction Representation Tests
###############################################################################

def test_transaction_repr_contains_class_name() -> None:
    """
    Verify the representation identifies the Transaction class.
    """
    transaction = create_transaction()
    result = repr(
        transaction
    )
    assert "Transaction" in result


def test_transaction_repr_contains_transaction_id() -> None:
    """
    Verify the representation contains the transaction ID.
    """
    transaction = create_transaction()
    result = repr(
        transaction
    )
    assert transaction.transaction_id in result


def test_transaction_repr_contains_network() -> None:
    """
    Verify the representation contains the transaction network.
    """
    transaction = create_transaction()
    result = repr(
        transaction
    )
    assert "bitcoin" in result


def test_transaction_repr_contains_status() -> None:
    """
    Verify the representation contains the transaction status.
    """
    transaction = create_transaction()
    result = repr(
        transaction
    )
    assert "created" in result


def test_transaction_repr_does_not_expose_signature() -> None:
    """
    Verify the representation does not expose transaction signatures.
    """
    transaction = create_transaction()
    transaction.sign(
        "secret-signature-data"
    )
    result = repr(
        transaction
    )
    assert "secret-signature-data" not in result


###############################################################################
# End of File
###############################################################################