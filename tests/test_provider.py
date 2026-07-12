from providers.factory import ProviderFactory


provider = ProviderFactory.get_provider()

print("Connected:", provider.is_connected())

web3 = provider.get_web3()

print("Chain ID:", web3.eth.chain_id)

print("Latest Block:", web3.eth.block_number)