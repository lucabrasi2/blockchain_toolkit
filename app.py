"""
TEST

Universal Blockchain Toolkit
Version 1.0
"""

from ethereum.wallets import (
    is_valid_address,
    get_eth_balance,
    get_nonce,
)


def main():

    print("=" * 60)
    print("        UNIVERSAL BLOCKCHAIN TOOLKIT")
    print("=" * 60)

    address = input("\nEnter an Ethereum wallet address:\n> ").strip()

    # Validate address
    if not is_valid_address(address):
        print("\n❌ Invalid Ethereum address.")
        return

    try:

        balance = get_eth_balance(address)
        nonce = get_nonce(address)

        print("\n========== WALLET REPORT ==========")
        print(f"Address : {address}")
        print(f"Balance : {balance['ether']} ETH")
        print(f"Wei     : {balance['wei']}")
        print(f"Nonce   : {nonce}")

    except Exception as error:
        print(f"\n❌ {error}")


if __name__ == "__main__":
    main()