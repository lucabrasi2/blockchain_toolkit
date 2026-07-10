"""
Ethereum Controller

Coordinates Ethereum-related user actions for the
Universal Blockchain Platform (UBP).
"""

from ethereum.wallets import (
    is_valid_address,
    checksum_address,
    get_eth_balance,
    get_nonce,
)

from core.display.wallet_display import display_wallet_report


def wallet_inspector():
    """
    Ethereum Wallet Inspector.

    Prompts the user for a wallet address, validates it,
    retrieves wallet information, and displays a formatted report.
    """

    print("\nEnter Ethereum wallet address:")

    address = input("> ").strip()

    # Validate the wallet address
    if not is_valid_address(address):
        print("\n❌ Invalid Ethereum wallet address.")
        input("\nPress Enter to continue...")
        return

    # Convert to checksum format
    address = checksum_address(address)

    try:
        # Retrieve wallet information
        balance = get_eth_balance(address)
        nonce = get_nonce(address)

        # Display the report
        display_wallet_report(
            address=address,
            balance=balance,
            nonce=nonce,
        )

    except Exception as error:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(error)
        print("=" * 60)

    input("\nPress Enter to continue...")