from __future__ import annotations

from typing import Any

from core.logger import get_logger
from providers.web3_provider import Web3Provider
from providers.config import ProviderConfig
from providers.provider_type import ProviderType

logger = get_logger(__name__)


class AlchemyProvider(Web3Provider):
    """
    Enterprise Alchemy provider implementation.

    This provider supplies Ethereum-compatible blockchain connectivity
    through Alchemy infrastructure while delegating connection lifecycle,
    health monitoring, statistics, and diagnostics to BaseProvider.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """
        Initialize the Alchemy provider.

        Parameters
        ----------
        config : ProviderConfig
            Validated provider configuration.
        """
        super().__init__()

        self._config = config

        logger.info(
            "Initialized AlchemyProvider "
            "(network=%s)",
            self._config.network,
        )

    ###########################################################################
    # Provider Identity
    ###########################################################################

    @property
    def name(self) -> str:
        return "Alchemy"

    @property
    def blockchain(self) -> str:
        """
        Determine the blockchain from the configured network.
        """
        network = self._config.network.lower()

        if "polygon" in network:
            return "Polygon"

        if "arb" in network or "arbitrum" in network:
            return "Arbitrum"

        if "optimism" in network or "opt" in network:
            return "Optimism"

        if "base" in network:
            return "Base"

        return "Ethereum"

    @property
    def network(self) -> str:
        return self._config.network

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CLOUD

    ###########################################################################
    # Endpoint Configuration
    ###########################################################################

    @property
    def http_url(self) -> str:
        """
        Return the HTTP RPC endpoint.
        """

        if self._config.endpoint:
            return self._config.endpoint

        return (
            f"https://{self._config.network}"
            f".g.alchemy.com/v2/"
            f"{self._config.api_key}"
        )

    @property
    def ws_url(self) -> str:
        """
        Return the WebSocket RPC endpoint.
        """

        return (
            f"wss://{self._config.network}"
            f".g.alchemy.com/v2/"
            f"{self._config.api_key}"
        )
        ###########################################################################
    # Provider Configuration
    ###########################################################################

    def get_config(self) -> dict[str, Any]:
        """
        Return provider configuration.

        Sensitive information such as API keys is never exposed.
        """

        return {
            "provider": self.name,
            "blockchain": self.blockchain,
            "network": self.network,
            "provider_type": self.provider_type.value,
            "http_enabled": True,
            "websocket_enabled": bool(self.ws_url),
            "api_key_configured": bool(self._config.api_key),
            "endpoint_override": bool(self._config.endpoint),
        }

    ###########################################################################
    # Provider Information
    ###########################################################################

    def get_provider_info(self) -> dict[str, Any]:
        """
        Return normalized provider information.
        """

        information = super().get_provider_info()

        information.update(
            {
                "service": "Alchemy",
                "api_key_configured": bool(self._config.api_key),
                "endpoint_override": bool(self._config.endpoint),
            }
        )

        return information

    ###########################################################################
    # Endpoint Validation
    ###########################################################################

    def validate_endpoint(self) -> bool:
        """
        Validate the configured Alchemy endpoint.
        """

        logger.debug(
            "Validating Alchemy endpoint for %s.",
            self.network,
        )

        return self.health_check()

    ###########################################################################
    # Blockchain Queries
    ###########################################################################

    def get_block_number(self) -> int:
        """
        Return the latest block number.
        """

        self.before_request()

        try:
            block_number = self.web3.eth.block_number

            self.after_request(successful=True)

            return block_number

        except Exception:
            self.after_request(successful=False)
            logger.exception(
                "Failed to retrieve latest block number."
            )
            raise

    ###########################################################################
    # Account Operations
    ###########################################################################

    def get_balance(self, address: str) -> int:
        """
        Retrieve an account balance.

        Parameters
        ----------
        address : str
            Ethereum-compatible wallet address.

        Returns
        -------
        int
            Balance in Wei.
        """

        self.before_request()

        try:
            balance = self.web3.eth.get_balance(address)

            self.after_request(successful=True)

            return balance

        except Exception:
            self.after_request(successful=False)
            logger.exception(
                "Failed to retrieve balance for %s.",
                address,
            )
            raise

    def get_balance_eth(self, address: str) -> float:
        """
        Retrieve an account balance in Ether.

        Parameters
        ----------
        address : str
            Ethereum-compatible wallet address.

        Returns
        -------
        float
            Balance in Ether.
        """

        balance = self.get_balance(address)

        return float(
            self.web3.from_wei(
                balance,
                "ether",
            )
        )
        ###########################################################################
    # Block Operations
    ###########################################################################

    def get_block(
        self,
        block_identifier: Any = "latest",
    ) -> dict[str, Any]:
        """
        Retrieve block information.

        Parameters
        ----------
        block_identifier : Any
            Block number, block hash, or "latest".

        Returns
        -------
        dict[str, Any]
            Block information.
        """

        self.before_request()

        try:
            block = self.web3.eth.get_block(
                block_identifier
            )

            self.after_request(
                successful=True
            )

            return dict(block)

        except Exception:
            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve block: %s",
                block_identifier,
            )

            raise

    ###########################################################################
    # Transaction Operations
    ###########################################################################

    def get_transaction(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction information.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Transaction details.
        """

        self.before_request()

        try:
            transaction = (
                self.web3.eth.get_transaction(
                    transaction_hash
                )
            )

            self.after_request(
                successful=True
            )

            return dict(transaction)

        except Exception:
            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve transaction: %s",
                transaction_hash,
            )

            raise

    def get_transaction_receipt(
        self,
        transaction_hash: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction receipt.

        Parameters
        ----------
        transaction_hash : str
            Transaction hash.

        Returns
        -------
        dict[str, Any]
            Receipt information.
        """

        self.before_request()

        try:
            receipt = (
                self.web3.eth.get_transaction_receipt(
                    transaction_hash
                )
            )

            self.after_request(
                successful=True
            )

            return dict(receipt)

        except Exception:
            self.after_request(
                successful=False
            )

            logger.exception(
                "Failed to retrieve receipt: %s",
                transaction_hash,
            )

            raise

    ###########################################################################
    # Alchemy Features
    ###########################################################################

    def get_token_balances(
        self,
        address: str,
    ) -> dict[str, Any]:
        """
        Placeholder for Alchemy Token API support.

        Future support:
        - alchemy_getTokenBalances
        - ERC20 discovery
        - NFT discovery
        """

        logger.info(
            "Token balance request for %s",
            address,
        )

        return {
            "address": address,
            "tokens": [],
            "status": "not_enabled",
        }

    ###########################################################################
    # Cleanup
    ###########################################################################

    def close(self) -> None:
        """
        Release provider resources.
        """

        logger.info(
            "Closing Alchemy provider."
        )

        super().close()


###############################################################################
# End of File
###############################################################################