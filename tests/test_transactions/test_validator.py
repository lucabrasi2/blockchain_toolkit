"""
Universal Blockchain Platform (UBP)

Module:
tests.test_transactions.test_validator

Purpose:
Tests for the TransactionValidator service.

Project:
Universal Blockchain Platform (UBP)
"""

from __future__ import annotations

import pytest

from transactions.exceptions import (
    TransactionValidationError,
)

from transactions.transaction import (
    Transaction,
)

from transactions.validator import (
    TransactionValidator,
)


###############################################################################
# Test Fixtures
###############################################################################


@pytest.fixture
def validator() -> TransactionValidator:
    """
    Return a TransactionValidator instance.
    """

    return TransactionValidator()


def create_transaction() -> Transaction:
    """
    Create a valid Transaction instance for validator testing.

    The current generic validator accepts alphanumeric
    blockchain-independent address values.
    """

    return Transaction(
        sender="senderaddress",
        receiver="receiveraddress",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
    )


###############################################################################
# Construction Tests
###############################################################################


def test_validator_creation(
    validator: TransactionValidator,
) -> None:
    """
    Verify the validator can be instantiated.
    """

    assert isinstance(
        validator,
        TransactionValidator,
    )


###############################################################################
# Transaction Validation Tests
###############################################################################


def test_validate_transaction_success(
    validator: TransactionValidator,
) -> None:
    """
    Verify a valid Transaction object passes validation.
    """

    transaction = create_transaction()

    assert validator.validate_transaction(
        transaction
    ) is True


def test_validate_transaction_rejects_non_transaction(
    validator: TransactionValidator,
) -> None:
    """
    Verify validation rejects objects that are not Transaction instances.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Expected Transaction instance",
    ):
        validator.validate_transaction(
            {
                "sender": "senderaddress",
            }  # type: ignore[arg-type]
        )


def test_validate_transaction_rejects_invalid_transaction_id(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the transaction ID.
    """

    transaction = create_transaction()

    transaction.transaction_id = "invalid"

    with pytest.raises(
        TransactionValidationError,
        match="Invalid transaction ID",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_rejects_invalid_sender(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the sender.
    """

    transaction = create_transaction()

    transaction.sender = "!!invalid!!"

    with pytest.raises(
        TransactionValidationError,
        match="Invalid sender address",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_rejects_invalid_receiver(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the receiver.
    """

    transaction = create_transaction()

    transaction.receiver = "!!invalid!!"

    with pytest.raises(
        TransactionValidationError,
        match="Invalid receiver address",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_rejects_invalid_amount(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the amount.
    """

    transaction = create_transaction()

    transaction.amount = 0

    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be greater than zero",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_rejects_invalid_asset(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the asset.
    """

    transaction = create_transaction()

    transaction.asset = "!"

    with pytest.raises(
        TransactionValidationError,
        match="Invalid asset format",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_rejects_invalid_network(
    validator: TransactionValidator,
) -> None:
    """
    Verify transaction-level validation checks the network.
    """

    transaction = create_transaction()

    transaction.network = "!"

    with pytest.raises(
        TransactionValidationError,
        match="Invalid network format",
    ):
        validator.validate_transaction(
            transaction
        )


def test_validate_transaction_accepts_metadata(
    validator: TransactionValidator,
) -> None:
    """
    Verify valid transaction metadata passes validation.
    """

    transaction = Transaction(
        sender="senderaddress",
        receiver="receiveraddress",
        amount=100.0,
        asset="BTC",
        network="bitcoin",
        metadata={
            "purpose": "test",
            "reference": "UBP-001",
        },
    )

    assert validator.validate_transaction(
        transaction
    ) is True


def test_validate_transaction_rejects_invalid_metadata(
    validator: TransactionValidator,
) -> None:
    """
    Verify invalid metadata is rejected.
    """

    transaction = create_transaction()

    transaction.metadata = {
        123: "invalid-key",
    }

    with pytest.raises(
        TransactionValidationError,
        match="Metadata keys must be strings",
    ):
        validator.validate_transaction(
            transaction
        )


###############################################################################
# End of Part 1
###############################################################################
###############################################################################
# Individual Sender Validation Tests
###############################################################################


def test_validate_sender_accepts_valid_sender(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_sender accepts a valid sender address.
    """

    assert validator.validate_sender(
        "senderaddress"
    ) is True


def test_validate_sender_rejects_empty_sender(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_sender rejects an empty sender.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Sender address cannot be empty",
    ):
        validator.validate_sender(
            ""
        )


def test_validate_sender_rejects_non_string_sender(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_sender rejects a non-string sender.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Sender address must be a string",
    ):
        validator.validate_sender(
            123  # type: ignore[arg-type]
        )


def test_validate_sender_rejects_invalid_format(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_sender rejects an invalid sender format.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Invalid sender address",
    ):
        validator.validate_sender(
            "!!invalid!!"
        )


###############################################################################
# Individual Receiver Validation Tests
###############################################################################


def test_validate_receiver_accepts_valid_receiver(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_receiver accepts a valid receiver address.
    """

    assert validator.validate_receiver(
        "receiveraddress"
    ) is True


def test_validate_receiver_rejects_empty_receiver(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_receiver rejects an empty receiver.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Receiver address cannot be empty",
    ):
        validator.validate_receiver(
            ""
        )


def test_validate_receiver_rejects_non_string_receiver(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_receiver rejects a non-string receiver.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Receiver address must be a string",
    ):
        validator.validate_receiver(
            123  # type: ignore[arg-type]
        )


def test_validate_receiver_rejects_invalid_format(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_receiver rejects an invalid receiver format.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Invalid receiver address",
    ):
        validator.validate_receiver(
            "!!invalid!!"
        )


###############################################################################
# Amount Validation Tests
###############################################################################


def test_validate_amount_accepts_positive_amount(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_amount accepts a positive amount.
    """

    assert validator.validate_amount(
        100.0
    ) is True


def test_validate_amount_accepts_integer_amount(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_amount accepts a positive integer amount.
    """

    assert validator.validate_amount(
        100
    ) is True


def test_validate_amount_rejects_zero(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_amount rejects zero.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be greater than zero",
    ):
        validator.validate_amount(
            0
        )


def test_validate_amount_rejects_negative_amount(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_amount rejects a negative amount.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be greater than zero",
    ):
        validator.validate_amount(
            -1
        )


def test_validate_amount_rejects_non_numeric_amount(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_amount rejects a non-numeric amount.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Transaction amount must be numeric",
    ):
        validator.validate_amount(
            "100"  # type: ignore[arg-type]
        )


###############################################################################
# Asset Validation Tests
###############################################################################


def test_validate_asset_accepts_valid_asset(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_asset accepts a valid asset identifier.
    """

    assert validator.validate_asset(
        "BTC"
    ) is True


def test_validate_asset_accepts_lowercase_asset(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_asset accepts a lowercase asset identifier.
    """

    assert validator.validate_asset(
        "btc"
    ) is True


def test_validate_asset_rejects_empty_asset(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_asset rejects an empty asset.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Asset cannot be empty",
    ):
        validator.validate_asset(
            ""
        )


def test_validate_asset_rejects_non_string_asset(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_asset rejects a non-string asset.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Asset must be a string",
    ):
        validator.validate_asset(
            123  # type: ignore[arg-type]
        )


def test_validate_asset_rejects_invalid_format(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_asset rejects an invalid asset format.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Invalid asset format",
    ):
        validator.validate_asset(
            "!"
        )


###############################################################################
# Network Validation Tests
###############################################################################


def test_validate_network_accepts_valid_network(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_network accepts a valid network identifier.
    """

    assert validator.validate_network(
        "bitcoin"
    ) is True


def test_validate_network_accepts_alphanumeric_network(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_network accepts an alphanumeric network identifier.
    """

    assert validator.validate_network(
        "ethereum1"
    ) is True


def test_validate_network_rejects_empty_network(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_network rejects an empty network.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Network cannot be empty",
    ):
        validator.validate_network(
            ""
        )


def test_validate_network_rejects_non_string_network(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_network rejects a non-string network.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Network must be a string",
    ):
        validator.validate_network(
            123  # type: ignore[arg-type]
        )


def test_validate_network_rejects_invalid_format(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_network rejects an invalid network format.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Invalid network format",
    ):
        validator.validate_network(
            "!"
        )


###############################################################################
# Transaction ID Validation Tests
###############################################################################


def test_validate_transaction_id_accepts_valid_id(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_transaction_id accepts a valid transaction ID.
    """

    assert validator.validate_transaction_id(
        "abc123"
    ) is True


def test_validate_transaction_id_rejects_empty_id(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_transaction_id rejects an empty transaction ID.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Transaction ID cannot be empty",
    ):
        validator.validate_transaction_id(
            ""
        )


def test_validate_transaction_id_rejects_non_string_id(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_transaction_id rejects a non-string transaction ID.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Transaction ID must be a string",
    ):
        validator.validate_transaction_id(
            123  # type: ignore[arg-type]
        )


def test_validate_transaction_id_rejects_invalid_format(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_transaction_id rejects an invalid format.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Invalid transaction ID",
    ):
        validator.validate_transaction_id(
            "!!invalid!!"
        )


###############################################################################
# Metadata Validation Tests
###############################################################################


def test_validate_metadata_accepts_empty_metadata(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_metadata accepts an empty metadata dictionary.
    """

    assert validator.validate_metadata(
        {}
    ) is True


def test_validate_metadata_accepts_valid_metadata(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_metadata accepts valid metadata.
    """

    metadata = {
        "purpose": "test",
        "reference": "UBP-001",
    }

    assert validator.validate_metadata(
        metadata
    ) is True


def test_validate_metadata_rejects_non_dictionary(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_metadata rejects non-dictionary metadata.
    """

    with pytest.raises(
        TransactionValidationError,
        match="Metadata must be a dictionary",
    ):
        validator.validate_metadata(
            "invalid"  # type: ignore[arg-type]
        )


def test_validate_metadata_rejects_non_string_key(
    validator: TransactionValidator,
) -> None:
    """
    Verify validate_metadata rejects metadata keys that are not strings.
    """

    metadata = {
        123: "invalid-key",
    }

    with pytest.raises(
        TransactionValidationError,
        match="Metadata keys must be strings",
    ):
        validator.validate_metadata(
            metadata
        )


###############################################################################
# End of Part 2
###############################################################################