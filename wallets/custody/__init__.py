"""
Universal Blockchain Platform (UBP)

Wallet custody package.
"""

from wallets.custody.base import (
    CustodyProvider,
    CustodyType,
)

from wallets.custody.custodial import (
    CustodialProvider,
)

from wallets.custody.non_custodial import (
    NonCustodialProvider,
)


__all__ = [
    "CustodyProvider",
    "CustodyType",
    "CustodialProvider",
    "NonCustodialProvider",
]