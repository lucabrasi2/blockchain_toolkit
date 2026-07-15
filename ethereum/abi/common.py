"""
Universal Blockchain Platform (UBP)

Module:
    Common ABIs Definition

Purpose:
    Common contract interfaces for
    ownership and metadata.
"""


OWNER_ABI = [

    {
        "constant": True,
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "name": "",
                "type": "address",
            }
        ],
        "type": "function",
    },
]


METADATA_ABI = [

    {
        "constant": True,
        "inputs": [],
        "name": "version",
        "outputs": [
            {
                "name": "",
                "type": "string",
            }
        ],
        "type": "function",
    },
]