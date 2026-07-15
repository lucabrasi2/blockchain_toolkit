"""
Universal Blockchain Platform (UBP)

Module:
    ERC-20 ABI Definition

Purpose:
    Minimal ABI required for ERC-20
    token intelligence.
"""


ERC20_ABI = [

    {
        "constant": True,
        "inputs": [],
        "name": "name",
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
        "inputs": [],
        "name": "symbol",
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
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8",
            }
        ],
        "type": "function",
    },

    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256",
            }
        ],
        "type": "function",
    },
]