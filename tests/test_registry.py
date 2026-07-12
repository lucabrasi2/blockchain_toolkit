from registry.blockchain_registry import registry


class DummyController:
    pass


registry.register("Ethereum", DummyController())
registry.register("Bitcoin", DummyController())
registry.register("TRON", DummyController())

print(registry.list_blockchains())
print(registry.count())
print(registry.exists("Ethereum"))
print(registry.exists("Solana"))