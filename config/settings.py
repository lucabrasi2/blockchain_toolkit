"""
Application settings.

This module loads configuration from the .env file
and validates that all required settings exist.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ALCHEMY_HTTP_URL = os.getenv("ALCHEMY_HTTP_URL")
ALCHEMY_WS_URL = os.getenv("ALCHEMY_WS_URL")


def validate_settings():
    """Ensure required settings are present."""

    if not ALCHEMY_HTTP_URL:
        raise ValueError("Missing ALCHEMY_HTTP_URL in .env")

    if not ALCHEMY_WS_URL:
        raise ValueError("Missing ALCHEMY_WS_URL in .env")