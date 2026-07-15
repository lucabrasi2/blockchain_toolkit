"""
Universal Blockchain Platform (UBP)

Version : 1.1.0
Module  : Ethereum Menu
Author  : Jaramogi Diddy

Ethereum submenu.
"""


def ethereum_menu() -> str:
    """
    Display the Ethereum menu.

    Returns:
        str:
            User selection.
    """

    print("=" * 50)
    print("                 ETHEREUM")
    print("=" * 50)

    print("1. Wallet Inspector")
    print("2. Token Inspector")
    print("3. Smart Contract Inspector")
    print("4. Block Explorer")
    print("5. Transaction Explorer")
    print("6. Network Information")
    print("7. Back")

    print()

    return input("Selection: ").strip()