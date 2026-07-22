"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
tests.test_providers

Purpose
-------
Integration tests for the UBP provider framework.

Tests:

- ProviderFactory
- AlchemyProvider
- InfuraProvider
- ProviderManager
- Provider registration


Architecture
------------
UBP Enterprise Connectivity Framework


Author
------
Jaramogi Diddy


Platform
--------
Universal Blockchain Platform (UBP)


Version
-------
2.0 Enterprise
===============================================================================
"""


from __future__ import annotations



import os



from providers.factory import ProviderFactory

from providers.manager import ProviderManager

from providers.exceptions import (
    ProviderError,
)



from core.logger import get_logger



logger = get_logger(__name__)




###############################################################################
# Test Configuration
###############################################################################


ALCHEMY_KEY = os.getenv(
    "ALCHEMY_API_KEY",
)


INFURA_ID = os.getenv(
    "INFURA_PROJECT_ID",
)





###############################################################################
# Factory Tests
###############################################################################


def test_supported_providers():
    """
    Verify provider discovery.
    """

    providers = (
        ProviderFactory.supported_providers()
    )


    assert "alchemy" in providers

    assert "infura" in providers



def test_factory_information():
    """
    Verify factory metadata.
    """

    info = (
        ProviderFactory.info()
    )


    assert (
        "supported_providers"
        in info
    )

###############################################################################
# Provider Creation Tests
###############################################################################


def test_create_alchemy_provider():
    """
    Verify Alchemy provider creation.
    """

    if not ALCHEMY_KEY:

        logger.warning(
            "Skipping Alchemy test. "
            "ALCHEMY_API_KEY not configured."
        )

        return



    provider = ProviderFactory.create(
        "alchemy",
        {
            "api_key": ALCHEMY_KEY,

            "network": "eth-mainnet",
        }
    )



    assert provider.name == "Alchemy"

    assert provider.blockchain == "Ethereum"

    assert provider.network == "eth-mainnet"



def test_create_infura_provider():
    """
    Verify Infura provider creation.
    """

    if not INFURA_ID:

        logger.warning(
            "Skipping Infura test. "
            "INFURA_PROJECT_ID not configured."
        )

        return



    provider = ProviderFactory.create(
        "infura",
        {
            "project_id": INFURA_ID,

            "network": "mainnet",
        }
    )



    assert provider.name == "Infura"

    assert provider.blockchain == "Ethereum"

    assert provider.network == "mainnet"





###############################################################################
# Configuration Validation Tests
###############################################################################


def test_invalid_alchemy_configuration():
    """
    Verify missing Alchemy credentials fail.
    """

    try:

        ProviderFactory.create(
            "alchemy",
            {}
        )


        assert False



    except ProviderError:

        assert True




def test_invalid_infura_configuration():
    """
    Verify missing Infura credentials fail.
    """

    try:

        ProviderFactory.create(
            "infura",
            {}
        )


        assert False



    except ProviderError:

        assert True

###############################################################################
# Provider Manager Tests
###############################################################################


def test_provider_manager_registration():
    """
    Verify providers can be registered
    with ProviderManager.
    """

    manager = ProviderManager()



    if ALCHEMY_KEY:

        alchemy = ProviderFactory.create(
            "alchemy",
            {
                "api_key": ALCHEMY_KEY,

                "network": "eth-mainnet",
            }
        )


        manager.register_provider(
            "alchemy",
            alchemy,
            default=True,
        )



    if INFURA_ID:

        infura = ProviderFactory.create(
            "infura",
            {
                "project_id": INFURA_ID,

                "network": "mainnet",
            }
        )


        manager.register_provider(
            "infura",
            infura,
        )



    providers = (
        manager.list_providers()
    )


    assert isinstance(
        providers,
        list,
    )





def test_active_provider_selection():
    """
    Verify active provider switching.
    """

    manager = ProviderManager()



    if not ALCHEMY_KEY:

        logger.warning(
            "Skipping active provider test."
        )

        return



    provider = ProviderFactory.create(
        "alchemy",
        {
            "api_key": ALCHEMY_KEY,

            "network": "eth-mainnet",
        }
    )



    manager.register_provider(
        "alchemy",
        provider,
        default=True,
    )



    active = (
        manager.get_active_provider()
    )


    assert (
        active.name == "Alchemy"
    )





###############################################################################
# Health Check Tests
###############################################################################


def test_provider_health_check():
    """
    Verify provider health monitoring.
    """

    if not ALCHEMY_KEY:

        logger.warning(
            "Skipping health check. "
            "ALCHEMY_API_KEY missing."
        )

        return



    provider = ProviderFactory.create(
        "alchemy",
        {
            "api_key": ALCHEMY_KEY,

            "network": "eth-mainnet",
        }
    )



    status = (
        provider.health_check()
    )


    assert isinstance(
        status,
        bool,
    )





###############################################################################
# Test Runner
###############################################################################


if __name__ == "__main__":

    test_supported_providers()

    test_factory_information()

    test_create_alchemy_provider()

    test_create_infura_provider()

    test_invalid_alchemy_configuration()

    test_invalid_infura_configuration()

    test_provider_manager_registration()

    test_active_provider_selection()

    test_provider_health_check()


    print(
        "UBP Provider tests completed."
    )



###############################################################################
# End of File
###############################################################################