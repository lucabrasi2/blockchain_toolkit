"""
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.test_blockchain_base

Purpose
-------
Tests for the abstract blockchain-wallet interface.

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

import pytest

from wallets.blockchain.base import BlockchainWallet


###############################################################################
# Test Implementation
###############################################################################


class DummyBlockchainWallet(BlockchainWallet):
    """
    Minimal concrete implementation used only to test the abstract
    BlockchainWallet contract.

    No real blockchain communication is performed.
    """

    def __init__(
        self,
        wallet_id: str = "wallet-001",
        blockchain: str = "testchain",
        network: str = "testnet",
    ) -> None:
        self._wallet_id = wallet_id
        self._blockchain = blockchain
        self._network = network

    @property
    def blockchain(self) -> str:
        """Return blockchain identifier."""
        return self._blockchain

    @property
    def network(self) -> str:
        """Return network identifier."""
        return self._network

    @property
    def wallet_id(self) -> str:
        """Return wallet identifier."""
        return self._wallet_id

    def get_address(self) -> str:
        """Return test blockchain address."""
        return "TEST_ADDRESS"

    def get_balance(self) -> dict[str, object]:
        """Return test balance."""
        return {
            "native": 100,
            "symbol": "TEST",
        }

    def prepare_transaction(
        self,
        transaction: dict[str, object],
    ) -> dict[str, object]:
        """Return a prepared test transaction."""
        return {
            **transaction,
            "prepared": True,
        }

    def sign_transaction(
        self,
        transaction: dict[str, object],
    ) -> str:
        """Return a dummy signed transaction."""
        return "SIGNED_TRANSACTION"

    def broadcast_transaction(
        self,
        signed_transaction: str,
    ) -> dict[str, object]:
        """Return a dummy broadcast result."""
        return {
            "success": True,
            "transaction_hash": "TEST_TX_HASH",
            "signed_transaction": signed_transaction,
        }

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, object]:
        """Return a dummy transaction."""
        return {
            "hash": transaction_hash,
            "status": "confirmed",
        }

    def get_transaction_status(
        self,
        transaction_hash: str,
    ) -> dict[str, object]:
        """Return a dummy transaction status."""
        return {
            "hash": transaction_hash,
            "status": "confirmed",
        }

    def get_latest_block(self) -> dict[str, object]:
        """Return a dummy latest block."""
        return {
            "number": 100,
            "hash": "TEST_BLOCK_HASH",
        }

    def get_status(self) -> dict[str, object]:
        """Return a dummy wallet status."""
        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "status": "READY",
        }


###############################################################################
# Abstract Interface Tests
###############################################################################


def test_blockchain_wallet_is_abstract() -> None:
    """
    Verify BlockchainWallet cannot be instantiated directly.
    """

    with pytest.raises(TypeError):
        BlockchainWallet()


def test_dummy_wallet_implements_interface() -> None:
    """
    Verify a concrete implementation satisfies the abstract interface.
    """

    wallet = DummyBlockchainWallet()

    assert isinstance(
        wallet,
        BlockchainWallet,
    )


###############################################################################
# Identity Tests
###############################################################################


def test_blockchain_identity() -> None:
    """
    Verify blockchain identity.
    """

    wallet = DummyBlockchainWallet(
        blockchain="testchain"
    )

    assert (
        wallet.blockchain
        == "testchain"
    )


def test_network_identity() -> None:
    """
    Verify network identity.
    """

    wallet = DummyBlockchainWallet(
        network="testnet"
    )

    assert (
        wallet.network
        == "testnet"
    )


def test_wallet_identity() -> None:
    """
    Verify UBP wallet identity.
    """

    wallet = DummyBlockchainWallet(
        wallet_id="wallet-123"
    )

    assert (
        wallet.wallet_id
        == "wallet-123"
    )


###############################################################################
# Address Tests
###############################################################################


def test_get_address() -> None:
    """
    Verify the common address interface.
    """

    wallet = DummyBlockchainWallet()

    assert (
        wallet.get_address()
        == "TEST_ADDRESS"
    )


###############################################################################
# Balance Tests
###############################################################################


def test_get_balance() -> None:
    """
    Verify the common balance interface.
    """

    wallet = DummyBlockchainWallet()

    balance = wallet.get_balance()

    assert isinstance(
        balance,
        dict,
    )

    assert (
        balance["native"]
        == 100
    )

    assert (
        balance["symbol"]
        == "TEST"
    )


###############################################################################
# Transaction Preparation Tests
###############################################################################


def test_prepare_transaction() -> None:
    """
    Verify transaction preparation.
    """

    wallet = DummyBlockchainWallet()

    transaction = {
        "to": "TEST_RECIPIENT",
        "amount": 10,
    }

    prepared = wallet.prepare_transaction(
        transaction
    )

    assert (
        prepared["to"]
        == "TEST_RECIPIENT"
    )

    assert (
        prepared["amount"]
        == 10
    )

    assert (
        prepared["prepared"]
        is True
    )


###############################################################################
# Transaction Signing Tests
###############################################################################


def test_sign_transaction() -> None:
    """
    Verify the common transaction-signing interface.
    """

    wallet = DummyBlockchainWallet()

    signed = wallet.sign_transaction(
        {
            "to": "TEST_RECIPIENT",
            "amount": 10,
        }
    )

    assert isinstance(
        signed,
        str,
    )

    assert (
        signed
        == "SIGNED_TRANSACTION"
    )


###############################################################################
# Transaction Broadcasting Tests
###############################################################################


def test_broadcast_transaction() -> None:
    """
    Verify transaction broadcasting.
    """

    wallet = DummyBlockchainWallet()

    result = wallet.broadcast_transaction(
        "SIGNED_TRANSACTION"
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result["success"]
        is True
    )

    assert (
        result["transaction_hash"]
        == "TEST_TX_HASH"
    )


###############################################################################
# Transaction Inspection Tests
###############################################################################


def test_get_transaction() -> None:
    """
    Verify transaction retrieval.
    """

    wallet = DummyBlockchainWallet()

    result = wallet.get_transaction(
        "TEST_TX_HASH"
    )

    assert (
        result["hash"]
        == "TEST_TX_HASH"
    )

    assert (
        result["status"]
        == "confirmed"
    )


def test_get_transaction_status() -> None:
    """
    Verify transaction status retrieval.
    """

    wallet = DummyBlockchainWallet()

    result = wallet.get_transaction_status(
        "TEST_TX_HASH"
    )

    assert (
        result["hash"]
        == "TEST_TX_HASH"
    )

    assert (
        result["status"]
        == "confirmed"
    )


###############################################################################
# Blockchain State Tests
###############################################################################


def test_get_latest_block() -> None:
    """
    Verify latest-block retrieval.
    """

    wallet = DummyBlockchainWallet()

    result = wallet.get_latest_block()

    assert (
        result["number"]
        == 100
    )

    assert (
        result["hash"]
        == "TEST_BLOCK_HASH"
    )


###############################################################################
# Wallet Status Tests
###############################################################################


def test_get_status() -> None:
    """
    Verify wallet status reporting.
    """

    wallet = DummyBlockchainWallet(
        wallet_id="status-wallet",
        blockchain="testchain",
        network="testnet",
    )

    status = wallet.get_status()

    assert (
        status["wallet_id"]
        == "status-wallet"
    )

    assert (
        status["blockchain"]
        == "testchain"
    )

    assert (
        status["network"]
        == "testnet"
    )

    assert (
        status["status"]
        == "READY"
    )


###############################################################################
# Representation Tests
###############################################################################


def test_wallet_repr() -> None:
    """
    Verify developer representation.
    """

    wallet = DummyBlockchainWallet(
        wallet_id="wallet-001",
        blockchain="testchain",
        network="testnet",
    )

    representation = repr(wallet)

    assert (
        "DummyBlockchainWallet"
        in representation
    )

    assert (
        "wallet-001"
        in representation
    )

    assert (
        "testchain"
        in representation
    )

    assert (
        "testnet"
        in representation
    )


###############################################################################
# Interface Completeness
###############################################################################


def test_interface_methods_exist() -> None:
    """
    Verify all required public methods exist on the abstraction.
    """

    required_methods = [
        "get_address",
        "get_balance",
        "prepare_transaction",
        "sign_transaction",
        "broadcast_transaction",
        "get_transaction",
        "get_transaction_status",
        "get_latest_block",
        "get_status",
    ]

    for method_name in required_methods:
        assert hasattr(
            BlockchainWallet,
            method_name,
        )


###############################################################################
# End of File
###############################################################################
