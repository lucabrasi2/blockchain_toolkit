"""
Ethereum Menu
"""


def ethereum_menu():
    print()
    print("=" * 50)
    print("             ETHEREUM")
    print("=" * 50)
    print("1. Wallet Inspector")
    print("2. Token Inspector")
    print("3. Block Explorer")
    print("4. Transaction Explorer")
    print("5. Network Information")
    print("6. Back")
    print()

    return input("Selection: ").strip()