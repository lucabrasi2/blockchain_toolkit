


"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.blockchain.bitcoin.test_wallet

Purpose
-------
Tests for the UBP Bitcoin blockchain wallet.

No real Bitcoin network calls are performed.
The BitcoinProvider boundary is mocked.

Version
-------
2.0.0
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from wallets.custody.base import CustodyProvider
from wallets.custody.base import CustodyType
from providers.bitcoin import BitcoinProvider
from providers.config import ProviderConfig
from wallets.blockchain.base import BlockchainWallet
from wallets.blockchain.bitcoin.wallet import BitcoinWallet


###############################################################################
# Constants
###############################################################################

WALLET_ID = "bitcoin-wallet-001"

VALID_ADDRESS = (
    "bc1qexamplebitcoinwalletaddress"
)

TRANSACTION_HASH = (
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)


###############################################################################
# Dummy Custody Provider
###############################################################################


class DummyCustodyProvider(CustodyProvider):
    """
    Minimal custody implementation for Bitcoin wallet tests.

    This test provider deliberately keeps custody behavior simple while
    preserving the production architecture:

        BitcoinWallet
            |
            +-- CustodyProvider
                    |
                    +-- DummyCustodyProvider
    """

    def __init__(self) -> None:
        self._wallets: dict[str, bool] = {}

        self.sign_calls: list[
            tuple[str, dict[str, object]]
        ] = []

    @property
    def custody_type(self) -> str:
        """
        Return the custody model used by the test provider.
        """

        return CustodyType.NON_CUSTODIAL

    def create_wallet(
        self,
        **options: object,
    ) -> dict[str, object]:
        """
        Create a minimal test custody wallet record.
        """

        wallet_id = str(
            options.get(
                "wallet_id",
                "test-wallet",
            )
        )

        self._wallets[wallet_id] = False

        return {
            "wallet_id": wallet_id,
        }

    def import_wallet(
        self,
        **options: object,
    ) -> dict[str, object]:
        """
        Import a minimal test custody wallet record.
        """

        wallet_id = str(
            options.get(
                "wallet_id",
                "test-wallet",
            )
        )

        self._wallets[wallet_id] = False

        return {
            "wallet_id": wallet_id,
        }

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        """
        Delete a test custody wallet record.
        """

        self._wallets.pop(
            wallet_id,
            None,
        )

    def lock(
        self,
        wallet_id: str,
    ) -> None:
        """
        Lock a test wallet.
        """

        if wallet_id in self._wallets:
            self._wallets[wallet_id] = False

    def unlock(
        self,
        wallet_id: str,
        **credentials: object,
    ) -> bool:
        """
        Unlock a test wallet.
        """

        self._wallets[wallet_id] = True

        return True

    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        """
        Return the current test-wallet unlock state.
        """

        return self._wallets.get(
            wallet_id,
            False,
        )

    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict[str, object],
    ) -> str:
        """
        Record the signing request and return deterministic test output.
        """

        self.sign_calls.append(
            (
                wallet_id,
                dict(transaction),
            )
        )

        return "SIGNED_BITCOIN_TRANSACTION"

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        """
        Return a deterministic test public key.
        """

        return "TEST_PUBLIC_KEY"

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        """
        Return the deterministic test Bitcoin address.
        """

        return VALID_ADDRESS

    def get_status(
        self,
        wallet_id: str,
    ) -> dict[str, object]:
        """
        Return deterministic custody status.
        """

        return {
            "wallet_id": wallet_id,
            "unlocked": self.is_unlocked(
                wallet_id
            ),
        }


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def provider() -> BitcoinProvider:
    """
    Return a configured Bitcoin provider.

    The provider boundary is mocked during individual tests whenever
    blockchain communication is required.
    """

    config = ProviderConfig(
        provider="bitcoin",
        network="mainnet",
    )

    return BitcoinProvider(config)


@pytest.fixture
def custody() -> DummyCustodyProvider:
    """
    Return a dummy custody provider.
    """

    return DummyCustodyProvider()


@pytest.fixture
def wallet(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> BitcoinWallet:
    """
    Return a test Bitcoin wallet.
    """

    custody.create_wallet(
        wallet_id=WALLET_ID
    )

    return BitcoinWallet(
        wallet_id=WALLET_ID,
        address=VALID_ADDRESS,
        provider=provider,
        custody=custody,
    )


###############################################################################
# Construction
###############################################################################


def test_wallet_implements_blockchain_wallet(
    wallet: BitcoinWallet,
) -> None:
    assert isinstance(
        wallet,
        BlockchainWallet,
    )


def test_wallet_identity(
    wallet: BitcoinWallet,
) -> None:
    assert wallet.wallet_id == WALLET_ID
    assert wallet.blockchain == "bitcoin"
    assert wallet.network == "mainnet"


def test_wallet_address(
    wallet: BitcoinWallet,
) -> None:
    assert wallet.get_address() == VALID_ADDRESS
    assert wallet.address == VALID_ADDRESS


def test_wallet_provider(
    wallet: BitcoinWallet,
) -> None:
    assert isinstance(
        wallet.provider,
        BitcoinProvider,
    )


def test_wallet_custody(
    wallet: BitcoinWallet,
    custody: DummyCustodyProvider,
) -> None:
    assert wallet.custody is custody
    assert isinstance(
        wallet.custody,
        CustodyProvider,
    )


###############################################################################
# Construction Validation
###############################################################################


def test_empty_wallet_id_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(ValueError):
        BitcoinWallet(
            wallet_id="",
            address=VALID_ADDRESS,
            provider=provider,
            custody=custody,
        )


def test_whitespace_wallet_id_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(ValueError):
        BitcoinWallet(
            wallet_id="   ",
            address=VALID_ADDRESS,
            provider=provider,
            custody=custody,
        )


def test_empty_address_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(ValueError):
        BitcoinWallet(
            wallet_id=WALLET_ID,
            address="",
            provider=provider,
            custody=custody,
        )


def test_whitespace_address_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(ValueError):
        BitcoinWallet(
            wallet_id=WALLET_ID,
            address="   ",
            provider=provider,
            custody=custody,
        )


def test_invalid_wallet_id_type_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(TypeError):
        BitcoinWallet(
            wallet_id=123,
            address=VALID_ADDRESS,
            provider=provider,
            custody=custody,
        )


def test_invalid_address_type_rejected(
    provider: BitcoinProvider,
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(TypeError):
        BitcoinWallet(
            wallet_id=WALLET_ID,
            address=123,
            provider=provider,
            custody=custody,
        )


def test_invalid_provider_rejected(
    custody: DummyCustodyProvider,
) -> None:
    with pytest.raises(TypeError):
        BitcoinWallet(
            wallet_id=WALLET_ID,
            address=VALID_ADDRESS,
            provider=MagicMock(),
            custody=custody,
        )


def test_invalid_custody_rejected(
    provider: BitcoinProvider,
) -> None:
    with pytest.raises(TypeError):
        BitcoinWallet(
            wallet_id=WALLET_ID,
            address=VALID_ADDRESS,
            provider=provider,
            custody=MagicMock(),
        )


###############################################################################
# Balance
###############################################################################


def test_get_balance(
    wallet: BitcoinWallet,
) -> None:
    expected = {
        "address": VALID_ADDRESS,
        "asset": "BTC",
        "balance_btc": 1.25,
        "balance_sats": 125_000_000,
        "utxo_count": 2,
        "height": 850_000,
        "best_block": (
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ),
        "utxos": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
                "value_sats": 100_000_000,
                "value_btc": 1.0,
            },
            {
                "txid": (
                    "cccccccccccccccccccccccccccccccc"
                    "cccccccccccccccccccccccccccccccc"
                ),
                "vout": 1,
                "value_sats": 25_000_000,
                "value_btc": 0.25,
            },
        ],
    }

    wallet.provider.get_address_balance = MagicMock(
        return_value=expected
    )

    result = wallet.get_balance()

    assert result == expected

    wallet.provider.get_address_balance.assert_called_once_with(
        VALID_ADDRESS
    )


def test_get_balance_zero_balance(
    wallet: BitcoinWallet,
) -> None:
    expected = {
        "address": VALID_ADDRESS,
        "asset": "BTC",
        "balance_btc": 0.0,
        "balance_sats": 0,
        "utxo_count": 0,
        "height": 850_000,
        "best_block": (
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ),
        "utxos": [],
    }

    wallet.provider.get_address_balance = MagicMock(
        return_value=expected
    )

    result = wallet.get_balance()

    assert result["address"] == VALID_ADDRESS
    assert result["asset"] == "BTC"
    assert result["balance_btc"] == 0.0
    assert result["balance_sats"] == 0
    assert result["utxo_count"] == 0
    assert result["utxos"] == []

    wallet.provider.get_address_balance.assert_called_once_with(
        VALID_ADDRESS
    )


def test_get_balance_uses_wallet_address(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.get_address_balance = MagicMock(
        return_value={
            "address": VALID_ADDRESS,
            "asset": "BTC",
            "balance_btc": 0.5,
            "balance_sats": 50_000_000,
            "utxo_count": 1,
            "height": 850_000,
            "best_block": "abc123",
            "utxos": [],
        }
    )

    wallet.get_balance()

    wallet.provider.get_address_balance.assert_called_once_with(
        VALID_ADDRESS
    )


def test_get_balance_preserves_provider_result(
    wallet: BitcoinWallet,
) -> None:
    expected = {
        "address": VALID_ADDRESS,
        "asset": "BTC",
        "balance_btc": 2.5,
        "balance_sats": 250_000_000,
        "utxo_count": 3,
        "height": 850_000,
        "best_block": "abc123",
        "utxos": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
                "value_sats": 250_000_000,
                "value_btc": 2.5,
            }
        ],
    }

    wallet.provider.get_address_balance = MagicMock(
        return_value=expected
    )

    result = wallet.get_balance()

    assert result is expected


def test_get_balance_propagates_provider_error(
    wallet: BitcoinWallet,
) -> None:
    error = RuntimeError(
        "Bitcoin provider balance lookup failed."
    )

    wallet.provider.get_address_balance = MagicMock(
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match="Bitcoin provider balance lookup failed.",
    ):
        wallet.get_balance()

    wallet.provider.get_address_balance.assert_called_once_with(
        VALID_ADDRESS
    )


###############################################################################
# Transaction Preparation
###############################################################################


def test_prepare_transaction_returns_copy(
    wallet: BitcoinWallet,
) -> None:
    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
        "fee": 1_000,
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared == transaction
    assert prepared is not transaction


def test_prepare_transaction_does_not_modify_input(
    wallet: BitcoinWallet,
) -> None:
    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
    }

    original = dict(transaction)

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert transaction == original
    assert prepared == original


def test_prepare_transaction_accepts_empty_dict(
    wallet: BitcoinWallet,
) -> None:
    transaction = {}

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared == {}
    assert prepared is not transaction


def test_prepare_transaction_rejects_non_dict(
    wallet: BitcoinWallet,
) -> None:
    with pytest.raises(TypeError):
        wallet.prepare_transaction(
            "invalid"
        )


###############################################################################
# Transaction Construction
###############################################################################


def test_build_transaction_creates_and_funds_transaction(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify transaction construction delegates to the Bitcoin provider.
    """

    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
    }

    raw_transaction = "0200000001rawtransaction"

    funded_transaction = {
        "hex": "0200000001fundedtransaction",
        "fee": 0.00001,
        "changepos": 1,
    }

    wallet.provider.create_raw_transaction = MagicMock(
        return_value=raw_transaction
    )

    wallet.provider.fund_raw_transaction = MagicMock(
        return_value=funded_transaction
    )

    result = wallet.build_transaction(
        transaction
    )

    assert result == {
        "wallet_id": WALLET_ID,
        "blockchain": "bitcoin",
        "network": "mainnet",
        "hex": funded_transaction["hex"],
        "fee": funded_transaction["fee"],
        "changepos": funded_transaction["changepos"],
        "funded": True,
    }

    wallet.provider.create_raw_transaction.assert_called_once_with(
        transaction
    )

    wallet.provider.fund_raw_transaction.assert_called_once_with(
        raw_transaction,
        options=None,
    )


def test_build_transaction_forwards_funding_options(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify Bitcoin Core funding options are forwarded unchanged.
    """

    transaction = {
        "inputs": [],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 25_000,
            }
        ],
    }

    options = {
        "changeAddress": VALID_ADDRESS,
        "includeWatching": True,
        "lockUnspents": True,
    }

    raw_transaction = "0200000001rawtransaction"

    funded_transaction = {
        "hex": "0200000001fundedtransaction",
        "fee": 0.00002,
        "changepos": 0,
    }

    wallet.provider.create_raw_transaction = MagicMock(
        return_value=raw_transaction
    )

    wallet.provider.fund_raw_transaction = MagicMock(
        return_value=funded_transaction
    )

    result = wallet.build_transaction(
        transaction,
        options=options,
    )

    assert result["hex"] == funded_transaction["hex"]
    assert result["fee"] == funded_transaction["fee"]
    assert result["changepos"] == funded_transaction["changepos"]
    assert result["funded"] is True

    wallet.provider.create_raw_transaction.assert_called_once_with(
        transaction
    )

    wallet.provider.fund_raw_transaction.assert_called_once_with(
        raw_transaction,
        options=options,
    )


def test_build_transaction_does_not_modify_input(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify transaction construction does not modify the caller's input.
    """

    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
    }

    original = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
    }

    wallet.provider.create_raw_transaction = MagicMock(
        return_value="0200000001rawtransaction"
    )

    wallet.provider.fund_raw_transaction = MagicMock(
        return_value={
            "hex": "0200000001fundedtransaction",
            "fee": 0.00001,
            "changepos": -1,
        }
    )

    wallet.build_transaction(
        transaction
    )

    assert transaction == original


def test_build_transaction_rejects_non_dict_transaction(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify invalid transaction input is rejected.
    """

    with pytest.raises(
        TypeError,
        match="transaction must be a dictionary",
    ):
        wallet.build_transaction(
            "invalid"
        )


def test_build_transaction_rejects_non_dict_options(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify invalid funding options are rejected.
    """

    with pytest.raises(
        TypeError,
        match="options must be a dictionary",
    ):
        wallet.build_transaction(
            {},
            options="invalid",
        )


def test_build_transaction_rejects_invalid_raw_transaction(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify an invalid raw transaction returned by the provider is rejected.
    """

    wallet.provider.create_raw_transaction = MagicMock(
        return_value=""
    )

    wallet.provider.fund_raw_transaction = MagicMock()

    with pytest.raises(
        ValueError,
        match="empty raw transaction",
    ):
        wallet.build_transaction(
            {}
        )

    wallet.provider.fund_raw_transaction.assert_not_called()


def test_build_transaction_rejects_invalid_funded_transaction(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify an invalid funded transaction returned by the provider is rejected.
    """

    raw_transaction = "0200000001rawtransaction"

    wallet.provider.create_raw_transaction = MagicMock(
        return_value=raw_transaction
    )

    wallet.provider.fund_raw_transaction = MagicMock(
        return_value={
            "fee": 0.00001,
            "changepos": -1,
        }
    )

    with pytest.raises(
        ValueError,
        match="without valid hex",
    ):
        wallet.build_transaction(
            {}
        )

    wallet.provider.create_raw_transaction.assert_called_once_with(
        {}
    )

    wallet.provider.fund_raw_transaction.assert_called_once_with(
        raw_transaction,
        options=None,
    )


def test_build_transaction_propagates_provider_error(
    wallet: BitcoinWallet,
) -> None:
    """
    Verify provider construction errors are propagated.
    """

    error = RuntimeError(
        "Bitcoin transaction construction failed."
    )

    wallet.provider.create_raw_transaction = MagicMock(
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match="Bitcoin transaction construction failed.",
    ):
        wallet.build_transaction(
            {}
        )

    wallet.provider.create_raw_transaction.assert_called_once_with(
        {}
    )



###############################################################################
# Transaction Signing
###############################################################################


def test_sign_transaction_delegates_to_custody(
    wallet: BitcoinWallet,
    custody: DummyCustodyProvider,
) -> None:
    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
        "fee": 1_000,
    }

    result = wallet.sign_transaction(
        transaction
    )

    assert result == "SIGNED_BITCOIN_TRANSACTION"

    assert custody.sign_calls == [
        (
            WALLET_ID,
            transaction,
        )
    ]


def test_sign_transaction_does_not_modify_input(
    wallet: BitcoinWallet,
    custody: DummyCustodyProvider,
) -> None:
    transaction = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
        "fee": 1_000,
    }

    original = {
        "inputs": [
            {
                "txid": TRANSACTION_HASH,
                "vout": 0,
            }
        ],
        "outputs": [
            {
                "address": VALID_ADDRESS,
                "amount": 50_000,
            }
        ],
        "fee": 1_000,
    }

    wallet.sign_transaction(
        transaction
    )

    assert transaction == original

    assert custody.sign_calls[0] == (
        WALLET_ID,
        original,
    )


def test_sign_transaction_propagates_custody_error(
    wallet: BitcoinWallet,
    custody: DummyCustodyProvider,
) -> None:
    error = RuntimeError(
        "Bitcoin custody signing failed."
    )

    custody.sign_transaction = MagicMock(
        side_effect=error
    )

    with pytest.raises(
        RuntimeError,
        match="Bitcoin custody signing failed.",
    ):
        wallet.sign_transaction(
            {
                "inputs": [],
                "outputs": [],
            }
        )

    custody.sign_transaction.assert_called_once_with(
        WALLET_ID,
        {
            "inputs": [],
            "outputs": [],
        },
    )


###############################################################################
# Transaction Broadcasting
###############################################################################


def test_broadcast_transaction(
    wallet: BitcoinWallet,
) -> None:
    signed_transaction = (
        "0200000001"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "00000000"
    )

    transaction_hash = (
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    )

    wallet.provider.send_raw_transaction = MagicMock(
        return_value=transaction_hash
    )

    result = wallet.broadcast_transaction(
        signed_transaction
    )

    assert (
        result["wallet_id"]
        == WALLET_ID
    )

    assert (
        result["blockchain"]
        == "bitcoin"
    )

    assert (
        result["network"]
        == "mainnet"
    )

    assert (
        result["transaction_hash"]
        == transaction_hash
    )

    assert (
        result["status"]
        == "broadcast"
    )

    assert (
        result["broadcast"]
        is True
    )

    wallet.provider.send_raw_transaction.assert_called_once_with(
        signed_transaction
    )


###############################################################################
# Transaction Inspection
###############################################################################


def test_get_transaction(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.get_transaction = MagicMock(
        return_value={
            "txid": TRANSACTION_HASH,
            "confirmations": 3,
        }
    )

    result = wallet.get_transaction(
        TRANSACTION_HASH
    )

    assert result["txid"] == TRANSACTION_HASH
    assert result["confirmations"] == 3

    wallet.provider.get_transaction.assert_called_once_with(
        TRANSACTION_HASH
    )


###############################################################################
# Transaction Status
###############################################################################


def test_get_transaction_status(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.get_transaction = MagicMock(
        return_value={
            "txid": TRANSACTION_HASH,
            "confirmations": 3,
        }
    )

    result = wallet.get_transaction_status(
        TRANSACTION_HASH
    )

    assert (
        result["transaction_hash"]
        == TRANSACTION_HASH
    )

    assert (
        result["status"]
        == "confirmed"
    )

    assert (
        result["confirmed"]
        is True
    )

    assert (
        result["confirmations"]
        == 3
    )

    wallet.provider.get_transaction.assert_called_once_with(
        TRANSACTION_HASH
    )


###############################################################################
# Latest Block
###############################################################################


def test_get_latest_block(
    wallet: BitcoinWallet,
) -> None:
    blockchain_info = {
        "chain": "main",
        "blocks": 850_000,
        "headers": 850_000,
        "bestblockhash": (
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ),
    }

    wallet.provider.get_blockchain_info = MagicMock(
        return_value=blockchain_info
    )

    wallet.provider.get_block_count = MagicMock(
        return_value=850_000
    )

    result = wallet.get_latest_block()

    assert result["blockchain"] == "bitcoin"
    assert result["network"] == "mainnet"
    assert result["height"] == 850_000

    assert result["best_block_hash"] == (
        blockchain_info["bestblockhash"]
    )

    assert result["chain"] == "main"
    assert result["headers"] == 850_000
    assert result["blocks"] == 850_000

    wallet.provider.get_blockchain_info.assert_called_once_with()
    wallet.provider.get_block_count.assert_called_once_with()


def test_get_latest_block_uses_provider_state(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.get_blockchain_info = MagicMock(
        return_value={
            "chain": "test",
            "blocks": 100,
            "headers": 101,
            "bestblockhash": "abc123",
        }
    )

    wallet.provider.get_block_count = MagicMock(
        return_value=100
    )

    result = wallet.get_latest_block()

    assert result["height"] == 100
    assert result["chain"] == "test"
    assert result["headers"] == 101
    assert result["best_block_hash"] == "abc123"


def test_get_latest_block_handles_missing_optional_fields(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.get_blockchain_info = MagicMock(
        return_value={}
    )

    wallet.provider.get_block_count = MagicMock(
        return_value=0
    )

    result = wallet.get_latest_block()

    assert result["blockchain"] == "bitcoin"
    assert result["network"] == "mainnet"
    assert result["height"] == 0
    assert result["best_block_hash"] is None
    assert result["chain"] is None
    assert result["headers"] is None
    assert result["blocks"] is None


###############################################################################
# Wallet Status
###############################################################################


def test_get_status(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.is_connected = MagicMock(
        return_value=True
    )

    status = wallet.get_status()

    assert status["wallet_id"] == WALLET_ID
    assert status["blockchain"] == "bitcoin"
    assert status["network"] == "mainnet"
    assert status["address"] == VALID_ADDRESS
    assert status["provider"] == wallet.provider.name
    assert status["provider_connected"] is True
    assert status["provider_available"] is True


def test_get_status_when_provider_disconnected(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.is_connected = MagicMock(
        return_value=False
    )

    status = wallet.get_status()

    assert status["wallet_id"] == WALLET_ID
    assert status["blockchain"] == "bitcoin"
    assert status["network"] == "mainnet"
    assert status["address"] == VALID_ADDRESS
    assert status["provider_connected"] is False
    assert status["provider_available"] is False


def test_get_status_checks_provider_connection(
    wallet: BitcoinWallet,
) -> None:
    wallet.provider.is_connected = MagicMock(
        return_value=True
    )

    wallet.get_status()

    assert (
        wallet.provider.is_connected.call_count
        == 1
    )


###############################################################################
# Representation
###############################################################################


def test_repr(
    wallet: BitcoinWallet,
) -> None:
    representation = repr(wallet)

    assert "BitcoinWallet" in representation
    assert WALLET_ID in representation
    assert "bitcoin" in representation
    assert "mainnet" in representation
    assert VALID_ADDRESS in representation