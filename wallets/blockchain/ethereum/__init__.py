"""
Universal Blockchain Platform (UBP)

Package
-------
wallets.blockchain.ethereum

Purpose
-------
Ethereum blockchain wallet implementation.

This package exposes the Ethereum wallet through the
UBP blockchain-wallet architecture.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0.0
"""

from wallets.blockchain.ethereum.wallet import EthereumWallet


__all__ = [
    "EthereumWallet",
]
