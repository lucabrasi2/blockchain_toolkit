"""
Wallet Display Module

Responsible for displaying Ethereum wallet information
for the Universal Blockchain Platform (UBP).
"""


def display_wallet_report(address, balance, nonce):
    """
    Display a formatted Ethereum wallet report.

    Args:
        address (str): Ethereum wallet address.
        balance (dict): Dictionary containing ETH and Wei balances.
        nonce (int): Transaction count (nonce).
    """

    print()
    print("=" * 60)
    print("               ETHEREUM WALLET REPORT")
    print("=" * 60)

    print(f"Address : {address}")
    print(f"Balance : {balance['ether']} ETH")
    print(f"Wei     : {balance['wei']}")
    print(f"Nonce   : {nonce}")

    print("=" * 60)