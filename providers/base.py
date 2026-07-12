"""
Universal Blockchain Platform (UBP)

Version : 0.8.0
Module  : Base Provider Interface
Author  : Jaramogi Diddy

Defines the abstract interface that every blockchain
provider must implement.
"""

from abc import ABC, abstractmethod
from web3 import Web3


class BaseProvider(ABC):
    """
    Abstract base class for blockchain providers.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the provider.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Return True if the provider is connected.
        """
        pass

    @abstractmethod
    def get_web3(self) -> Web3:
        """
        Return the configured Web3 instance.
        """
        pass