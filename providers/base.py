"""
Base Provider Interface.

Every blockchain provider must implement these methods.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
   Abstract blockchain provider.
    """

    @abstractmethod
    def connect(self):
        """
        Create a connection.
        """

    @abstractmethod
    def is_connected(self):
        """
        Verify the connection.
        """

    @abstractmethod
    def get_web3(self):
        """
        Return the Web3 instance.
        """