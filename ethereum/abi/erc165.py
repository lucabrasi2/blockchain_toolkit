"""
Universal Blockchain Platform (UBP)

Module:
    ERC-165 ABI Definition

Purpose:
    Minimal ABI required for ERC-165
    interface detection.
"""


ERC165_ABI = [

    {
        "constant": True,
        "inputs": [
            {
                "name": "interfaceId",
                "type": "bytes4",
            }
        ],
        "name": "supportsInterface",
        "outputs": [
            {
                "name": "",
                "type": "bool",
            }
        ],
        "type": "function",
    },
]