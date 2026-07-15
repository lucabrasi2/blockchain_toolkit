"""
Universal Blockchain Platform (UBP)

Module:
    Input Handler

Purpose:
    Handle user input for the application.

Responsibilities:
    • Get and validate address input
    • Get and validate block input
    • Get and validate transaction hash
    • Get and validate numeric input
    • Provide input prompts
    • Input validation and sanitization

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from typing import Optional, Union
import re

from core.display.utils import print_error, print_info, print_warning


def get_address_input(prompt: str = "Enter address") -> Optional[str]:
    """
    Get and validate an address input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[str]
        Validated address or None if canceled.
    """
    print()
    address = input(f"{prompt}: ").strip()

    if not address:
        print_error("Address cannot be empty.")
        return None

    # Basic validation (0x prefix for Ethereum)
    if address.startswith("0x"):
        if len(address) != 42:
            print_error("Invalid Ethereum address format. Should be 42 characters including 0x.")
            return None
        # Check if it's valid hex
        try:
            int(address[2:], 16)
        except ValueError:
            print_error("Invalid Ethereum address. Contains non-hex characters.")
            return None
    else:
        print_info("Address format not recognized. Proceeding anyway...")

    return address


def get_block_input(prompt: str = "Enter block number") -> Optional[Union[int, str]]:
    """
    Get and validate a block number input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[Union[int, str]]
        Validated block number as int, 'latest' string, or None if canceled.
    """
    print()
    block_input = input(f"{prompt}: ").strip()

    if not block_input:
        print_error("Block number cannot be empty.")
        return None

    # Check for 'latest' keyword
    if block_input.lower() in ["latest", "pending", "earliest"]:
        return block_input.lower()

    try:
        block_number = int(block_input)
        if block_number < 0:
            print_error("Block number must be positive.")
            return None
        return block_number
    except ValueError:
        print_error("Invalid block number. Please enter a number or 'latest'.")
        return None


def get_transaction_hash(prompt: str = "Enter transaction hash") -> Optional[str]:
    """
    Get and validate a transaction hash input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[str]
        Validated transaction hash or None if canceled.
    """
    print()
    tx_hash = input(f"{prompt}: ").strip()

    if not tx_hash:
        print_error("Transaction hash cannot be empty.")
        return None

    # Basic validation (0x prefix and 64 hex characters for Ethereum)
    if tx_hash.startswith("0x"):
        if not re.match(r"^0x[a-fA-F0-9]{64}$", tx_hash):
            print_warning("Transaction hash format may be invalid.")
            # Don't return None, let user decide if they want to proceed
            proceed = get_yes_no("Do you want to proceed anyway?")
            if not proceed:
                return None
            return tx_hash
    else:
        # Try without 0x prefix
        if re.match(r"^[a-fA-F0-9]{64}$", tx_hash):
            tx_hash = "0x" + tx_hash
            print_info(f"Added 0x prefix: {tx_hash}")
        else:
            print_warning("Transaction hash format may be invalid.")
            proceed = get_yes_no("Do you want to proceed anyway?")
            if not proceed:
                return None

    return tx_hash


def get_token_address(prompt: str = "Enter token address") -> Optional[str]:
    """
    Get and validate a token address input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[str]
        Validated token address or None if canceled.
    """
    return get_address_input(prompt)


def get_choice_input(
    prompt: str = "Enter your choice",
    min_choice: int = 1,
    max_choice: int = 10,
    allow_back: bool = True
) -> Optional[int]:
    """
    Get and validate a numeric choice input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.
    min_choice : int, optional
        Minimum valid choice.
    max_choice : int, optional
        Maximum valid choice.
    allow_back : bool, optional
        Whether to allow '0' as back option.

    Returns
    -------
    Optional[int]
        Validated choice or None if canceled.
    """
    print()
    choice = input(f"{prompt}: ").strip()

    if not choice:
        print_error("Choice cannot be empty.")
        return None

    try:
        choice_num = int(choice)
        if allow_back and choice_num == 0:
            return 0
        if choice_num < min_choice or choice_num > max_choice:
            print_error(f"Please enter a number between {min_choice} and {max_choice}.")
            return None
        return choice_num
    except ValueError:
        print_error("Invalid input. Please enter a number.")
        return None


def get_yes_no(prompt: str = "Continue?") -> bool:
    """
    Get a yes/no confirmation.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    bool
        True if user confirms, False otherwise.
    """
    print()
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ["y", "yes"]


def get_text_input(prompt: str = "Enter text", allow_empty: bool = False) -> Optional[str]:
    """
    Get text input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.
    allow_empty : bool, optional
        Whether to allow empty input.

    Returns
    -------
    Optional[str]
        Input text or None if canceled.
    """
    print()
    text = input(f"{prompt}: ").strip()

    if not text and not allow_empty:
        print_error("Input cannot be empty.")
        return None

    return text if text else None


def get_network_input(prompt: str = "Select network") -> Optional[str]:
    """
    Get network selection.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[str]
        Selected network or None if canceled.
    """
    print()
    print_info("Available networks: mainnet, goerli, sepolia, local")
    network = input(f"{prompt}: ").strip().lower()

    if not network:
        print_error("Network cannot be empty.")
        return None

    valid_networks = ["mainnet", "goerli", "sepolia", "local", "main", "testnet", "dev"]
    if network not in valid_networks:
        print_warning(f"Network '{network}' may not be valid.")
        proceed = get_yes_no("Do you want to proceed anyway?")
        if not proceed:
            return None

    return network


def get_provider_input(prompt: str = "Select provider") -> Optional[str]:
    """
    Get provider selection.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.

    Returns
    -------
    Optional[str]
        Selected provider or None if canceled.
    """
    print()
    print_info("Available providers: alchemy, infura, quicknode, ankr, local")
    provider = input(f"{prompt}: ").strip().lower()

    if not provider:
        print_error("Provider cannot be empty.")
        return None

    valid_providers = ["alchemy", "infura", "quicknode", "ankr", "local", "auto"]
    if provider not in valid_providers:
        print_warning(f"Provider '{provider}' may not be valid.")
        proceed = get_yes_no("Do you want to proceed anyway?")
        if not proceed:
            return None

    return provider


def get_int_input(prompt: str = "Enter a number", min_val: int = None, max_val: int = None) -> Optional[int]:
    """
    Get and validate an integer input.

    Parameters
    ----------
    prompt : str, optional
        Prompt to display to the user.
    min_val : int, optional
        Minimum allowed value.
    max_val : int, optional
        Maximum allowed value.

    Returns
    -------
    Optional[int]
        Validated integer or None if canceled.
    """
    print()
    value = input(f"{prompt}: ").strip()

    if not value:
        print_error("Value cannot be empty.")
        return None

    try:
        int_val = int(value)
        if min_val is not None and int_val < min_val:
            print_error(f"Value must be at least {min_val}.")
            return None
        if max_val is not None and int_val > max_val:
            print_error(f"Value must be at most {max_val}.")
            return None
        return int_val
    except ValueError:
        print_error("Invalid input. Please enter a number.")
        return None


# Convenience functions
def get_eth_address(prompt: str = "Enter Ethereum address") -> Optional[str]:
    """Get an Ethereum address."""
    return get_address_input(prompt)


def get_btc_address(prompt: str = "Enter Bitcoin address") -> Optional[str]:
    """Get a Bitcoin address."""
    print()
    address = input(f"{prompt}: ").strip()

    if not address:
        print_error("Address cannot be empty.")
        return None

    # Simple Bitcoin address validation (basic format check)
    if not (address.startswith("1") or address.startswith("3") or address.startswith("bc1")):
        print_warning("This may not be a valid Bitcoin address format.")
        proceed = get_yes_no("Do you want to proceed anyway?")
        if not proceed:
            return None

    return address


def get_tron_address(prompt: str = "Enter TRON address") -> Optional[str]:
    """Get a TRON address."""
    print()
    address = input(f"{prompt}: ").strip()

    if not address:
        print_error("Address cannot be empty.")
        return None

    # Simple TRON address validation (T-prefix or 0x-prefix)
    if not (address.startswith("T") or address.startswith("0x")):
        print_warning("This may not be a valid TRON address format.")
        proceed = get_yes_no("Do you want to proceed anyway?")
        if not proceed:
            return None

    return address
