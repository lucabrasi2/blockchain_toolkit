"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
wallets.blockchain.bitcoin.wallet

Purpose
-------
Bitcoin blockchain wallet implementation for UBP.

Architecture
------------

    BitcoinWallet
          |
    +-----+----------------+
    |                      |
    v                      v
BitcoinProvider      CustodyProvider
    |                      |
    v                      v
Bitcoin Core         Signing Authority
    |
    v
Bitcoin Network

Responsibilities
----------------

- Bitcoin wallet identity
- Bitcoin network identity
- Bitcoin address management
- Bitcoin balance interface
- Transaction preparation
- Transaction signing boundary
- Transaction broadcasting boundary
- Transaction inspection boundary
- Blockchain state inspection
- Wallet status reporting

Not Responsible For
-------------------

- Private-key storage
- Private-key generation
- Custody implementation
- Persistent wallet storage
- Provider lifecycle management

Private-key operations are delegated to the UBP custody layer.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
===============================================================================
"""

from __future__ import annotations

from typing import Any

from providers.bitcoin import BitcoinProvider
from wallets.blockchain.base import BlockchainWallet
from wallets.custody.base import CustodyProvider


###############################################################################
# Bitcoin Wallet
###############################################################################


class BitcoinWallet(BlockchainWallet):
    """
    Enterprise Bitcoin blockchain wallet.

    The wallet represents a Bitcoin address and delegates blockchain
    communication to BitcoinProvider.

    Private-key handling and custody remain outside this class.
    Signing authority is supplied by CustodyProvider.
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        wallet_id: str,
        address: str,
        provider: BitcoinProvider,
        custody: CustodyProvider,
    ) -> None:
        """
        Initialize a Bitcoin wallet.

        Parameters
        ----------
        wallet_id:
            UBP wallet identifier.

        address:
            Bitcoin wallet address.

        provider:
            BitcoinProvider instance.

        custody:
            CustodyProvider responsible for signing authority.

        Raises
        ------
        TypeError
            If wallet_id, address, provider, or custody has
            an invalid type.

        ValueError
            If wallet_id or address is empty.
        """

        if not isinstance(
            wallet_id,
            str,
        ):
            raise TypeError(
                "wallet_id must be a string."
            )

        if not isinstance(
            address,
            str,
        ):
            raise TypeError(
                "address must be a string."
            )

        if not isinstance(
            provider,
            BitcoinProvider,
        ):
            raise TypeError(
                "provider must be a BitcoinProvider."
            )

        if not isinstance(
            custody,
            CustodyProvider,
        ):
            raise TypeError(
                "custody must be a CustodyProvider."
            )

        if not wallet_id.strip():
            raise ValueError(
                "wallet_id cannot be empty."
            )

        if not address.strip():
            raise ValueError(
                "address cannot be empty."
            )

        self._wallet_id = wallet_id
        self._address = address
        self._provider = provider
        self._custody = custody

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def blockchain(self) -> str:
        """
        Return the blockchain identifier.

        Returns
        -------
        str
            Blockchain identifier.
        """

        return "bitcoin"

    @property
    def network(self) -> str:
        """
        Return the configured Bitcoin network.

        Returns
        -------
        str
            Bitcoin network identifier.
        """

        return self._provider.network

    @property
    def wallet_id(self) -> str:
        """
        Return the UBP wallet identifier.

        Returns
        -------
        str
            Wallet identifier.
        """

        return self._wallet_id

    ###########################################################################
    # Provider
    ###########################################################################

    @property
    def provider(self) -> BitcoinProvider:
        """
        Return the Bitcoin provider.

        Returns
        -------
        BitcoinProvider
            Configured Bitcoin provider.
        """

        return self._provider

    ###########################################################################
    # Custody
    ###########################################################################

    @property
    def custody(self) -> CustodyProvider:
        """
        Return the wallet custody provider.

        Returns
        -------
        CustodyProvider
            Configured custody provider.
        """

        return self._custody

    ###########################################################################
    # Address
    ###########################################################################

    @property
    def address(self) -> str:
        """
        Return the Bitcoin wallet address.

        Returns
        -------
        str
            Bitcoin address.
        """

        return self._address

    def get_address(self) -> str:
        """
        Return the Bitcoin wallet address.

        Returns
        -------
        str
            Bitcoin address.
        """

        return self._address

    ###########################################################################
    # Balance
    ###########################################################################

    def get_balance(self) -> dict[str, Any]:
        """
        Retrieve the Bitcoin wallet balance.

        The wallet delegates address-level balance inspection to
        BitcoinProvider.

        BitcoinProvider performs the UTXO scan against the Bitcoin
        node and returns the normalized balance representation.

        Returns
        -------
        dict[str, Any]
            Normalized Bitcoin wallet balance information.

        The returned structure contains:

        - address
        - asset
        - balance_btc
        - balance_sats
        - utxo_count
        - height
        - best_block
        - utxos
        """

        return self.provider.get_address_balance(
            self.address
        )

    ###########################################################################
    # Transaction Preparation
    ###########################################################################

    def prepare_transaction(
        self,
        transaction: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare a Bitcoin transaction request.

        The current implementation intentionally performs only
        structural preparation. Bitcoin-specific UTXO selection,
        fee calculation, change generation, and transaction creation
        will be implemented at the provider/transaction layer.

        Parameters
        ----------
        transaction:
            Transaction request.

        Returns
        -------
        dict[str, Any]
            Independent copy of the transaction.

        Raises
        ------
        TypeError
            If transaction is not a dictionary.
        """

        if not isinstance(
            transaction,
            dict,
        ):
            raise TypeError(
                "transaction must be a dictionary."
            )

        return dict(transaction)

    ###########################################################################
    # Transaction Construction
    ###########################################################################

    def build_transaction(
        self,
        transaction: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build and fund a Bitcoin transaction.

        The wallet delegates Bitcoin-specific transaction construction
        and funding to BitcoinProvider.

        The transaction is created and funded while remaining unsigned.
        Signing authority remains exclusively with CustodyProvider.

        Parameters
        ----------
        transaction:
            Bitcoin transaction request containing the inputs and outputs
            required by Bitcoin Core's raw transaction construction.

        options:
            Optional Bitcoin Core funding options.

        Returns
        -------
        dict[str, Any]
            Normalized transaction-building result containing:

            - wallet_id
            - blockchain
            - network
            - hex
            - fee
            - changepos
            - funded

        Raises
        ------
        TypeError
            If transaction or options has an invalid type.

        ValueError
            If transaction construction or funding returns an
            invalid result.
        """

        if not isinstance(
            transaction,
            dict,
        ):
            raise TypeError(
                "transaction must be a dictionary."
            )

        if options is not None and not isinstance(
            options,
            dict,
        ):
            raise TypeError(
                "options must be a dictionary."
            )

        prepared = self.prepare_transaction(
            transaction
        )

        raw_transaction = (
            self.provider.create_raw_transaction(
                prepared
            )
        )

        if not isinstance(
            raw_transaction,
            str,
        ):
            raise ValueError(
                "Bitcoin provider returned an invalid "
                "raw transaction."
            )

        raw_transaction = raw_transaction.strip()

        if not raw_transaction:
            raise ValueError(
                "Bitcoin provider returned an empty "
                "raw transaction."
            )

        funded_transaction = (
            self.provider.fund_raw_transaction(
                raw_transaction,
                options=options,
            )
        )

        if not isinstance(
            funded_transaction,
            dict,
        ):
            raise ValueError(
                "Bitcoin provider returned an invalid "
                "funded transaction."
            )

        funded_hex = funded_transaction.get(
            "hex"
        )

        if not isinstance(
            funded_hex,
            str,
        ) or not funded_hex.strip():
            raise ValueError(
                "Bitcoin provider returned a funded "
                "transaction without valid hex."
            )

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "hex": funded_hex,
            "fee": funded_transaction.get(
                "fee"
            ),
            "changepos": funded_transaction.get(
                "changepos"
            ),
            "funded": True,
        }

    ###########################################################################
    # Transaction Signing
    ###########################################################################

    def sign_transaction(
        self,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign a Bitcoin transaction through the custody layer.

        The wallet prepares the transaction structurally and then
        delegates signing authority to CustodyProvider.

        The wallet does not access or manage private-key material.

        Parameters
        ----------
        transaction:
            Bitcoin transaction request.

        Returns
        -------
        str
            Serialized signed Bitcoin transaction.

        Raises
        ------
        TypeError
            If transaction is not a dictionary.
        """

        prepared = self.prepare_transaction(
            transaction
        )

        return self.custody.sign_transaction(
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
        Broadcast a signed Bitcoin transaction.

        The wallet delegates transaction broadcasting to
        BitcoinProvider.

        Parameters
        ----------
        signed_transaction:
            Serialized signed Bitcoin transaction.

        Returns
        -------
        dict[str, Any]
            Normalized broadcast result.

        Raises
        ------
        TypeError
            If signed_transaction is not a string.

        ValueError
            If signed_transaction is empty.
        """

        if not isinstance(
            signed_transaction,
            str,
        ):
            raise TypeError(
                "signed_transaction must be a string."
            )

        signed_transaction = signed_transaction.strip()

        if not signed_transaction:
            raise ValueError(
                "signed_transaction cannot be empty."
            )

        transaction_hash = (
            self.provider.send_raw_transaction(
                signed_transaction
            )
        )

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "transaction_hash": transaction_hash,
            "status": "broadcast",
            "broadcast": True,
        }

    ###########################################################################
    # Transaction Inspection
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve Bitcoin transaction information.

        The wallet delegates transaction inspection to
        BitcoinProvider.

        Parameters
        ----------
        transaction_hash:
            Bitcoin transaction hash.

        Returns
        -------
        dict[str, Any]
            Bitcoin transaction information.

        Raises
        ------
        TypeError
            If transaction_hash is not a string.

        ValueError
            If transaction_hash is empty.
        """

        if not isinstance(
            transaction_hash,
            str,
        ):
            raise TypeError(
                "transaction_hash must be a string."
            )

        transaction_hash = transaction_hash.strip()

        if not transaction_hash:
            raise ValueError(
                "transaction_hash cannot be empty."
            )

        return self.provider.get_transaction(
            transaction_hash
        )

    ###########################################################################
    # Transaction Status
    ###########################################################################

    def get_transaction_status(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve normalized Bitcoin transaction status.

        Bitcoin transaction confirmation state is determined
        from the transaction's confirmation count.

        Parameters
        ----------
        transaction_hash:
            Bitcoin transaction hash.

        Returns
        -------
        dict[str, Any]
            Normalized transaction status information.
        """

        if not isinstance(
            transaction_hash,
            str,
        ):
            raise TypeError(
                "transaction_hash must be a string."
            )

        transaction_hash = transaction_hash.strip()

        if not transaction_hash:
            raise ValueError(
                "transaction_hash cannot be empty."
            )

        transaction = self.provider.get_transaction(
            transaction_hash
        )

        confirmations = transaction.get(
            "confirmations",
            0,
        )

        if not isinstance(
            confirmations,
            int,
        ):
            raise ValueError(
                "Bitcoin transaction returned an "
                "invalid confirmation count."
            )

        if confirmations > 0:
            status = "confirmed"
            confirmed = True
        else:
            status = "pending"
            confirmed = False

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "transaction_hash": transaction_hash,
            "status": status,
            "confirmed": confirmed,
            "confirmations": confirmations,
            "transaction": transaction,
        }

    ###########################################################################
    # Blockchain State
    ###########################################################################

    def get_latest_block(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the latest Bitcoin blockchain state.

        Returns
        -------
        dict[str, Any]
            Normalized latest-block information.
        """

        blockchain_info = (
            self.provider.get_blockchain_info()
        )

        block_count = (
            self.provider.get_block_count()
        )

        return {
            "blockchain": self.blockchain,
            "network": self.network,
            "height": block_count,
            "best_block_hash": blockchain_info.get(
                "bestblockhash"
            ),
            "chain": blockchain_info.get(
                "chain"
            ),
            "headers": blockchain_info.get(
                "headers"
            ),
            "blocks": blockchain_info.get(
                "blocks"
            ),
        }

    ###########################################################################
    # Wallet Status
    ###########################################################################

    def get_status(
        self,
    ) -> dict[str, Any]:
        """
        Return Bitcoin wallet status information.

        Returns
        -------
        dict[str, Any]
            Wallet status information.
        """

        provider_connected = (
            self.provider.is_connected()
        )

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "address": self.address,
            "provider": self.provider.name,
            "provider_connected": provider_connected,
            "provider_available": provider_connected,
            "custody": self.custody.custody_type,
        }

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"wallet_id={self.wallet_id!r}, "
            f"blockchain={self.blockchain!r}, "
            f"network={self.network!r}, "
            f"address={self.address!r}"
            ")"
        )


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "BitcoinWallet",
]


###############################################################################
# End of File
###############################################################################