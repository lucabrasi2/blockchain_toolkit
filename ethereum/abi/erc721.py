"""
Universal Blockchain Platform (UBP)

Module:
    ERC-721 ABI Definition

Purpose:
    Minimal ABI required for ERC-721
    NFT token intelligence.
"""


ERC721_ABI = [

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
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256",
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

    {
        "constant": True,
        "inputs": [
            {
                "name": "_tokenId",
                "type": "uint256",
            }
        ],
        "name": "ownerOf",
        "outputs": [
            {
                "name": "",
                "type": "address",
            }
        ],
        "type": "function",
    },
]
