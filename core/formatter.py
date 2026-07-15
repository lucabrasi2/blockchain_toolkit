"""
Universal Blockchain Platform (UBP)

Version : 2.0.0
Module  : Formatter
Author  : Jaramogi Diddy

Shared formatting utilities used throughout UBP.
"""

from datetime import datetime, UTC
from decimal import Decimal


class Formatter:
    """
    Shared formatting helper for UBP.
    """

    # ==========================================================
    # REPORT FORMATTING
    # ==========================================================

    @staticmethod
    def title(title: str) -> str:
        """
        Return a formatted report title.
        """

        line = "=" * 50

        return (
            f"\n{line}\n"
            f"{title.center(50)}\n"
            f"{line}"
        )

    @staticmethod
    def section(title: str) -> str:
        """
        Return a formatted report section.
        """

        line = "-" * 50

        return (
            f"\n{title}\n"
            f"{line}"
        )

    @staticmethod
    def field(
        label: str,
        value,
        width: int = 20,
    ) -> str:
        """
        Format a report field.
        """

        return f"{label:<{width}}: {value}"

    @staticmethod
    def blank() -> str:
        """
        Return a blank line.
        """

        return ""

    # ==========================================================
    # STATUS MESSAGES
    # ==========================================================

    @staticmethod
    def success(message: str) -> str:
        """
        Format a success message.
        """

        return f"✅ {message}"

    @staticmethod
    def warning(message: str) -> str:
        """
        Format a warning message.
        """

        return f"⚠️ {message}"

    @staticmethod
    def error(message: str) -> str:
        """
        Format an error message.
        """

        return f"❌ {message}"

    # ==========================================================
    # NUMBER FORMATTING
    # ==========================================================

    @staticmethod
    def format_number(value) -> str:
        """
        Format numeric values using commas.
        """

        return f"{value:,}"

    @staticmethod
    def format_eth(value) -> str:
        """
        Format Ether values.
        """

        return (
            f"{Decimal(value):,.6f} ETH"
        )

    @staticmethod
    def format_gwei(value) -> str:
        """
        Format Wei into Gwei.
        """

        gwei = (
            Decimal(value)
            / Decimal(1_000_000_000)
        )

        return f"{gwei:,.3f} Gwei"

    @staticmethod
    def format_percentage(value) -> str:
        """
        Format percentage values.
        """

        return f"{Decimal(value):.2f}%"

    @staticmethod
    def format_bytes(size: int) -> str:
        """
        Format byte values.
        """

        return (
            f"{Formatter.format_number(size)} bytes"
        )

    # ==========================================================
    # DATE & TIME
    # ==========================================================

    @staticmethod
    def format_timestamp(
        timestamp: int,
    ) -> str:
        """
        Convert Unix timestamp into UTC.
        """

        return datetime.fromtimestamp(
            timestamp,
            tz=UTC,
        ).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

    # ==========================================================
    # BLOCKCHAIN HELPERS
    # ==========================================================

    @staticmethod
    def shorten_hash(
        value: str,
        start: int = 10,
        end: int = 8,
    ) -> str:
        """
        Shorten long hashes.
        """

        if len(value) <= start + end:

            return value

        return (
            f"{value[:start]}..."
            f"{value[-end:]}"
        )

    @staticmethod
    def shorten_address(
        address: str,
    ) -> str:
        """
        Shorten Ethereum addresses.
        """

        return Formatter.shorten_hash(
            address,
            start=10,
            end=6,
        )

    # ==========================================================
    # BOOLEAN HELPERS
    # ==========================================================

    @staticmethod
    def yes_no(value: bool) -> str:
        """
        Convert boolean to YES or NO.
        """

        return (
            "YES"
            if value
            else "NO"
        )

    @staticmethod
    def enabled_disabled(value: bool) -> str:
        """
        Convert boolean to Enabled/Disabled.
        """

        return (
            "Enabled"
            if value
            else "Disabled"
        )