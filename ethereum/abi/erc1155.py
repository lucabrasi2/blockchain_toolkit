"""
Universal Blockchain Platform (UBP)

Module:
    ERC-1155 ABI Definition

Purpose:
    Minimal ABI required for ERC-1155
    multi-token intelligence.
"""


ERC1155_ABI = [

    {
        "constant": True,
        "inputs": [
            {
                "name": "_id",
                "type": "uint256",
            }
        ],
        "name": "uri",
        "outputs": [
            {
                "name": "",
                "type": "string",
            }
        ],
        "type": "function",
    },

    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address",
            },
            {
                "name": "_id",
                "type": "uint256",
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256",
            }
        ],
        "type": "function",
    },
]
