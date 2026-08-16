"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.blockchain.ethereum.test_wallet

Purpose
-------
Tests for the UBP Ethereum blockchain wallet.

The tests use mocked provider and custody boundaries.
No real Ethereum RPC calls are performed.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from providers.base import BaseProvider
from wallets.blockchain.base import BlockchainWallet
from wallets.blockchain.ethereum.wallet import EthereumWallet
from wallets.custody.base import CustodyProvider
from wallets.custody.base import CustodyType


###############################################################################
# Constants
###############################################################################


VALID_ADDRESS = (
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
)

VALID_RECIPIENT = (
    "0x0000000000000000000000000000000000000001"
)

VALID_TRANSACTION_HASH = (
    "0x"
    "1111111111111111111111111111111111111111111111111111111111111111"
)


###############################################################################
# Dummy Ethereum Provider
###############################################################################


class DummyEthereumProvider(BaseProvider):
    """
    Minimal concrete Ethereum provider for unit testing.

    No real RPC connection is performed.
    """

    @property
    def name(self) -> str:
        return "test-ethereum"

    @property
    def blockchain(self) -> str:
        return "ethereum"

    @property
    def network(self) -> str:
        return "testnet"

    @property
    def provider_type(self) -> str:
        return "test"

    @property
    def http_url(self) -> str:
        return "http://test.ethereum.local"

    @property
    def ws_url(self) -> str:
        return "ws://test.ethereum.local"

    def get_config(self) -> dict[str, object]:
        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "http_url": self.http_url,
            "ws_url": self.ws_url,
        }

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def is_connected(self) -> bool:
        return True


###############################################################################
# Dummy Custody Provider
###############################################################################


class DummyCustodyProvider(CustodyProvider):
    """
    Minimal custody implementation for Ethereum wallet tests.
    """

    def __init__(self) -> None:
        self._wallets: dict[str, bool] = {}
        self.sign_calls: list[
            tuple[str, dict[str, object]]
        ] = []

    @property
    def custody_type(self) -> str:
        return CustodyType.NON_CUSTODIAL

    def create_wallet(
        self,
        **options: object,
    ) -> dict[str, object]:
        wallet_id = str(
            options.get(
                "wallet_id",
                "test-wallet",
            )
        )

        self._wallets[
            wallet_id
        ] = False

        return {
            "wallet_id": wallet_id,
        }

    def import_wallet(
        self,
        **options: object,
    ) -> dict[str, object]:
        wallet_id = str(
            options.get(
                "wallet_id",
                "test-wallet",
            )
        )

        self._wallets[
            wallet_id
        ] = False

        return {
            "wallet_id": wallet_id,
        }

    def delete_wallet(
        self,
        wallet_id: str,
    ) -> None:
        self._wallets.pop(
            wallet_id,
            None,
        )

    def lock(
        self,
        wallet_id: str,
    ) -> None:
        if wallet_id in self._wallets:
            self._wallets[
                wallet_id
            ] = False

    def unlock(
        self,
        wallet_id: str,
        **credentials: object,
    ) -> bool:
        self._wallets[
            wallet_id
        ] = True

        return True

    def is_unlocked(
        self,
        wallet_id: str,
    ) -> bool:
        return self._wallets.get(
            wallet_id,
            False,
        )

    def sign_transaction(
        self,
        wallet_id: str,
        transaction: dict[str, object],
    ) -> str:
        self.sign_calls.append(
            (
                wallet_id,
                dict(transaction),
            )
        )

        return "SIGNED_ETHEREUM_TRANSACTION"

    def get_public_key(
        self,
        wallet_id: str,
    ) -> str:
        return "TEST_PUBLIC_KEY"

    def get_address(
        self,
        wallet_id: str,
        blockchain: str,
    ) -> str:
        return VALID_ADDRESS

    def get_status(
        self,
        wallet_id: str,
    ) -> dict[str, object]:
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
def provider() -> DummyEthereumProvider:
    """
    Return a dummy Ethereum provider.
    """

    return DummyEthereumProvider()


@pytest.fixture
def custody() -> DummyCustodyProvider:
    """
    Return a dummy custody provider.
    """

    return DummyCustodyProvider()


@pytest.fixture
def wallet(
    provider: DummyEthereumProvider,
    custody: DummyCustodyProvider,
) -> EthereumWallet:
    """
    Return a test Ethereum wallet.
    """

    custody.create_wallet(
        wallet_id="wallet-001"
    )

    return EthereumWallet(
        wallet_id="wallet-001",
        address=VALID_ADDRESS,
        provider=provider,
        custody=custody,
    )


###############################################################################
# Construction
###############################################################################


def test_wallet_is_blockchain_wallet(
    wallet: EthereumWallet,
) -> None:
    """
    Verify the Ethereum wallet satisfies the common abstraction.
    """

    assert isinstance(
        wallet,
        BlockchainWallet,
    )


def test_wallet_identity(
    wallet: EthereumWallet,
) -> None:
    """
    Verify wallet identity properties.
    """

    assert wallet.wallet_id == "wallet-001"
    assert wallet.blockchain == "ethereum"
    assert wallet.network == "testnet"


def test_wallet_address_is_checksum_address(
    wallet: EthereumWallet,
) -> None:
    """
    Verify the wallet exposes its Ethereum address.
    """

    assert wallet.get_address() == VALID_ADDRESS


def test_wallet_provider_property(
    wallet: EthereumWallet,
    provider: DummyEthereumProvider,
) -> None:
    """
    Verify provider access.
    """

    assert wallet.provider is provider


def test_wallet_custody_property(
    wallet: EthereumWallet,
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify custody access.
    """

    assert wallet.custody is custody


###############################################################################
# Construction Validation
###############################################################################


def test_empty_wallet_id_rejected(
    provider: DummyEthereumProvider,
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify empty wallet IDs are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Wallet ID cannot be empty",
    ):
        EthereumWallet(
            wallet_id="",
            address=VALID_ADDRESS,
            provider=provider,
            custody=custody,
        )


def test_invalid_address_rejected(
    provider: DummyEthereumProvider,
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify invalid Ethereum addresses are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Invalid Ethereum wallet address",
    ):
        EthereumWallet(
            wallet_id="wallet-001",
            address="invalid-address",
            provider=provider,
            custody=custody,
        )


def test_invalid_provider_rejected(
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify a non-provider object is rejected.
    """

    with pytest.raises(
        TypeError,
        match="Provider must be a BaseProvider",
    ):
        EthereumWallet(
            wallet_id="wallet-001",
            address=VALID_ADDRESS,
            provider=MagicMock(),
            custody=custody,
        )


def test_invalid_custody_rejected(
    provider: DummyEthereumProvider,
) -> None:
    """
    Verify a non-custody object is rejected.
    """

    with pytest.raises(
        TypeError,
        match="Custody must be a CustodyProvider",
    ):
        EthereumWallet(
            wallet_id="wallet-001",
            address=VALID_ADDRESS,
            provider=provider,
            custody=MagicMock(),
        )


def test_non_ethereum_provider_rejected(
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify an Ethereum wallet cannot use another blockchain provider.
    """

    provider = MagicMock(
        spec=BaseProvider
    )

    provider.blockchain = "bitcoin"

    with pytest.raises(
        ValueError,
        match="requires an Ethereum provider",
    ):
        EthereumWallet(
            wallet_id="wallet-001",
            address=VALID_ADDRESS,
            provider=provider,
            custody=custody,
        )


###############################################################################
# Web3 Access
###############################################################################


def test_web3_property(
    wallet: EthereumWallet,
) -> None:
    """
    Verify Web3 access is delegated to the provider.
    """

    mock_web3 = MagicMock()

    wallet.provider._web3 = mock_web3

    assert wallet.web3 is mock_web3


###############################################################################
# Balance
###############################################################################


def test_get_balance(
    wallet: EthereumWallet,
) -> None:
    """
    Verify Ethereum balance retrieval.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_balance.return_value = (
        1_500_000_000_000_000_000
    )

    mock_web3.from_wei.return_value = 1.5

    wallet.provider._web3 = mock_web3

    result = wallet.get_balance()

    assert result["wallet_id"] == "wallet-001"
    assert result["address"] == VALID_ADDRESS
    assert result["blockchain"] == "ethereum"
    assert result["asset"] == "ETH"
    assert (
        result["balance_wei"]
        == 1_500_000_000_000_000_000
    )
    assert result["balance_eth"] == 1.5

    mock_web3.eth.get_balance.assert_called_once_with(
        VALID_ADDRESS
    )


###############################################################################
# Transaction Preparation
###############################################################################


def test_prepare_transaction(
    wallet: EthereumWallet,
) -> None:
    """
    Verify basic Ethereum transaction preparation.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_transaction_count.return_value = 7
    mock_web3.eth.chain_id = 11155111
    mock_web3.eth.estimate_gas.return_value = 21000
    mock_web3.eth.gas_price = 20_000_000_000

    wallet.provider._web3 = mock_web3

    transaction = {
        "to": VALID_RECIPIENT,
        "value": 1000,
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert prepared["from"] == VALID_ADDRESS
    assert prepared["to"] == VALID_RECIPIENT
    assert prepared["value"] == 1000
    assert prepared["nonce"] == 7
    assert prepared["chainId"] == 11155111
    assert prepared["gas"] == 21000


def test_prepare_transaction_requires_dictionary(
    wallet: EthereumWallet,
) -> None:
    """
    Verify transaction preparation requires a dictionary.
    """

    with pytest.raises(
        TypeError,
        match="Transaction must be a dictionary",
    ):
        wallet.prepare_transaction(
            "invalid"
        )


def test_invalid_recipient_rejected(
    wallet: EthereumWallet,
) -> None:
    """
    Verify invalid Ethereum recipients are rejected.
    """

    with pytest.raises(
        ValueError,
        match="Invalid Ethereum recipient",
    ):
        wallet.prepare_transaction(
            {
                "to": "invalid",
                "value": 1,
            }
        )


def test_negative_value_rejected(
    wallet: EthereumWallet,
) -> None:
    """
    Verify negative transaction values are rejected.
    """

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        wallet.prepare_transaction(
            {
                "to": VALID_RECIPIENT,
                "value": -1,
            }
        )


###############################################################################
# Signing
###############################################################################


def test_sign_transaction_delegates_to_custody(
    wallet: EthereumWallet,
    custody: DummyCustodyProvider,
) -> None:
    """
    Verify Ethereum signing is delegated to custody.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_transaction_count.return_value = 1
    mock_web3.eth.chain_id = 11155111
    mock_web3.eth.estimate_gas.return_value = 21000
    mock_web3.eth.gas_price = 20_000_000_000

    wallet.provider._web3 = mock_web3

    result = wallet.sign_transaction(
        {
            "to": VALID_RECIPIENT,
            "value": 100,
        }
    )

    assert (
        result
        == "SIGNED_ETHEREUM_TRANSACTION"
    )

    assert len(
        custody.sign_calls
    ) == 1

    wallet_id, transaction = (
        custody.sign_calls[0]
    )

    assert wallet_id == "wallet-001"
    assert transaction["from"] == VALID_ADDRESS
    assert transaction["to"] == VALID_RECIPIENT


###############################################################################
# Broadcasting
###############################################################################


def test_broadcast_transaction(
    wallet: EthereumWallet,
) -> None:
    """
    Verify signed Ethereum transactions are broadcast.
    """

    mock_web3 = MagicMock()

    mock_hash = MagicMock()

    mock_hash.hex.return_value = (
        VALID_TRANSACTION_HASH
    )

    mock_web3.eth.send_raw_transaction.return_value = (
        mock_hash
    )

    wallet.provider._web3 = mock_web3

    result = wallet.broadcast_transaction(
        "SIGNED_ETHEREUM_TRANSACTION"
    )

    assert result["success"] is True

    assert (
        result["transaction_hash"]
        == VALID_TRANSACTION_HASH
    )

    mock_web3.eth.send_raw_transaction.assert_called_once_with(
        "SIGNED_ETHEREUM_TRANSACTION"
    )


def test_empty_signed_transaction_rejected(
    wallet: EthereumWallet,
) -> None:
    """
    Verify empty signed transactions are rejected.
    """

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        wallet.broadcast_transaction("")


###############################################################################
# Transaction Retrieval
###############################################################################


def test_get_transaction(
    wallet: EthereumWallet,
) -> None:
    """
    Verify Ethereum transaction retrieval.
    """

    mock_web3 = MagicMock()

    mock_transaction = {
        "hash": VALID_TRANSACTION_HASH,
        "from": VALID_ADDRESS,
        "to": VALID_RECIPIENT,
        "value": 100,
    }

    mock_web3.eth.get_transaction.return_value = (
        mock_transaction
    )

    wallet.provider._web3 = mock_web3

    result = wallet.get_transaction(
        VALID_TRANSACTION_HASH
    )

    assert result["wallet_id"] == "wallet-001"
    assert (
        result["transaction"]
        == mock_transaction
    )


###############################################################################
# Transaction Status
###############################################################################


def test_confirmed_transaction_status(
    wallet: EthereumWallet,
) -> None:
    """
    Verify a successful Ethereum transaction receipt.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_transaction_receipt.return_value = {
        "status": 1,
        "blockNumber": 100,
    }

    wallet.provider._web3 = mock_web3

    result = wallet.get_transaction_status(
        VALID_TRANSACTION_HASH
    )

    assert result["status"] == "confirmed"
    assert result["confirmed"] is True


def test_failed_transaction_status(
    wallet: EthereumWallet,
) -> None:
    """
    Verify a failed Ethereum transaction receipt.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_transaction_receipt.return_value = {
        "status": 0,
        "blockNumber": 100,
    }

    wallet.provider._web3 = mock_web3

    result = wallet.get_transaction_status(
        VALID_TRANSACTION_HASH
    )

    assert result["status"] == "failed"
    assert result["confirmed"] is True


def test_pending_transaction_status(
    wallet: EthereumWallet,
) -> None:
    """
    Verify an unavailable receipt is reported as pending.
    """

    mock_web3 = MagicMock()

    mock_web3.eth.get_transaction_receipt.side_effect = (
        Exception("transaction not mined")
    )

    wallet.provider._web3 = mock_web3

    result = wallet.get_transaction_status(
        VALID_TRANSACTION_HASH
    )

    assert result["status"] == "pending"
    assert result["confirmed"] is False


###############################################################################
# Latest Block
###############################################################################


def test_get_latest_block(
    wallet: EthereumWallet,
) -> None:
    """
    Verify latest Ethereum block retrieval.
    """

    mock_web3 = MagicMock()

    mock_block_hash = MagicMock()

    mock_block_hash.hex.return_value = (
        "0x"
        "2222222222222222222222222222222222222222222222222222222222222222"
    )

    mock_web3.eth.get_block.return_value = {
        "number": 12345,
        "hash": mock_block_hash,
        "timestamp": 1700000000,
        "transactions": [
            "tx1",
            "tx2",
        ],
    }

    wallet.provider._web3 = mock_web3

    result = wallet.get_latest_block()

    assert result["blockchain"] == "ethereum"
    assert result["network"] == "testnet"
    assert result["number"] == 12345
    assert result["transaction_count"] == 2


###############################################################################
# Wallet Status
###############################################################################


def test_wallet_status(
    wallet: EthereumWallet,
) -> None:
    """
    Verify Ethereum wallet status.
    """

    mock_web3 = MagicMock()

    mock_web3.is_connected.return_value = True

    wallet.provider._web3 = mock_web3

    result = wallet.get_status()

    assert result["wallet_id"] == "wallet-001"
    assert result["blockchain"] == "ethereum"
    assert result["network"] == "testnet"
    assert result["provider"] == "test-ethereum"
    assert result["provider_connected"] is True
    assert (
        result["custody_type"]
        == CustodyType.NON_CUSTODIAL
    )
    assert result["status"] == "READY"


###############################################################################
# Representation
###############################################################################


def test_repr(
    wallet: EthereumWallet,
) -> None:
    """
    Verify developer representation.
    """

    representation = repr(wallet)

    assert "EthereumWallet" in representation
    assert "wallet-001" in representation
    assert "testnet" in representation


def test_str(
    wallet: EthereumWallet,
) -> None:
    """
    Verify human-readable representation.
    """

    representation = str(wallet)

    assert "Ethereum wallet" in representation
    assert "wallet-001" in representation


###############################################################################
# End of File
###############################################################################