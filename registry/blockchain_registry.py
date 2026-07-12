"""
Blockchain Registry

Central registry for all blockchain modules.
"""


class BlockchainRegistry:
    """
    Stores blockchain controllers registered with UBP.
    """

    def __init__(self):
        """
        Initialize an empty registry.
        """
        self._blockchains = {}

    def register(self, name, controller):
        """
        Register a blockchain controller.

        Args:
            name (str):
                Blockchain name.

            controller:
                Controller instance.
        """

        self._blockchains[name] = controller

    def get(self, name):
        """
        Retrieve a blockchain controller.

        Returns:
            Controller instance or None.
        """

        return self._blockchains.get(name)

    def exists(self, name):
        """
        Check whether a blockchain exists.
        """

        return name in self._blockchains

    def list_blockchains(self):
        """
        Return all registered blockchains.
        """

        return list(self._blockchains.keys())

    def count(self):
        """
        Return the number of registered blockchains.
        """

        return len(self._blockchains)


# Global registry instance
registry = BlockchainRegistry()