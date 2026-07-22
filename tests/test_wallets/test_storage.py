"""
Tests for wallets.storage module.
"""

from pathlib import Path

import pytest

from wallets.wallet import Wallet
from wallets.storage import WalletStorage
from wallets.exceptions import WalletNotFoundError


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def storage(tmp_path):
    """
    Create temporary wallet storage.
    """

    return WalletStorage(
        storage_path=str(tmp_path)
    )


@pytest.fixture
def wallet():
    """
    Sample wallet.
    """

    return Wallet(
        wallet_id="wallet001",
        address="0x123456789",
        network="ethereum",
    )


###############################################################################
# Creation
###############################################################################


def test_storage_creation(storage):

    assert storage.storage_path.exists()


###############################################################################
# Save / Load
###############################################################################


def test_save_wallet(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    assert storage.wallet_exists(
        wallet.wallet_id
    )


def test_load_wallet(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    loaded = storage.load_wallet(
        wallet.wallet_id
    )

    assert loaded.wallet_id == wallet.wallet_id

    assert loaded.address == wallet.address


###############################################################################
# Delete
###############################################################################


def test_delete_wallet(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    storage.delete_wallet(
        wallet.wallet_id
    )

    assert not storage.wallet_exists(
        wallet.wallet_id
    )


def test_delete_missing_wallet(storage):

    with pytest.raises(
        WalletNotFoundError
    ):

        storage.delete_wallet(
            "missing"
        )
###############################################################################
# Wallet Discovery
###############################################################################


def test_wallet_exists(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    assert storage.wallet_exists(
        wallet.wallet_id
    )


def test_list_wallets(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    wallets = storage.list_wallets()

    assert wallet.wallet_id in wallets


def test_count_wallets(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    assert storage.count_wallets() == 1



###############################################################################
# Storage Maintenance
###############################################################################


def test_clear_storage(
    storage,
    wallet,
):

    storage.save_wallet(wallet)

    assert storage.count_wallets() == 1

    storage.clear()

    assert storage.count_wallets() == 0



###############################################################################
# Backup & Restore
###############################################################################


def test_backup_wallet(
    storage,
    wallet,
    tmp_path,
):

    storage.save_wallet(wallet)

    backup_dir = tmp_path / "backup"

    backup_file = storage.backup(
        wallet.wallet_id,
        str(backup_dir),
    )

    assert backup_file.exists()


def test_restore_wallet(
    storage,
    wallet,
    tmp_path,
):

    storage.save_wallet(wallet)

    backup_dir = tmp_path / "backup"

    backup_file = storage.backup(
        wallet.wallet_id,
        str(backup_dir),
    )

    storage.delete_wallet(
        wallet.wallet_id
    )

    assert storage.count_wallets() == 0

    restored = storage.restore(
        str(backup_file)
    )

    assert restored.wallet_id == wallet.wallet_id

    assert storage.count_wallets() == 1



###############################################################################
# Information
###############################################################################


def test_storage_info(
    storage,
):

    info = storage.info()

    assert "storage_path" in info

    assert "wallet_count" in info

    assert info["backend"] == "JSON"



###############################################################################
# Representation
###############################################################################


def test_repr(
    storage,
):

    representation = repr(storage)

    assert "WalletStorage" in representation


def test_str(
    storage,
):

    text = str(storage)

    assert "Wallet storage" in text