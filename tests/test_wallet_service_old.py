"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Wallet Service Test
Author  : Jaramogi Diddy

Standalone test for WalletService.
"""

from services.ethereum.wallet_service import (
    WalletService,
)


def main():

    wallet_service = WalletService()

    address = input(
        "\nEnter Ethereum wallet address:\n> "
    ).strip()

    try:

        wallet = (
            wallet_service.get_wallet_balance(
                address
            )
        )

        print("\n========== WALLET REPORT ==========\n")

        print(
            f"Address : {wallet.address}"
        )

        print(
            f"ETH     : {wallet.ether}"
        )

        print(
            f"Wei     : {wallet.wei}"
        )

        print(
            f"Nonce   : {wallet.nonce}"
        )

    except Exception as error:

        print(
            f"\nERROR:\n{error}"
        )


if __name__ == "__main__":

    main()