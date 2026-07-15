"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Ethereum Contract Intelligence

Author  : Jaramogi Diddy

Description
-----------
Provides blockchain intelligence for Ethereum
smart contracts.

Responsibilities
----------------
• Smart contract detection
• EIP-7702 delegated account detection
• ERC-165 interface detection
• ERC-20 detection
• ERC-721 detection
• ERC-1155 detection
• Contract metadata retrieval
• Bytecode analysis

This module intentionally contains NO business
logic.

Business logic belongs in:

    services/ethereum/contract_service.py

The controller layer should never access this
module directly.
"""

from __future__ import annotations

from typing import Any

from web3 import Web3
from web3.contract import Contract

from ethereum.connection import get_connection

from ethereum.wallets import (
    is_valid_address,
)

from ethereum.abi import (
    ERC20_ABI,
    ERC165_ABI,
)

from constants.contract_types import (
    EOA,
    EOA_DELEGATED,
    CONTRACT,
    ERC20,
    ERC721,
    ERC1155,
    UNKNOWN,
)

from exceptions.blockchain_exceptions import (
    InvalidWalletAddressError,
)

from core.logger import get_logger


logger = get_logger(__name__)


###############################################################################
# Ethereum Interface IDs
###############################################################################

ERC721_INTERFACE_ID = "0x80ac58cd"

ERC1155_INTERFACE_ID = "0xd9b67a26"

EIP7702_PREFIX = b"\xef\x01\x00"


###############################################################################
# Internal Helpers
###############################################################################


def _get_web3() -> Web3:
    """
    Return the active Web3 connection.

    Returns
    -------
    Web3
        Active blockchain connection.
    """

    return get_connection()


def _validate_address(
    address: str,
) -> None:
    """
    Validate an Ethereum address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Raises
    ------
    InvalidWalletAddressError
        If the supplied address is invalid.
    """

    logger.info(
        "Validating Ethereum address."
    )

    if not is_valid_address(address):

        logger.warning(
            "Invalid Ethereum address."
        )

        raise InvalidWalletAddressError(
            "Invalid Ethereum address."
        )


def _get_contract(
    address: str,
    abi: list[dict[str, Any]],
) -> Contract:
    """
    Create a Web3 contract instance.

    Parameters
    ----------
    address : str
        Ethereum contract address.

    abi : list
        Contract ABI.

    Returns
    -------
    Contract
        Web3 contract object.
    """

    _validate_address(address)

    w3 = _get_web3()

    return w3.eth.contract(
        address=Web3.to_checksum_address(
            address
        ),
        abi=abi,
    )


def _safe_call(
    function,
    default=None,
):
    """
    Execute a blockchain call safely.

    Any blockchain exception is converted
    into a default return value.

    Parameters
    ----------
    function
        Callable contract function.

    default
        Value returned on failure.
    """

    try:

        return function.call()

    except Exception:

        return default


###############################################################################
# Bytecode Intelligence
###############################################################################


def get_bytecode(
    address: str,
) -> bytes:
    """
    Retrieve deployed bytecode.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    bytes
        Contract bytecode.
    """

    logger.info(
        "Retrieving contract bytecode."
    )

    _validate_address(address)

    w3 = _get_web3()

    return w3.eth.get_code(
        Web3.to_checksum_address(
            address
        )
    )


def get_bytecode_size(
    address: str,
) -> int:
    """
    Return deployed bytecode size.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    int
        Bytecode length.
    """

    return len(
        get_bytecode(address)
    )


def is_contract(
    address: str,
) -> bool:
    """
    Determine whether an address is a smart contract.

    An address is classified as a contract if it has
    deployed bytecode.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    bool
        True if the address contains bytecode,
        otherwise False.
    """

    logger.info(
        "Checking if address is a contract."
    )

    try:
        bytecode = get_bytecode(address)

        is_contract_ = (
            bytecode is not None
            and len(bytecode) > 0
            and bytecode != b""
            and bytecode != b"0x"
        )

        logger.info(
            f"Contract detection result: {is_contract_}"
        )

        return is_contract_

    except Exception as error:
        logger.error(f"Error checking if address is contract: {error}")
        return False


###############################################################################
# Contract Detection Intelligence
###############################################################################


def is_erc20(
    address: str,
) -> bool:
    """
    Determine whether a contract implements
    the ERC-20 token standard.

    The contract is considered ERC-20 compatible
    if the required metadata and supply functions
    execute successfully.

    Parameters
    ----------
    address : str
        Ethereum contract address.

    Returns
    -------
    bool
        True if the contract appears to implement
        the ERC-20 standard, otherwise False.
    """

    logger.info(
        "Checking ERC-20 compatibility."
    )

    try:

        contract = _get_contract(
            address,
            ERC20_ABI,
        )

        required_functions = [

            contract.functions.name(),

            contract.functions.symbol(),

            contract.functions.decimals(),

            contract.functions.totalSupply(),

        ]

        for function in required_functions:

            if _safe_call(function) is None:

                logger.debug(
                    "ERC-20 compatibility check failed."
                )

                return False

        logger.info(
            "ERC-20 compatibility confirmed."
        )

        return True

    except Exception as error:

        logger.debug(
            f"ERC-20 detection failed: {error}"
        )

        return False


def is_erc721(
    address: str,
) -> bool:
    """
    Determine whether a contract implements
    the ERC-721 NFT standard.

    Parameters
    ----------
    address : str
        Ethereum contract address.

    Returns
    -------
    bool
        True if the contract appears to implement
        the ERC-721 standard, otherwise False.
    """

    logger.info(
        "Checking ERC-721 compatibility."
    )

    try:

        # Check for ERC-721 interface via ERC-165
        contract = _get_contract(
            address,
            ERC165_ABI,
        )

        supports_interface = contract.functions.supportsInterface(
            ERC721_INTERFACE_ID
        )

        if _safe_call(supports_interface) is True:

            logger.info(
                "ERC-721 compatibility confirmed via ERC-165."
            )

            return True

        return False

    except Exception as error:

        logger.debug(
            f"ERC-721 detection failed: {error}"
        )

        return False


def is_erc1155(
    address: str,
) -> bool:
    """
    Determine whether a contract implements
    the ERC-1155 Multi-Token standard.

    Parameters
    ----------
    address : str
        Ethereum contract address.

    Returns
    -------
    bool
        True if the contract appears to implement
        the ERC-1155 standard, otherwise False.
    """

    logger.info(
        "Checking ERC-1155 compatibility."
    )

    try:

        # Check for ERC-1155 interface via ERC-165
        contract = _get_contract(
            address,
            ERC165_ABI,
        )

        supports_interface = contract.functions.supportsInterface(
            ERC1155_INTERFACE_ID
        )

        if _safe_call(supports_interface) is True:

            logger.info(
                "ERC-1155 compatibility confirmed via ERC-165."
            )

            return True

        return False

    except Exception as error:

        logger.debug(
            f"ERC-1155 detection failed: {error}"
        )

        return False


def is_eip7702_delegated(
    address: str,
) -> bool:
    """
    Determine whether an address has been delegated
    under EIP-7702.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    bool
        True if the address contains EIP-7702
        delegation bytecode.
    """

    logger.info(
        "Checking EIP-7702 delegation."
    )

    bytecode = get_bytecode(address)

    if bytecode is None or len(bytecode) < 3:

        return False

    is_delegated = bytecode[:3] == EIP7702_PREFIX

    logger.info(
        f"EIP-7702 delegation result: {is_delegated}"
    )

    return is_delegated


def classify_address(
    address: str,
) -> str:
    """
    Classify an Ethereum address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    str
        Classification constant:
            EOA
            EOA_DELEGATED
            ERC20
            ERC721
            ERC1155
            CONTRACT
            UNKNOWN
    """

    logger.info(
        f"Classifying address: {address}"
    )

    _validate_address(address)

    # Check if it's a contract first
    if not is_contract(address):

        # Check for EIP-7702 delegation
        if is_eip7702_delegated(address):

            return EOA_DELEGATED

        return EOA

    # It's a contract - check token standards
    if is_erc20(address):

        return ERC20

    if is_erc721(address):

        return ERC721

    if is_erc1155(address):

        return ERC1155

    return CONTRACT


def get_contract_type(
    address: str,
) -> str:
    """
    Alias for classify_address.

    Parameters
    ----------
    address : str
        Ethereum address.

    Returns
    -------
    str
        Contract type classification.
    """

    return classify_address(address)