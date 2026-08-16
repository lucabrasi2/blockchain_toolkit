"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.bitcoin.bitcoin

Purpose
-------
Enterprise Bitcoin provider implementation.

This module provides Bitcoin network connectivity through
Bitcoin Core-compatible JSON-RPC.

Architecture
------------

    BitcoinWallet
          |
    BitcoinProvider
          |
    Bitcoin JSON-RPC transport
          |
    Bitcoin Core / compatible node

The provider does not manage private keys or wallet custody.

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

from decimal import Decimal
from typing import Any
from typing import Optional

import requests

from core.logger import get_logger

from providers.base import (
    BaseProvider,
    ProviderType,
)

from providers.config import ProviderConfig


logger = get_logger(__name__)


###############################################################################
# Bitcoin Provider
###############################################################################


class BitcoinProvider(BaseProvider):
    """
    Enterprise Bitcoin provider.

    Responsibilities
    ----------------
    - Bitcoin provider identity
    - Network configuration
    - Bitcoin Core JSON-RPC transport
    - RPC request execution
    - RPC error normalization
    - Provider status reporting
    - Bitcoin UTXO inspection
    - Bitcoin address balance inspection

    Not responsible for
    -------------------
    - Private-key storage
    - Private-key generation
    - Wallet custody
    - Transaction signing
    """

    ###########################################################################
    # Construction
    ###########################################################################

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:
        """
        Initialize Bitcoin provider.

        Parameters
        ----------
        config:
            UBP provider configuration.
        """

        super().__init__()

        self._config = config

        self._session = requests.Session()

        options = (
            config.options
            if isinstance(
                config.options,
                dict,
            )
            else {}
        )

        self._rpc_username = options.get(
            "username"
        )

        self._rpc_password = options.get(
            "password"
        )

        self._connected = False

        self._last_error: Optional[str] = None

        logger.info(
            "Initialized BitcoinProvider "
            "(network=%s)",
            self._config.network,
        )

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        """
        Return provider name.
        """

        return "bitcoin"

    @property
    def blockchain(self) -> str:
        """
        Return blockchain identifier.
        """

        return "bitcoin"

    @property
    def network(self) -> str:
        """
        Return configured Bitcoin network.
        """

        return self._config.network

    @property
    def provider_type(self) -> ProviderType:
        """
        Return infrastructure classification.

        An explicitly configured HTTP endpoint represents
        externally configured/private infrastructure.

        Without an explicit endpoint, Bitcoin defaults
        to a local Bitcoin Core node.
        """

        if self._config.http_url:
            return ProviderType.PRIVATE

        return ProviderType.LOCAL

    ###########################################################################
    # Endpoint Configuration
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        Return Bitcoin JSON-RPC HTTP endpoint.

        An explicitly configured ProviderConfig HTTP URL
        takes precedence.

        Otherwise the standard Bitcoin Core local RPC
        endpoint for the configured network is returned.
        """

        if self._config.http_url:
            return self._config.http_url

        network = (
            self.network
            .strip()
            .lower()
        )

        if network == "mainnet":
            return "http://127.0.0.1:8332"

        if network == "testnet":
            return "http://127.0.0.1:18332"

        if network == "regtest":
            return "http://127.0.0.1:18443"

        if network == "signet":
            return "http://127.0.0.1:38332"

        raise ValueError(
            f"Unsupported Bitcoin network: {network}"
        )

    @property
    def ws_url(self) -> str:
        """
        Return configured Bitcoin WebSocket endpoint.

        Bitcoin Core's standard JSON-RPC interface is
        HTTP-based, so no WebSocket endpoint is assumed
        when none is configured.
        """

        return self._config.ws_url or ""

    ###########################################################################
    # Configuration
    ###########################################################################

    def get_config(self) -> dict[str, Any]:
        """
        Return safe provider configuration.

        Credentials are never returned.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider_type": self.provider_type.value,
            "http_url": self.http_url,
            "websocket_enabled": bool(
                self.ws_url
            ),
            "authentication_configured": (
                bool(self._rpc_username)
                and bool(self._rpc_password)
            ),
        }

    ###########################################################################
    # Connection Management
    ###########################################################################

    def connect(self) -> bool:
        """
        Verify connectivity to the Bitcoin JSON-RPC endpoint.

        The provider uses getblockchaininfo as its
        connectivity health check.
        """

        try:
            self.rpc_call(
                "getblockchaininfo"
            )

            self._connected = True
            self._last_error = None

            logger.info(
                "Connected to Bitcoin "
                "network '%s'.",
                self.network,
            )

            return True

        except Exception as exc:
            self._connected = False
            self._last_error = str(exc)

            logger.error(
                "Bitcoin connection failed: %s",
                exc,
            )

            return False

    def disconnect(self) -> None:
        """
        Disconnect the provider transport.
        """

        self._session.close()

        self._session = requests.Session()

        self._connected = False

        logger.info(
            "Disconnected Bitcoin provider."
        )

    def is_connected(self) -> bool:
        """
        Return current provider connection state.
        """

        return self._connected

    ###########################################################################
    # JSON-RPC
    ###########################################################################

    def rpc_call(
        self,
        method: str,
        params: Optional[list[Any]] = None,
    ) -> Any:
        """
        Execute a Bitcoin JSON-RPC request.

        Parameters
        ----------
        method:
            Bitcoin Core RPC method.

        params:
            Optional positional RPC parameters.

        Returns
        -------
        Any
            JSON-RPC result.

        Raises
        ------
        TypeError
            Invalid method or parameter type.

        ValueError
            Invalid or malformed RPC response.

        RuntimeError
            Bitcoin RPC returned an error.

        requests.RequestException
            Transport-level failure.
        """

        if not isinstance(
            method,
            str,
        ):
            raise TypeError(
                "RPC method must be a string."
            )

        method = method.strip()

        if not method:
            raise ValueError(
                "RPC method cannot be empty."
            )

        if params is None:
            params = []

        if not isinstance(
            params,
            list,
        ):
            raise TypeError(
                "RPC parameters must be a list."
            )

        payload = {
            "jsonrpc": "1.0",
            "id": "ubp",
            "method": method,
            "params": params,
        }

        auth = None

        if (
            self._rpc_username is not None
            and self._rpc_password is not None
        ):
            auth = (
                self._rpc_username,
                self._rpc_password,
            )

        response = self._session.post(
            self.http_url,
            json=payload,
            auth=auth,
            timeout=self._config.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Bitcoin RPC returned "
                "an invalid response."
            )

        error = data.get(
            "error"
        )

        if error is not None:
            message = (
                error.get(
                    "message",
                    "Unknown Bitcoin RPC error.",
                )
                if isinstance(
                    error,
                    dict,
                )
                else str(error)
            )

            raise RuntimeError(
                f"Bitcoin RPC error: {message}"
            )

        if "result" not in data:
            raise ValueError(
                "Bitcoin RPC response "
                "does not contain a result."
            )

        return data["result"]

    ###########################################################################
    # Bitcoin Node Information
    ###########################################################################

    def get_blockchain_info(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve Bitcoin blockchain information.
        """

        result = self.rpc_call(
            "getblockchaininfo"
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Invalid blockchain information "
                "returned by Bitcoin RPC."
            )

        return result

    def get_network_info(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve Bitcoin node network information.
        """

        result = self.rpc_call(
            "getnetworkinfo"
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Invalid network information "
                "returned by Bitcoin RPC."
            )

        return result

    def get_block_count(
        self,
    ) -> int:
        """
        Return the current Bitcoin block height.
        """

        result = self.rpc_call(
            "getblockcount"
        )

        if not isinstance(
            result,
            int,
        ):
            raise ValueError(
                "Bitcoin RPC returned "
                "an invalid block count."
            )

        return result

    ###########################################################################
    # Bitcoin Raw Transaction Construction
    ###########################################################################

    def create_raw_transaction(
        self,
        inputs: list[dict[str, Any]],
        outputs: dict[str, Any],
    ) -> str:
        """
        Create an unsigned Bitcoin raw transaction.

        This method delegates raw transaction construction to
        Bitcoin Core through JSON-RPC.

        Parameters
        ----------
        inputs:
            Bitcoin transaction inputs. Each input must contain
            a transaction ID and output index.

        outputs:
            Bitcoin transaction outputs in Bitcoin Core's RPC format.

        Returns
        -------
        str
            Unsigned serialized Bitcoin transaction in hexadecimal form.

        Raises
        ------
        TypeError
            If inputs, transaction inputs, txids, vouts, or outputs
            have invalid types.

        ValueError
            If inputs or outputs are empty or malformed, or if Bitcoin
            Core returns an invalid or empty raw transaction.

        Notes
        -----
        This method only constructs an unsigned transaction. It does not
        perform private-key operations or transaction signing.
        """

        if not isinstance(
            inputs,
            list,
        ):
            raise TypeError(
                "inputs must be a list."
            )

        if not inputs:
            raise ValueError(
                "inputs cannot be empty."
            )

        for index, transaction_input in enumerate(
            inputs
        ):
            if not isinstance(
                transaction_input,
                dict,
            ):
                raise TypeError(
                    "Each transaction input must "
                    "be a dictionary."
                )

            txid = transaction_input.get(
                "txid"
            )

            if txid is None:
                raise ValueError(
                    f"Transaction input {index} "
                    "is missing txid."
                )

            if not isinstance(
                txid,
                str,
            ):
                raise TypeError(
                    f"Transaction input {index} "
                    "txid must be a string."
                )

            if not txid.strip():
                raise ValueError(
                    f"Transaction input {index} "
                    "txid cannot be empty."
                )

            if "vout" not in transaction_input:
                raise ValueError(
                    f"Transaction input {index} "
                    "is missing vout."
                )

            vout = transaction_input[
                "vout"
            ]

            if not isinstance(
                vout,
                int,
            ):
                raise TypeError(
                    f"Transaction input {index} "
                    "vout must be an integer."
                )

            if vout < 0:
                raise ValueError(
                    f"Transaction input {index} "
                    "vout cannot be negative."
                )

        if not isinstance(
            outputs,
            dict,
        ):
            raise TypeError(
                "outputs must be a dictionary."
            )

        if not outputs:
            raise ValueError(
                "outputs cannot be empty."
            )

        result = self.rpc_call(
            "createrawtransaction",
            [
                inputs,
                outputs,
            ],
        )

        if not isinstance(
            result,
            str,
        ):
            raise ValueError(
                "Bitcoin Core returned an invalid "
                "raw transaction."
            )

        result = result.strip()

        if not result:
            raise ValueError(
                "Bitcoin Core returned an empty "
                "raw transaction."
            )

        return result

    ###########################################################################
    # Bitcoin UTXO Inspection
    ###########################################################################

    def get_address_utxos(
        self,
        address: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve unspent transaction outputs for a Bitcoin address.

        This uses Bitcoin Core's ``scantxoutset`` RPC with an
        ``addr(<address>)`` descriptor.

        The operation scans the node's UTXO set and does not require
        the address to belong to the node's wallet.

        Parameters
        ----------
        address:
            Bitcoin address to inspect.

        Returns
        -------
        list[dict[str, Any]]
            Normalized UTXO records.

        Raises
        ------
        TypeError
            If address is not a string.

        ValueError
            If address is empty or the RPC response is malformed.

        RuntimeError
            If Bitcoin Core reports that the UTXO scan failed.
        """

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

        result = self.rpc_call(
            "scantxoutset",
            [
                "start",
                [
                    f"addr({address})"
                ],
            ],
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Invalid UTXO scan response "
                "returned by Bitcoin RPC."
            )

        if result.get("success") is not True:
            raise RuntimeError(
                "Bitcoin UTXO scan was not successful."
            )

        unspents = result.get(
            "unspents",
            [],
        )

        if not isinstance(
            unspents,
            list,
        ):
            raise ValueError(
                "Bitcoin RPC returned invalid "
                "UTXO data."
            )

        normalized: list[dict[str, Any]] = []

        for utxo in unspents:
            if not isinstance(
                utxo,
                dict,
            ):
                raise ValueError(
                    "Bitcoin RPC returned an invalid "
                    "UTXO record."
                )

            normalized.append(
                dict(utxo)
            )

        return normalized

    ###########################################################################
    # Bitcoin Address Balance
    ###########################################################################

    def get_address_balance(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Retrieve the unspent balance for a Bitcoin address.

        The balance is calculated from the address's current UTXO set.

        Parameters
        ----------
        address:
            Bitcoin address to inspect.

        Returns
        -------
        dict[str, Any]
            Normalized balance information containing:

            - address
            - asset
            - balance_btc
            - balance_sats
            - utxo_count
            - height
            - best_block
            - utxos
        """

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

        result = self.rpc_call(
            "scantxoutset",
            [
                "start",
                [
                    f"addr({address})"
                ],
            ],
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Invalid UTXO scan response "
                "returned by Bitcoin RPC."
            )

        if result.get("success") is not True:
            raise RuntimeError(
                "Bitcoin UTXO scan was not successful."
            )

        unspents = result.get(
            "unspents",
            [],
        )

        if not isinstance(
            unspents,
            list,
        ):
            raise ValueError(
                "Bitcoin RPC returned invalid "
                "UTXO data."
            )

        total_btc = Decimal("0")

        normalized_utxos: list[dict[str, Any]] = []

        for utxo in unspents:
            if not isinstance(
                utxo,
                dict,
            ):
                raise ValueError(
                    "Bitcoin RPC returned an invalid "
                    "UTXO record."
                )

            amount = utxo.get(
                "amount",
                0,
            )

            if not isinstance(
                amount,
                (int, float, str),
            ):
                raise ValueError(
                    "Bitcoin RPC returned an invalid "
                    "UTXO amount."
                )

            amount_btc = Decimal(
                str(amount)
            )

            amount_sats = int(
                amount_btc * Decimal("100000000")
            )

            normalized_utxo = dict(
                utxo
            )

            normalized_utxo[
                "amount_btc"
            ] = float(amount_btc)

            normalized_utxo[
                "amount_sats"
            ] = amount_sats

            total_btc += amount_btc

            normalized_utxos.append(
                normalized_utxo
            )

        total_sats = int(
            total_btc * Decimal("100000000")
        )

        return {
            "address": address,
            "asset": "BTC",
            "balance_btc": float(total_btc),
            "balance_sats": total_sats,
            "utxo_count": len(
                normalized_utxos
            ),
            "height": result.get(
                "height"
            ),
            "best_block": result.get(
                "bestblock"
            ),
            "utxos": normalized_utxos,
        }
        ###########################################################################
    # Bitcoin Transaction Funding
    ###########################################################################

    def fund_raw_transaction(
        self,
        raw_transaction: str,
        options: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Fund an unsigned Bitcoin raw transaction.

        This method delegates transaction funding to Bitcoin Core
        through the ``fundrawtransaction`` JSON-RPC method. Bitcoin
        Core may select suitable UTXOs, calculate the required fee,
        and add a change output according to the supplied options.

        Parameters
        ----------
        raw_transaction:
            Unsigned serialized Bitcoin transaction in hexadecimal form.

        options:
            Optional Bitcoin Core funding options.

        Returns
        -------
        dict[str, Any]
            Bitcoin Core funding result. The standard response contains
            at least ``hex``, ``fee``, and ``changepos``.

        Raises
        ------
        TypeError
            If raw_transaction is not a string or options is not a
            dictionary when supplied.

        ValueError
            If raw_transaction is empty, options are malformed, or
            Bitcoin Core returns an invalid funding result.

        Notes
        -----
        This method does not sign the transaction. Private-key operations
        remain outside the provider and belong to the custody layer.
        """

        if not isinstance(
            raw_transaction,
            str,
        ):
            raise TypeError(
                "raw_transaction must be a string."
            )

        raw_transaction = raw_transaction.strip()

        if not raw_transaction:
            raise ValueError(
                "raw_transaction cannot be empty."
            )

        if options is not None and not isinstance(
            options,
            dict,
        ):
            raise TypeError(
                "options must be a dictionary."
            )

        params: list[Any] = [
            raw_transaction,
        ]

        if options is not None:
            params.append(
                dict(options)
            )

        result = self.rpc_call(
            "fundrawtransaction",
            params,
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Bitcoin RPC returned an invalid "
                "funding result."
            )

        funded_transaction = result.get(
            "hex"
        )

        if not isinstance(
            funded_transaction,
            str,
        ):
            raise ValueError(
                "Bitcoin RPC funding result does not "
                "contain a valid raw transaction."
            )

        funded_transaction = funded_transaction.strip()

        if not funded_transaction:
            raise ValueError(
                "Bitcoin RPC returned an empty "
                "funded transaction."
            )

        normalized = dict(result)
        normalized[
            "hex"
        ] = funded_transaction

        return normalized

    ###########################################################################
    # Bitcoin Transaction Inspection
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve a Bitcoin transaction by transaction ID.

        Parameters
        ----------
        transaction_hash:
            Bitcoin transaction hash.

        Returns
        -------
        dict[str, Any]
            Raw Bitcoin transaction information.

        Raises
        ------
        TypeError
            If transaction_hash is not a string.

        ValueError
            If transaction_hash is empty.

        RuntimeError
            If Bitcoin RPC reports an error.
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

        result = self.rpc_call(
            "getrawtransaction",
            [
                transaction_hash,
                True,
            ],
        )

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Bitcoin RPC returned invalid "
                "transaction data."
            )

        return result
    ###########################################################################
    # Bitcoin Transaction Broadcasting
    ###########################################################################

    def send_raw_transaction(
        self,
        signed_transaction: str,
    ) -> str:
        """
        Broadcast a signed Bitcoin transaction.

        Parameters
        ----------
        signed_transaction:
            Serialized signed Bitcoin transaction in hexadecimal form.

        Returns
        -------
        str
            Transaction ID returned by Bitcoin Core.

        Raises
        ------
        TypeError
            If signed_transaction is not a string.

        ValueError
            If signed_transaction is empty or Bitcoin Core returns
            an invalid transaction ID.
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

        result = self.rpc_call(
            "sendrawtransaction",
            [
                signed_transaction,
            ],
        )

        if not isinstance(
            result,
            str,
        ):
            raise ValueError(
                "Bitcoin RPC returned an invalid "
                "transaction ID."
            )

        result = result.strip()

        if not result:
            raise ValueError(
                "Bitcoin RPC returned an empty "
                "transaction ID."
            )

        return result
    ###########################################################################
    # Provider Status
    ###########################################################################

    @property
    def last_error(
        self,
    ) -> Optional[str]:
        """
        Return the most recent provider error.
        """

        return self._last_error

    def get_status(
        self,
    ) -> dict[str, Any]:
        """
        Return provider status.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "connected": self._connected,
            "last_error": self._last_error,
        }


###############################################################################
# Public Exports
###############################################################################


__all__ = [
    "BitcoinProvider",
]


###############################################################################
# End of File
##############