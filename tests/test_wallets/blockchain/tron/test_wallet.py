"""
Universal Blockchain Platform (UBP)

## Module

tests.test_wallets.blockchain.tron.test_wallet

## Purpose

Tests for the UBP TRON blockchain wallet.

No real TRON network calls are performed.
The TronProvider boundary is mocked.

## Version

2.0.0
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from providers.config import ProviderConfig
from providers.tron import TronProvider
from wallets.blockchain.base import BlockchainWallet
from wallets.blockchain.tron.wallet import TronWallet


###############################################################################
# Constants
###############################################################################

WALLET_ID = "tron-wallet-001"

VALID_ADDRESS = (
    "TQ9h9QW4Y9Q4mJ7"
    "2h3X8x9Q7v"
)

TRANSACTION_HASH = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)


###############################################################################
# Fixtures
###############################################################################

@pytest.fixture
def provider() -> TronProvider:
    """
    Return a mocked-configured TRON provider.
    """

    config = ProviderConfig(
        provider="tron",
        network="mainnet",
    )

    return TronProvider(config)


@pytest.fixture
def wallet(
    provider: TronProvider,
) -> TronWallet:
    """
    Return a test TRON wallet.
    """

    return TronWallet(
        wallet_id=WALLET_ID,
        address=VALID_ADDRESS,
        provider=provider,
    )


###############################################################################
# Construction
###############################################################################

def test_wallet_implements_blockchain_wallet(
    wallet: TronWallet,
) -> None:
    assert isinstance(
        wallet,
        BlockchainWallet,
    )


def test_wallet_identity(
    wallet: TronWallet,
) -> None:
    assert wallet.wallet_id == WALLET_ID
    assert wallet.blockchain == "tron"
    assert wallet.network == "mainnet"


def test_wallet_address(
    wallet: TronWallet,
) -> None:
    assert wallet.get_address() == VALID_ADDRESS
    assert wallet.address == VALID_ADDRESS


def test_wallet_provider(
    wallet: TronWallet,
) -> None:
    assert isinstance(
        wallet.provider,
        TronProvider,
    )


###############################################################################
# Construction Validation
###############################################################################

def test_empty_wallet_id_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(ValueError):
        TronWallet(
            wallet_id="",
            address=VALID_ADDRESS,
            provider=provider,
        )


def test_whitespace_wallet_id_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(ValueError):
        TronWallet(
            wallet_id="   ",
            address=VALID_ADDRESS,
            provider=provider,
        )


def test_empty_address_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(ValueError):
        TronWallet(
            wallet_id=WALLET_ID,
            address="",
            provider=provider,
        )


def test_whitespace_address_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(ValueError):
        TronWallet(
            wallet_id=WALLET_ID,
            address="   ",
            provider=provider,
        )


def test_invalid_wallet_id_type_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(TypeError):
        TronWallet(
            wallet_id=123,
            address=VALID_ADDRESS,
            provider=provider,
        )


def test_invalid_address_type_rejected(
    provider: TronProvider,
) -> None:
    with pytest.raises(TypeError):
        TronWallet(
            wallet_id=WALLET_ID,
            address=123,
            provider=provider,
        )


def test_invalid_provider_rejected() -> None:
    with pytest.raises(TypeError):
        TronWallet(
            wallet_id=WALLET_ID,
            address=VALID_ADDRESS,
            provider=MagicMock(),
        )


###############################################################################
# Balance
###############################################################################

def test_get_balance(
    wallet: TronWallet,
) -> None:
    wallet.provider.get_account = MagicMock(
        return_value={
            "address": VALID_ADDRESS,
            "balance": 2_500_000,
        }
    )

    balance = wallet.get_balance()

    assert balance["address"] == VALID_ADDRESS
    assert balance["asset"] == "TRX"
    assert balance["balance_sun"] == 2_500_000
    assert balance["balance"] == 2.5
    assert balance["network"] == "mainnet"


def test_zero_balance(
    wallet: TronWallet,
) -> None:
    wallet.provider.get_account = MagicMock(
        return_value={
            "address": VALID_ADDRESS,
        }
    )

    balance = wallet.get_balance()

    assert balance["balance_sun"] == 0
    assert balance["balance"] == 0.0


def test_balance_uses_wallet_address(
    wallet: TronWallet,
) -> None:
    wallet.provider.get_account = MagicMock(
        return_value={
            "balance": 1_000_000,
        }
    )

    wallet.get_balance()

    wallet.provider.get_account.assert_called_once_with(
        VALID_ADDRESS
    )


###############################################################################
# Latest Block
###############################################################################

def test_get_latest_block(
    wallet: TronWallet,
) -> None:
    expected = {
        "blockID": "abc123",
        "block_header": {
            "raw_data": {
                "number": 123456,
            }
        },
    }

    wallet.provider.get_latest_block = MagicMock(
        return_value=expected
    )

    result = wallet.get_latest_block()

    assert result == expected

    wallet.provider.get_latest_block.assert_called_once_with()


###############################################################################
# Status
###############################################################################

def test_get_status(
    wallet: TronWallet,
) -> None:
    wallet.provider.is_available = MagicMock(
        return_value=True
    )

    status = wallet.get_status()

    assert status["wallet_id"] == WALLET_ID
    assert status["blockchain"] == "tron"
    assert status["network"] == "mainnet"
    assert status["address"] == VALID_ADDRESS
    assert status["provider"] == "tron"
    assert status["provider_available"] is True


###############################################################################
# Transaction Preparation
###############################################################################

def test_prepare_transaction_returns_tron_payload(
    wallet: TronWallet,
) -> None:
    transaction = {
        "to_address": VALID_ADDRESS,
        "amount": 1_000_000,
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared["owner_address"] == VALID_ADDRESS
    assert prepared["to_address"] == VALID_ADDRESS
    assert prepared["amount"] == 1_000_000
    assert prepared["network"] == "mainnet"


def test_prepare_transaction_preserves_extra_fields(
    wallet: TronWallet,
) -> None:
    transaction = {
        "to_address": VALID_ADDRESS,
        "amount": 2_000_000,
        "permission_id": 2,
        "memo": "UBP test transaction",
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared["permission_id"] == 2
    assert prepared["memo"] == "UBP test transaction"


def test_prepare_transaction_returns_copy(
    wallet: TronWallet,
) -> None:
    transaction = {
        "owner_address": VALID_ADDRESS,
        "to_address": VALID_ADDRESS,
        "amount": 1_000_000,
    }

    original = dict(transaction)

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared is not transaction

    assert transaction == original

    assert prepared["owner_address"] == VALID_ADDRESS
    assert prepared["to_address"] == VALID_ADDRESS
    assert prepared["amount"] == 1_000_000
    assert prepared["network"] == "mainnet"


def test_prepare_transaction_accepts_explicit_owner(
    wallet: TronWallet,
) -> None:
    transaction = {
        "owner_address": VALID_ADDRESS,
        "to_address": VALID_ADDRESS,
        "amount": 1_000_000,
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared["owner_address"] == VALID_ADDRESS


def test_prepare_transaction_rejects_non_dict(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            "invalid"
        )


def test_prepare_transaction_requires_destination(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "amount": 1_000_000,
            }
        )


def test_prepare_transaction_rejects_empty_destination(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "to_address": "",
                "amount": 1_000_000,
            }
        )


def test_prepare_transaction_rejects_non_string_destination(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            {
                "to_address": 123,
                "amount": 1_000_000,
            }
        )


def test_prepare_transaction_requires_amount(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "to_address": VALID_ADDRESS,
            }
        )


def test_prepare_transaction_rejects_non_integer_amount(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            {
                "to_address": VALID_ADDRESS,
                "amount": 1.5,
            }
        )


def test_prepare_transaction_rejects_boolean_amount(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            {
                "to_address": VALID_ADDRESS,
                "amount": True,
            }
        )


def test_prepare_transaction_rejects_zero_amount(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "to_address": VALID_ADDRESS,
                "amount": 0,
            }
        )


def test_prepare_transaction_rejects_negative_amount(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "to_address": VALID_ADDRESS,
                "amount": -1,
            }
        )


def test_prepare_transaction_rejects_invalid_owner(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "owner_address": "TDIFFERENTADDRESS",
                "to_address": VALID_ADDRESS,
                "amount": 1_000_000,
            }
        )


def test_prepare_transaction_rejects_empty_owner(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.prepare_transaction(
            {
                "owner_address": "",
                "to_address": VALID_ADDRESS,
                "amount": 1_000_000,
            }
        )


def test_prepare_transaction_rejects_non_string_owner(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            {
                "owner_address": 123,
                "to_address": VALID_ADDRESS,
                "amount": 1_000_000,
            }
        )


###############################################################################
# Transaction Signing and Broadcasting
###############################################################################

def test_sign_transaction_not_implemented(
    wallet: TronWallet,
) -> None:
    with pytest.raises(
        NotImplementedError
    ):
        wallet.sign_transaction({})


def test_broadcast_transaction_not_implemented(
    wallet: TronWallet,
) -> None:
    with pytest.raises(
        NotImplementedError
    ):
        wallet.broadcast_transaction(
            "signed-transaction"
        )


###############################################################################
# Transaction Inspection
###############################################################################

def test_get_transaction(
    wallet: TronWallet,
) -> None:
    expected = {
        "txID": TRANSACTION_HASH,
        "raw_data": {
            "contract": [],
        },
    }

    wallet.provider.get_transaction = MagicMock(
        return_value=expected
    )

    result = wallet.get_transaction(
        TRANSACTION_HASH
    )

    assert result == expected

    wallet.provider.get_transaction.assert_called_once_with(
        TRANSACTION_HASH
    )


def test_get_transaction_rejects_non_string(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.get_transaction(123)


def test_get_transaction_rejects_empty_hash(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.get_transaction("")


def test_get_transaction_rejects_whitespace_hash(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.get_transaction("   ")


###############################################################################
# Transaction Status
###############################################################################

def test_get_transaction_status_confirmed(
    wallet: TronWallet,
) -> None:
    expected_info = {
        "id": TRANSACTION_HASH,
        "blockNumber": 123456,
        "fee": 2_000_000,
        "receipt": {
            "result": "SUCCESS",
        },
    }

    wallet.provider.get_transaction_info = MagicMock(
        return_value=expected_info
    )

    status = wallet.get_transaction_status(
        TRANSACTION_HASH
    )

    assert status["transaction_hash"] == TRANSACTION_HASH
    assert status["status"] == "CONFIRMED"
    assert status["confirmed"] is True
    assert status["result"] == "SUCCESS"
    assert status["block_number"] == 123456
    assert status["fee"] == 2_000_000
    assert status["raw"] == expected_info

    wallet.provider.get_transaction_info.assert_called_once_with(
        TRANSACTION_HASH
    )


def test_get_transaction_status_failed(
    wallet: TronWallet,
) -> None:
    expected_info = {
        "id": TRANSACTION_HASH,
        "blockNumber": 123456,
        "receipt": {
            "result": "OUT_OF_ENERGY",
        },
    }

    wallet.provider.get_transaction_info = MagicMock(
        return_value=expected_info
    )

    status = wallet.get_transaction_status(
        TRANSACTION_HASH
    )

    assert status["transaction_hash"] == TRANSACTION_HASH
    assert status["status"] == "FAILED"
    assert status["confirmed"] is False
    assert status["result"] == "OUT_OF_ENERGY"
    assert status["block_number"] == 123456
    assert status["raw"] == expected_info


def test_get_transaction_status_unknown(
    wallet: TronWallet,
) -> None:
    expected_info = {
        "id": TRANSACTION_HASH,
        "blockNumber": 123456,
        "receipt": {},
    }

    wallet.provider.get_transaction_info = MagicMock(
        return_value=expected_info
    )

    status = wallet.get_transaction_status(
        TRANSACTION_HASH
    )

    assert status["transaction_hash"] == TRANSACTION_HASH
    assert status["status"] == "UNKNOWN"
    assert status["confirmed"] is False
    assert status["result"] is None
    assert status["block_number"] == 123456
    assert status["raw"] == expected_info


def test_get_transaction_status_rejects_non_string(
    wallet: TronWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.get_transaction_status(123)


def test_get_transaction_status_rejects_empty_hash(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.get_transaction_status("")


def test_get_transaction_status_rejects_whitespace_hash(
    wallet: TronWallet,
) -> None:
    with pytest.raises(ValueError):
        wallet.get_transaction_status("   ")


###############################################################################
# Representation
###############################################################################

def test_repr(
    wallet: TronWallet,
) -> None:
    representation = repr(wallet)

    assert "TronWallet" in representation
    assert WALLET_ID in representation
    assert "tron" in representation
    assert "mainnet" in representation
    assert VALID_ADDRESS in representation