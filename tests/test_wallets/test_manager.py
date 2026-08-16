"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_wallets.test_manager

Purpose
-------
Unit tests for WalletManager.

These tests verify that the wallet manager correctly orchestrates the
wallet subsystem.

Step 4 — Type Contract Verification

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from wallets.manager import WalletManager
from wallets.wallet import Wallet
from wallets.storage import WalletStorage
from wallets.validators import WalletValidator
from wallets.encryption import EncryptionManager


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def storage(tmp_path: Path) -> WalletStorage:
    """
    Temporary wallet storage.
    """

    return WalletStorage(
        storage_path=str(tmp_path),
    )


@pytest.fixture
def manager(
    storage: WalletStorage,
) -> WalletManager:
    """
    Wallet manager fixture.
    """

    return WalletManager(
        storage=storage,
        validator=WalletValidator(),
        encryption=EncryptionManager(),
    )


###############################################################################
# Initialization
###############################################################################


def test_manager_initialization(
    manager: WalletManager,
):
    """
    Manager initializes correctly.
    """

    assert isinstance(
        manager.storage,
        WalletStorage,
    )

    assert isinstance(
        manager.validator,
        WalletValidator,
    )

    assert isinstance(
        manager.encryption,
        EncryptionManager,
    )


###############################################################################
# Wallet Creation
###############################################################################


def test_create_wallet(
    manager: WalletManager,
):
    """
    Wallet creation succeeds.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-001",
        address="0x123456789ABCDEF",
        network="ethereum",
    )

    assert isinstance(
        wallet,
        Wallet,
    )

    assert wallet.wallet_id == "wallet-001"

    assert wallet.address == "0x123456789ABCDEF"

    assert wallet.network == "ethereum"

    assert wallet.wallet_type == "software"


def test_validate_created_wallet(
    manager: WalletManager,
):
    """
    Newly created wallet validates.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-002",
        address="0xABCDEF123456789",
        network="ethereum",
    )

    assert manager.validate_wallet(
        wallet
    )
###############################################################################
# Wallet Persistence
###############################################################################


def test_save_wallet(
    manager: WalletManager,
):
    """
    Wallet can be saved.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-save",
        address="0x111111111111111",
        network="ethereum",
    )

    manager.save_wallet(wallet)

    assert manager.wallet_exists(
        "wallet-save"
    )


def test_load_wallet(
    manager: WalletManager,
):
    """
    Wallet can be loaded.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-load",
        address="0x222222222222222",
        network="ethereum",
    )

    manager.save_wallet(wallet)

    loaded = manager.load_wallet(
        "wallet-load"
    )

    assert isinstance(
        loaded,
        Wallet,
    )

    assert loaded.wallet_id == wallet.wallet_id
    assert loaded.address == wallet.address
    assert loaded.network == wallet.network


###############################################################################
# Wallet Discovery
###############################################################################


def test_wallet_exists(
    manager: WalletManager,
):
    """
    Wallet existence check.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-exists",
        address="0x333333333333333",
        network="ethereum",
    )

    manager.save_wallet(wallet)

    assert manager.wallet_exists(
        "wallet-exists"
    )

    assert not manager.wallet_exists(
        "unknown-wallet"
    )


def test_list_wallets(
    manager: WalletManager,
):
    """
    Stored wallets are listed.
    """

    wallet1 = manager.create_wallet(
        wallet_id="wallet-1",
        address="0xAAAA",
        network="ethereum",
    )

    wallet2 = manager.create_wallet(
        wallet_id="wallet-2",
        address="0xBBBB",
        network="ethereum",
    )

    manager.save_wallet(wallet1)
    manager.save_wallet(wallet2)

    wallets = manager.list_wallets()

    assert "wallet-1" in wallets
    assert "wallet-2" in wallets
    assert len(wallets) == 2


def test_count_wallets(
    manager: WalletManager,
):
    """
    Wallet count is correct.
    """

    assert manager.count_wallets() == 0

    manager.save_wallet(
        manager.create_wallet(
            wallet_id="wallet-a",
            address="0xAAA",
            network="ethereum",
        )
    )

    manager.save_wallet(
        manager.create_wallet(
            wallet_id="wallet-b",
            address="0xBBB",
            network="ethereum",
        )
    )

    assert manager.count_wallets() == 2


###############################################################################
# Wallet Removal
###############################################################################


def test_delete_wallet(
    manager: WalletManager,
):
    """
    Wallet deletion succeeds.
    """

    wallet = manager.create_wallet(
        wallet_id="wallet-delete",
        address="0x444444444444444",
        network="ethereum",
    )

    manager.save_wallet(wallet)

    assert manager.wallet_exists(
        "wallet-delete"
    )

    manager.delete_wallet(
        "wallet-delete"
    )

    assert not manager.wallet_exists(
        "wallet-delete"
    )


def test_clear_storage(
    manager: WalletManager,
):
    """
    Storage can be cleared.
    """

    for index in range(3):

        manager.save_wallet(

            manager.create_wallet(
                wallet_id=f"wallet-{index}",
                address=f"0x{index}",
                network="ethereum",
            )

        )

    assert manager.count_wallets() == 3

    deleted = manager.clear_storage()

    assert deleted == 3

    assert manager.count_wallets() == 0
###############################################################################
# Backup & Restore
###############################################################################


def test_backup_and_restore(
    manager: WalletManager,
    tmp_path: Path,
):
    """
    Wallet storage can be backed up and restored.
    """

    wallet = manager.create_wallet(
        wallet_id="backup-wallet",
        address="0x555555555555555",
        network="ethereum",
    )

    manager.save_wallet(wallet)

    backup_directory = tmp_path / "backup"

    manager.backup_storage(
        str(backup_directory),
    )

    manager.clear_storage()

    assert manager.count_wallets() == 0

    manager.restore_storage(
        str(backup_directory),
    )

    assert manager.count_wallets() == 1


###############################################################################
# Encryption Delegation
###############################################################################


def test_encrypt_and_decrypt(
    manager: WalletManager,
):
    """
    Manager delegates encryption correctly.

    Verifies that encrypt_data returns a dict payload and
    decrypt_data returns the original plaintext.
    """

    plaintext = "UBP Enterprise Wallet"

    encrypted = manager.encrypt_data(
        plaintext,
        "secret-password",
    )

    # Critical: encrypted payload must be a dictionary
    assert isinstance(encrypted, dict)
    assert "ciphertext" in encrypted
    assert "salt" in encrypted
    assert "nonce" in encrypted

    decrypted = manager.decrypt_data(
        encrypted,
        "secret-password",
    )

    assert decrypted == plaintext


def test_encrypt_and_decrypt_bytes(
    manager: WalletManager,
):
    """
    Manager delegates bytes encryption correctly.
    """

    original = b"\x00\x01\x02\xff"

    encrypted = manager.encrypt_data(
        original,
        "secret-password",
    )

    assert isinstance(encrypted, dict)

    decrypted = manager.decrypt_data(
        encrypted,
        "secret-password",
    )

    assert decrypted == original


###############################################################################
# Validation Delegation
###############################################################################


def test_validate_wallet(
    manager: WalletManager,
):
    """
    Manager delegates validation.
    """

    wallet = manager.create_wallet(
        wallet_id="validator-wallet",
        address="0x666666666666666",
        network="ethereum",
    )

    assert manager.validate_wallet(wallet)


###############################################################################
# Manager Information
###############################################################################


def test_info(
    manager: WalletManager,
):
    """
    Manager information is returned.
    """

    info = manager.info()

    assert isinstance(info, dict)

    assert info["service"] == "Wallet Manager"

    assert "version" in info

    assert "wallets" in info


###############################################################################
# Representation
###############################################################################


def test_repr(
    manager: WalletManager,
):
    """
    __repr__ returns useful information.
    """

    representation = repr(manager)

    assert "WalletManager" in representation


def test_str(
    manager: WalletManager,
):
    """
    __str__ returns human-readable text.
    """

    text = str(manager)

    assert "Wallet Manager" in text