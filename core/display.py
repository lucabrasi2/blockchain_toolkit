"""
Display functions.

Responsible for presenting blockchain information.
"""

from datetime import datetime


def display_block(block):
    """
    Display Ethereum block information.
    """

    print("\n" + "=" * 60)
    print("            ETHEREUM BLOCK REPORT")
    print("=" * 60)

    print(f"Block Number : {block.number}")
    print(f"Hash         : {block.hash.hex()}")
    print(f"Parent Hash  : {block.parentHash.hex()}")

    print(f"Transactions : {len(block.transactions)}")

    print(f"Gas Used     : {block.gasUsed:,}")
    print(f"Gas Limit    : {block.gasLimit:,}")

    print(f"Timestamp    : {datetime.fromtimestamp(block.timestamp)}")

    if hasattr(block, "baseFeePerGas"):
        print(f"Base Fee     : {block.baseFeePerGas:,}")

    print("=" * 60)