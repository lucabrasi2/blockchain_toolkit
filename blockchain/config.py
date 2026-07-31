"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
blockchain.config

Purpose
-------
Defines configuration objects for blockchain implementations.

The BlockchainConfig class contains blockchain-specific settings
used by blockchain implementations while delegating connectivity
to the Provider subsystem.

Author
------
Jaramogi Diddy

Platform
--------
Universal Blockchain Platform (UBP)

Version
-------
2.1 Enterprise
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import Optional


@dataclass(slots=True)
class BlockchainConfig:
    """
    Blockchain configuration.

    Parameters
    ----------
    blockchain:
        Blockchain identifier.
        Example:
            ethereum
            bitcoin
            tron

    network:
        Network name.
        Example:
            mainnet
            testnet
            sepolia
            shasta

    provider:
        Registered provider name.

    chain_id:
        Expected blockchain chain ID.

    timeout:
        Request timeout in seconds.

    auto_connect:
        Automatically connect when the blockchain object
        is created.

    verify_chain_id:
        Verify that the connected chain ID matches the
        configured value.

    options:
        Additional blockchain-specific configuration.
    """

    blockchain: str

    network: str = "mainnet"

    provider: Optional[str] = None

    chain_id: Optional[int] = None

    timeout: int = 30

    auto_connect: bool = False

    verify_chain_id: bool = True

    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Normalize configuration values.
        """

        self.blockchain = self.blockchain.strip().lower()

        self.network = self.network.strip().lower()

        if self.provider is not None:
            self.provider = self.provider.strip().lower()

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero."
            )

    @property
    def has_provider(self) -> bool:
        """
        Return True if a provider has been configured.
        """

        return self.provider is not None

    @property
    def has_chain_id(self) -> bool:
        """
        Return True if an expected chain ID has been configured.
        """

        return self.chain_id is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the configuration.
        """

        return {
            "blockchain": self.blockchain,
            "network": self.network,
            "provider": self.provider,
            "chain_id": self.chain_id,
            "timeout": self.timeout,
            "auto_connect": self.auto_connect,
            "verify_chain_id": self.verify_chain_id,
            "options": dict(self.options),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "BlockchainConfig":
        """
        Construct a BlockchainConfig from a dictionary.
        """

        return cls(**data)

    def copy(
        self,
        **changes: Any,
    ) -> "BlockchainConfig":
        """
        Return a copy with selected fields replaced.
        """

        data = self.to_dict()
        data.update(changes)

        return BlockchainConfig(**data)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"blockchain={self.blockchain!r}, "
            f"network={self.network!r}, "
            f"provider={self.provider!r}, "
            f"chain_id={self.chain_id!r})"
        )