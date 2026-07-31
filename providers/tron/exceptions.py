"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.tron.exceptions

Purpose
-------
TRON provider exceptions.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

from providers.exceptions import ProviderError


class TronProviderError(ProviderError):
    """Base TRON provider exception."""
    pass


class TronConnectionError(TronProviderError):
    """TRON connection error."""
    pass


class TronConfigurationError(TronProviderError):
    """TRON configuration error."""
    pass


###############################################################################
# End of File
###############################################################################