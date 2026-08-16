"""
Universal Blockchain Platform (UBP)

## Module

wallets.blockchain.tron.wallet

## Purpose

TRON blockchain wallet implementation.

The wallet implements the common UBP BlockchainWallet contract
while delegating blockchain communication to TronProvider.

Private-key management and transaction signing remain within
the UBP custody architecture.

## Author

Jaramogi Diddy

## Project

Universal Blockchain Platform (UBP)

## Version

2.0.0
"""

from __future__ import annotations

from typing import Any

from providers.tron import TronProvider
from wallets.blockchain.base import BlockchainWallet


###############################################################################
# TRON Wallet
###############################################################################


class TronWallet(BlockchainWallet):
    """
    TRON blockchain wallet.

    Responsibilities
    ----------------
    - Wallet identity
    - Address management
    - TRX balance retrieval
    - Blockchain state access
    - Transaction preparation
    - Transaction inspection
    - Transaction status normalization

    Not responsible for
    -------------------
    - Private-key storage
    - Custody
    - Private-key signing
    - Persistent wallet storage
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        wallet_id: str,
        address: str,
        provider: TronProvider,
    ) -> None:
        """
        Initialize a TRON wallet.
        """

        if not isinstance(
            wallet_id,
            str,
        ):
            raise TypeError(
                "wallet_id must be a string."
            )

        wallet_id = wallet_id.strip()

        if not wallet_id:
            raise ValueError(
                "wallet_id cannot be empty."
            )

        if not isinstance(
            address,
            str,
        ):
            raise TypeError(
                "address must be a string."
            )

        address = address.strip()

        if not address:
            raise ValueError(
                "address cannot be empty."
            )

        if not isinstance(
            provider,
            TronProvider,
        ):
            raise TypeError(
                "provider must be a TronProvider."
            )

        self._wallet_id = wallet_id
        self._address = address
        self._provider = provider

    ###########################################################################
    # Identity
    ###########################################################################

    @property
    def blockchain(self) -> str:
        """
        Return the blockchain identifier.
        """

        return "tron"

    @property
    def network(self) -> str:
        """
        Return the configured TRON network.
        """

        return self._provider.network

    @property
    def wallet_id(self) -> str:
        """
        Return the UBP wallet identifier.
        """

        return self._wallet_id

    ###########################################################################
    # Provider
    ###########################################################################

    @property
    def provider(self) -> TronProvider:
        """
        Return the underlying TRON provider.
        """

        return self._provider

    ###########################################################################
    # Address
    ###########################################################################

    @property
    def address(self) -> str:
        """
        Return the TRON wallet address.
        """

        return self._address

    def get_address(self) -> str:
        """
        Return the TRON wallet address.
        """

        return self._address

    ###########################################################################
    # Balance
    ###########################################################################

    def get_balance(self) -> dict[str, Any]:
        """
        Retrieve the wallet's native TRX balance.

        TRON represents native TRX balances in SUN.

        One TRX is represented by 1,000,000 SUN.
        """

        account = self._provider.get_account(
            self._address
        )

        sun = int(
            account.get(
                "balance",
                0,
            )
        )

        trx = sun / 1_000_000

        return {
            "address": self._address,
            "asset": "TRX",
            "balance": trx,
            "balance_sun": sun,
            "network": self.network,
        }

    ###########################################################################
    # Blockchain State
    ###########################################################################

    def get_latest_block(self) -> dict[str, Any]:
        """
        Retrieve the latest TRON block.
        """

        return self._provider.get_latest_block()

    ###########################################################################
    # Transaction Preparation
    ###########################################################################

    def prepare_transaction(
        self,
        transaction: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare a native TRX transaction.

        Parameters
        ----------
        transaction : dict[str, Any]
            Transaction request.

        Required fields
        ---------------
        to_address : str
            Destination TRON address.

        amount : int
            Amount of TRX expressed in SUN.

        Optional fields
        ---------------
        owner_address : str
            Source wallet address. If omitted, the wallet's own
            address is used.

        Returns
        -------
        dict[str, Any]
            Prepared TRON transaction.

        Notes
        -----
        The transaction remains unsigned.

        Private-key handling, signing, custody authorization,
        and broadcasting are outside this method.
        """

        if not isinstance(
            transaction,
            dict,
        ):
            raise TypeError(
                "transaction must be a dictionary."
            )

        prepared = dict(transaction)

        #######################################################################
        # Destination
        #######################################################################

        if "to_address" not in prepared:
            raise ValueError(
                "transaction requires 'to_address'."
            )

        to_address = prepared["to_address"]

        if not isinstance(
            to_address,
            str,
        ):
            raise TypeError(
                "to_address must be a string."
            )

        to_address = to_address.strip()

        if not to_address:
            raise ValueError(
                "to_address cannot be empty."
            )

        prepared["to_address"] = to_address

        #######################################################################
        # Source / Owner
        #######################################################################

        if "owner_address" not in prepared:
            prepared["owner_address"] = self._address

        owner_address = prepared["owner_address"]

        if not isinstance(
            owner_address,
            str,
        ):
            raise TypeError(
                "owner_address must be a string."
            )

        owner_address = owner_address.strip()

        if not owner_address:
            raise ValueError(
                "owner_address cannot be empty."
            )

        if owner_address != self._address:
            raise ValueError(
                "owner_address must match the wallet address."
            )

        prepared["owner_address"] = owner_address

        #######################################################################
        # Amount
        #######################################################################

        if "amount" not in prepared:
            raise ValueError(
                "transaction requires 'amount'."
            )

        amount = prepared["amount"]

        if isinstance(
            amount,
            bool,
        ) or not isinstance(
            amount,
            int,
        ):
            raise TypeError(
                "amount must be an integer number of SUN."
            )

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        prepared["amount"] = amount

        #######################################################################
        # Transaction Metadata
        #######################################################################

        prepared["network"] = self.network

        return prepared

    ###########################################################################
    # Transaction Signing
    ###########################################################################

    def sign_transaction(
        self,
        transaction: dict[str, Any],
    ) -> str:
        """
        Sign a TRON transaction.

        Signing authority belongs to the custody layer.
        """

        raise NotImplementedError(
            "TRON transaction signing is handled "
            "by the custody layer."
        )

    ###########################################################################
    # Transaction Broadcasting
    ###########################################################################

    def broadcast_transaction(
        self,
        signed_transaction: str,
    ) -> dict[str, Any]:
        """
        Broadcast a signed TRON transaction.

        Broadcasting will be implemented in the transaction
        execution stage.
        """

        raise NotImplementedError(
            "TRON transaction broadcasting has "
            "not yet been implemented."
        )

    ###########################################################################
    # Transaction Inspection
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve a TRON transaction by transaction ID.
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

        return self._provider.get_transaction(
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
        Retrieve normalized TRON transaction status.

        The native TRON transaction information endpoint
        provides execution and receipt information.

        UBP converts that information into a normalized
        wallet-level status structure.
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

        info = (
            self._provider.get_transaction_info(
                transaction_hash
            )
        )

        receipt = info.get(
            "receipt",
            {},
        )

        result = receipt.get(
            "result"
        )

        if result is None:
            status = "UNKNOWN"

        elif result == "SUCCESS":
            status = "CONFIRMED"

        else:
            status = "FAILED"

        return {
            "transaction_hash": transaction_hash,
            "status": status,
            "confirmed": status == "CONFIRMED",
            "result": result,
            "block_number": info.get(
                "blockNumber"
            ),
            "fee": info.get(
                "fee"
            ),
            "raw": info,
        }

    ###########################################################################
    # Wallet Status
    ###########################################################################

    def get_status(self) -> dict[str, Any]:
        """
        Return the current TRON wallet status.
        """

        return {
            "wallet_id": self.wallet_id,
            "blockchain": self.blockchain,
            "network": self.network,
            "address": self.address,
            "provider": self.provider.name,
            "provider_available": (
                self.provider.is_available()
            ),
        }

    ###########################################################################
    # Representation
    ###########################################################################

    def __repr__(self) -> str:
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
# End of File
###############################################################################