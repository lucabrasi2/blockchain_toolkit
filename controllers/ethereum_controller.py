"""
Ethereum Controller
"""

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
    UBPException,
)


class EthereumController:
    """
    Ethereum Controller.
    """

    def __init__(self, wallet_service):
        self.wallet_service = wallet_service

    def wallet_inspector(self):
        """
        Inspect an Ethereum wallet.
        """

        address = input("\nEnter Ethereum wallet address:\n> ").strip()

        try:

            report = self.wallet_service.get_wallet_report(address)

            print("\n========== WALLET REPORT ==========")
            print(f"Address : {report['address']}")
            print(f"Balance : {report['balance_eth']} ETH")
            print(f"Wei     : {report['balance_wei']}")
            print(f"Nonce   : {report['nonce']}")

        except InvalidWalletAddressError as error:
            print(f"\n❌ {error}")

        except UBPException as error:
            print(f"\n❌ {error}")

        except Exception as error:
            print(f"\nUnexpected Error: {error}")

        input("\nPress Enter to continue...")