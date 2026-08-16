"""
Universal Blockchain Platform (UBP)

Module
------
wallets.blockchain.ethereum.wallet

Purpose
-------
Ethereum-specific blockchain wallet implementation.

Architecture
------------
Wallet
    |
    +-- CustodyProvider
    |
    +-- BlockchainWallet
             |
             +-- EthereumWallet
                     |
                     +-- UBP Provider
                     +-- Ethereum network

Responsibilities
----------------
- Represent an Ethereum wallet
- Validate Ethereum addresses
- Retrieve Ethereum balances
- Prepare Ethereum transactions
- Delegate transaction signing to custody
- Broadcast signed transactions
- Retrieve Ethereum transactions
- Retrieve transaction status
- Retrieve latest Ethereum block
- Report wallet status

Not Responsible For
-------------------
- Private-key storage
- Private-key generation
- Custody implementation
- RPC endpoint construction
- Provider lifecycle management
- Persistent wallet storage

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

from typing import Any

from web3 import Web3

from core.logger import get_logger
from providers.base import BaseProvider
from wallets.blockchain.base import BlockchainWallet
from wallets.custody.base import CustodyProvider


logger = get_logger(__name__)


###############################################################################
# Ethereum Wallet
###############################################################################


class EthereumWallet(BlockchainWallet):
    """
    Ethereum-specific implementation of the UBP blockchain-wallet contract.

    The wallet delegates network communication to the configured UBP provider
    and delegates signing authority to the configured custody provider.

    No private-key material is stored by this class.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        wallet_id: str,
        address: str,
        provider: BaseProvider,
        custody: CustodyProvider,
    ) -> None:
        """
        Initialize an Ethereum wallet.
        """

        if not isinstance(
            wallet_id,
            str,
        ):
            raise TypeError(
                "Wallet ID must be a string."
            )

        wallet_id = wallet_id.strip()

        if not wallet_id:
            raise ValueError(
                "Wallet ID cannot be empty."
            )

        if not isinstance(
            address,
            str,
        ):
            raise TypeError(
                "Ethereum address must be a string."
            )

        address = address.strip()

        if not address:
            raise ValueError(
                "Ethereum address cannot be empty."
            )

        if not isinstance(
            provider,
            BaseProvider,
        ):
            raise TypeError(
                "Provider must be a BaseProvider instance."
            )

        if not isinstance(
            custody,
            CustodyProvider,
        ):
            raise TypeError(
                "Custody must be a CustodyProvider instance."
            )

        provider_blockchain = (
            provider.blockchain
            .strip()
            .lower()
        )

        if provider_blockchain != "ethereum":
            raise ValueError(
                "EthereumWallet requires an Ethereum provider."
            )

        if not Web3.is_address(
            address
        ):
            raise ValueError(
                "Invalid Ethereum wallet address."
            )

        self._wallet_id = wallet_id

        self._address = (
            Web3.to_checksum_address(
                address
            )
        )

        self._provider = provider
        self._custody = custody

        logger.info(
            "EthereumWallet initialized: %s",
            self._wallet_id,
        )

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def blockchain(self) -> str:
        """
        Return the blockchain identifier.
        """

        return "ethereum"

    @property
    def network(self) -> str:
        """
        Return the configured Ethereum network.
        """

        return self._provider.network

    @property
    def wallet_id(self) -> str:
        """
        Return the UBP wallet identifier.
        """

        return self._wallet_id

    @property
    def address(self) -> str:
        """
        Return the checksummed Ethereum wallet address.
        """

        return self._address

    ###########################################################################
    # Provider Access
    ###########################################################################

    @property
    def provider(self) -> BaseProvider:
        """
        Return the configured UBP blockchain provider.
        """

        return self._provider

    @property
    def custody(self) -> CustodyProvider:
        """
        Return the configured custody provider.
        """

        return self._custody

    @property
    def web3(self) -> Any:
        """
        Return the active Web3 connection supplied by the UBP provider.
        """

        return self._provider.web3

    ###########################################################################
    # Address
    ###########################################################################

    def get_address(self) -> str:
        """
        Return the Ethereum wallet address.
        """

        return self._address

    ###########################################################################
    # Balance
    ###########################################################################

    def get_balance(self) -> dict[str, Any]:
        """
        Retrieve the Ethereum native-asset balance.
        """

        balance_wei = (
            self.web3.eth.get_balance(
                self._address
            )
        )

        balance_eth = (
            self.web3.from_wei(
                balance_wei,
                "ether",
            )
        )

        return {
            "wallet_id": self.wallet_id,
            "address": self.address,
            "blockchain": self.blockchain,
            "network": self.network,
            "asset": "ETH",
            "balance_wei": balance_wei,
            "balance_eth": balance_eth,
        }

    ###########################################################################
    # Transaction Preparation
    ###########################################################################

    def prepare_transaction(
        self,
        transaction: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare an Ethereum transaction.
        """

        if not isinstance(
            transaction,
            dict,
        ):
            raise TypeError(
                "Transaction must be a dictionary."
            )

        prepared = dict(
            transaction
        )

        prepared.setdefault(
            "from",
            self._address,
        )

        if not isinstance(
            prepared["from"],
            str,
        ):
            raise TypeError(
                "Ethereum sender address must be a string."
            )

        if not Web3.is_address(
            prepared["from"]
        ):
            raise ValueError(
                "Invalid Ethereum sender address."
            )

        prepared["from"] = (
            Web3.to_checksum_address(
                prepared["from"]
            )
        )

        if "to" in prepared:
            if not isinstance(
                prepared["to"],
                str,
            ):
                raise TypeError(
                    "Ethereum transaction recipient "
                    "must be a string."
                )

            if not Web3.is_address(
                prepared["to"]
            ):
                raise ValueError(
                    "Invalid Ethereum recipient address."
                )

            prepared["to"] = (
                Web3.to_checksum_address(
                    prepared["to"]
                )
            )

        if "value" in prepared:
            if not isinstance(
                prepared["value"],
                int,
            ):
                raise TypeError(
                    "Ethereum transaction value "
                    "must be an integer in wei."
                )

            if prepared["value"] < 0:
                raise ValueError(
                    "Ethereum transaction value "
                    "cannot be negative."
                )

        if "data" in prepared:
            if not isinstance(
                prepared["data"],
                (str, bytes),
            ):
                raise TypeError(
                    "Ethereum transaction data "
                    "must be bytes or a hexadecimal string."
                )

        if "nonce" not in prepared:
            prepared["nonce"] = (
                self.web3.eth.get_transaction_count(
                    self._address
                )
            )

        if "chainId" not in prepared:
            prepared["chainId"] = (
                self.web3.eth.chain_id
            )

        if (
            "gas" not in prepared
            and "to" in prepared
        ):
            prepared["gas"] = (
                self.web3.eth.estimate_gas(
                    prepared
                )
            )

        if (
            "gasPrice" not in prepared
            and "maxFeePerGas" not in prepared
        ):
            try:
                priority_fee = (
                    self.web3.eth.max_priority_fee
                )

                latest_block = (
                    self.web3.eth.get_block(
                        "latest"
                    )
                )

                base_fee = latest_block.get(
                    "baseFeePerGas"
                )

                if base_fee is not None:
                    prepared[
                        "maxPriorityFeePerGas"
                    ] = priority_fee

                    prepared[
                        "maxFeePerGas"
                    ] = (
                        base_fee * 2
                        + priority_fee
                    )

                else:
                    prepared[
                        "gasPrice"
                    ] = self.web3.eth.gas_price

            except Exception:
                prepared[
                    "gasPrice"
                ] = self.web3.eth.gas_price

        return prepared

    ###########################################################################
    # Transaction Signing
    ###########################################################################

    def sign_transaction(
        self,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign an Ethereum transaction through custody.
        """

        prepared = self.prepare_transaction(
            transaction
        )

        return self._custody.sign_transaction(
            self.wallet_id,
            prepared,
        )

    ###########################################################################
    # Transaction Broadcasting
    ###########################################################################

    def broadcast_transaction(
        self,
        signed_transaction: str,
    ) -> dict[str, Any]:
        """
        Broadcast a signed Ethereum transaction.
        """

        if not isinstance(
            signed_transaction,
            str,
        ):
            raise TypeError(
                "Signed transaction must be a string."
            )

        signed_transaction = (
            signed_transaction.strip()
        )

        if not signed_transaction:
            raise ValueError(
                "Signed transaction cannot be empty."
            )

        transaction_hash = (
            self.web3.eth.send_raw_transaction(
                signed_transaction
            )
        )

        transaction_hash_hex = (
            transaction_hash.hex()
        )

        return {
            "success": True,
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "transaction_hash": transaction_hash_hex,
        }

    ###########################################################################
    # Transaction Inspection
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve an Ethereum transaction.
        """

        self._validate_transaction_hash(
            transaction_hash
        )

        transaction = (
            self.web3.eth.get_transaction(
                transaction_hash
            )
        )

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "transaction": dict(
                transaction
            ),
        }

    ###########################################################################
    # Transaction Status
    ###########################################################################

    def get_transaction_status(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve Ethereum transaction receipt/status.
        """

        self._validate_transaction_hash(
            transaction_hash
        )

        try:
            receipt = (
                self.web3.eth.get_transaction_receipt(
                    transaction_hash
                )
            )

        except Exception:
            return {
                "wallet_id": self.wallet_id,
                "blockchain": self.blockchain,
                "network": self.network,
                "transaction_hash": transaction_hash,
                "status": "pending",
                "confirmed": False,
            }

        status_value = receipt.get(
            "status"
        )

        if status_value == 1:
            status = "confirmed"
            confirmed = True

        elif status_value == 0:
            status = "failed"
            confirmed = True

        else:
            status = "unknown"
            confirmed = False

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "transaction_hash": transaction_hash,
            "status": status,
            "confirmed": confirmed,
            "receipt": dict(
                receipt
            ),
        }

    ###########################################################################
    # Blockchain State
    ###########################################################################

    def get_latest_block(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest Ethereum block.
        """

        block = self.web3.eth.get_block(
            "latest"
        )

        block_hash = block.get(
            "hash"
        )

        return {
            "blockchain": self.blockchain,
            "network": self.network,
            "number": block.get(
                "number"
            ),
            "hash": (
                block_hash.hex()
                if block_hash is not None
                else None
            ),
            "timestamp": block.get(
                "timestamp"
            ),
            "transaction_count": len(
                block.get(
                    "transactions",
                    [],
                )
            ),
        }

    ###########################################################################
    # Wallet Status
    ###########################################################################

    def get_status(
        self,
    ) -> dict[str, Any]:
        """
        Return Ethereum wallet status.
        """

        try:
            provider_connected = (
                self.web3.is_connected()
            )

        except Exception:
            provider_connected = False

        try:
            custody_unlocked = (
                self._custody.is_unlocked(
                    self.wallet_id
                )
            )

        except Exception:
            custody_unlocked = False

        return {
            "wallet_id": self.wallet_id,
            "address": self.address,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider": self.provider.name,
            "provider_connected": provider_connected,
            "custody_type": self._custody.custody_type,
            "custody_unlocked": custody_unlocked,
            "status": (
                "READY"
                if provider_connected
                else "OFFLINE"
            ),
        }

    ###########################################################################
    # Internal Validation
    ###########################################################################

    @staticmethod
    def _validate_transaction_hash(
        transaction_hash: str,
    ) -> None:
        """
        Validate an Ethereum transaction hash.

        Web3.py 7 does not expose Web3.is_hex(), so validation is performed
        explicitly here.
        """

        if not isinstance(
            transaction_hash,
            str,
        ):
            raise TypeError(
                "Transaction hash must be a string."
            )

        transaction_hash = (
            transaction_hash.strip()
        )

        if not transaction_hash:
            raise ValueError(
                "Transaction hash cannot be empty."
            )

        if not transaction_hash.startswith(
            "0x"
        ):
            raise ValueError(
                "Invalid Ethereum transaction hash."
            )

        if len(
            transaction_hash
        ) != 66:
            raise ValueError(
                "Ethereum transaction hash "
                "must contain 32 bytes."
            )

        try:
            int(
                transaction_hash[2:],
                16,
            )

        except ValueError as exc:
            raise ValueError(
                "Invalid Ethereum transaction hash."
            ) from exc

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            "EthereumWallet("
            f"wallet_id={self.wallet_id!r}, "
            f"address={self.address!r}, "
            f"network={self.network!r}"
            ")"
        )

    def __str__(self) -> str:
        """
        Return a human-readable wallet description.
        """

        return (
            f"Ethereum wallet "
            f"{self.wallet_id} "
            f"({self.address})"
        )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "EthereumWallet",
]


###############################################################################
# End of File
###############################################################################