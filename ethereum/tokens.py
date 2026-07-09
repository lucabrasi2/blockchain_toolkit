"""
Ethereum ERC-20 token functions.
"""

from ethereum.connection import get_connection

# Minimal ERC-20 ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]

USDT_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

def get_token_balance(wallet_address, contract_address):
    """
    Get an ERC-20 token balance.
    """

    w3 = get_connection()

    wallet = w3.to_checksum_address(wallet_address)
    contract = w3.to_checksum_address(contract_address)

    token = w3.eth.contract(
        address=contract,
        abi=ERC20_ABI,
    )

    decimals = token.functions.decimals().call()
    symbol = token.functions.symbol().call()

    raw_balance = token.functions.balanceOf(wallet).call()

    balance = raw_balance / (10 ** decimals)

    return {
        "symbol": symbol,
        "balance": balance,
    }