"""
Universal Blockchain Platform (UBP)

Module:
    Display Utilities

Purpose:
    Common display utilities for
    consistent formatting across the platform.

Responsibilities:
    • Clear terminal screen
    • Print formatted headers
    • Print dividers
    • Color-coded messages
    • Table formatting
    • Address and balance formatting

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
import sys
from typing import Optional, List, Any


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal formatting."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header(text: str, char: str = "=", length: int = 60) -> None:
    """
    Print a formatted header.

    Parameters
    ----------
    text : str
        Header text to display.
    char : str, optional
        Character to use for the divider.
    length : int, optional
        Length of the divider line.
    """
    print(char * length)
    print(f"  {text}")
    print(char * length)
    print()


def print_divider(char: str = "-", length: int = 40) -> None:
    """Print a divider line."""
    print(char * length)


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}❌ Error: {message}{Colors.END}")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_bold(message: str) -> None:
    """Print a message in bold."""
    print(f"{Colors.BOLD}{message}{Colors.END}")


def format_address(address: str, truncate: bool = True) -> str:
    """
    Format an Ethereum address for display.

    Parameters
    ----------
    address : str
        Ethereum address.
    truncate : bool, optional
        Whether to truncate the address.

    Returns
    -------
    str
        Formatted address.
    """
    if not address:
        return "N/A"
    if truncate and len(address) > 10:
        return f"{address[:6]}...{address[-4:]}"
    return address


def format_balance(balance: float, decimals: int = 6) -> str:
    """
    Format a balance for display.

    Parameters
    ----------
    balance : float
        Balance to format.
    decimals : int, optional
        Number of decimal places.

    Returns
    -------
    str
        Formatted balance.
    """
    if balance is None:
        return "0.000000"
    return f"{balance:.{decimals}f}"


def format_wei(wei: int) -> str:
    """
    Format a Wei amount for display.

    Parameters
    ----------
    wei : int
        Amount in Wei.

    Returns
    -------
    str
        Formatted Wei amount with commas.
    """
    if wei is None:
        return "0"
    return f"{wei:,}"


def print_table(headers: List[str], rows: List[List[Any]], title: Optional[str] = None) -> None:
    """
    Print a formatted table.

    Parameters
    ----------
    headers : List[str]
        List of column headers.
    rows : List[List[Any]]
        List of rows, each row is a list of values.
    title : str, optional
        Table title.
    """
    if title:
        print_bold(title)
        print_divider()

    if not rows:
        print_info("No data to display.")
        return

    # Calculate column widths
    col_widths = [len(str(header)) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print headers
    header_line = " | ".join(
        str(header).ljust(col_widths[i])
        for i, header in enumerate(headers)
    )
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        row_line = " | ".join(
            str(cell).ljust(col_widths[i])
            for i, cell in enumerate(row)
        )
        print(row_line)

    print()


def print_key_value(key: str, value: Any, indent: int = 2) -> None:
    """
    Print a key-value pair in a formatted way.

    Parameters
    ----------
    key : str
        The key/label.
    value : Any
        The value to display.
    indent : int, optional
        Number of spaces to indent.
    """
    indent_str = " " * indent
    print(f"{indent_str}{key}: {value}")


def print_section(title: str, char: str = "-", length: int = 40) -> None:
    """
    Print a section title with a divider.

    Parameters
    ----------
    title : str
        Section title.
    char : str, optional
        Character to use for the divider.
    length : int, optional
        Length of the divider line.
    """
    print_bold(title)
    print_divider(char, length)


def print_json(data: dict, indent: int = 2) -> None:
    """
    Pretty print a dictionary as JSON-like output.

    Parameters
    ----------
    data : dict
        Dictionary to print.
    indent : int, optional
        Number of spaces to indent.
    """
    import json
    print(json.dumps(data, indent=indent, default=str))


def get_terminal_size() -> tuple:
    """
    Get the terminal size.

    Returns
    -------
    tuple
        (width, height) of the terminal.
    """
    try:
        import shutil
        return shutil.get_terminal_size()
    except Exception:
        return (80, 24)


def center_text(text: str, width: Optional[int] = None) -> str:
    """
    Center text within a given width.

    Parameters
    ----------
    text : str
        Text to center.
    width : int, optional
        Width to center within. Defaults to terminal width.

    Returns
    -------
    str
        Centered text.
    """
    if width is None:
        width = get_terminal_size()[0]
    return text.center(width)


# Backward compatibility aliases
print_warning = print_warning
print_error = print_error
print_info = print_info
print_success = print_success
print_bold = print_bold
