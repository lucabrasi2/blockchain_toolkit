"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
providers.factory

Purpose
-------
Provider factory and provider lifecycle management.
===============================================================================
"""

from __future__ import annotations


import os

from typing import Dict, Type


from dotenv import load_dotenv

load_dotenv()


from web3 import Web3



from providers.base import (
    BaseProvider,
    ProviderType,
)



from providers.exceptions import (
    ProviderNotFoundError,
    ProviderConfigurationError,
    ProviderConnectionError,
)





###############################################################################
# Provider Factory
###############################################################################


class ProviderFactory:
    """
    Central provider creation system.
    """


    _providers: Dict[str, Type[BaseProvider]] = {}



    @classmethod
    def register(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
    ):

        if not name:

            raise ProviderConfigurationError(
                "Provider name required"
            )


        cls._providers[
            name.lower()
        ] = provider_class




    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
    ):

        cls.register(
            name,
            provider_class
        )




    @classmethod
    def create(
        cls,
        name: str = "default",
        config: dict | None = None,
        **kwargs,
    ):


        name = name.lower()



        if name not in cls._providers:

            raise ProviderNotFoundError(
                f"Provider '{name}' not found"
            )



        if config is None:

            config = {}



        if not isinstance(config, dict):

            raise ProviderConfigurationError(
                "Provider configuration must be dictionary"
            )



        config.update(kwargs)



        provider_class = cls._providers[name]



        return provider_class(
            **config
        )





    @classmethod
    def get_provider(
        cls,
        name: str | None = None,
        **kwargs,
    ):


        if name is None:

            name = "default"



        return cls.create(
            name,
            kwargs
        )





    @classmethod
    def supported_providers(
        cls,
    ):


        return list(
            cls._providers.keys()
        )




    @classmethod
    def available_providers(
        cls,
    ):


        return cls.supported_providers()




    @classmethod
    def info(
        cls,
    ):


        return {

            "supported_providers":
                cls.supported_providers(),

            "count":
                len(cls._providers),

        }





    @classmethod
    def clear(
        cls,
    ):

        cls._providers.clear()





###############################################################################
# Default Provider
###############################################################################


class DefaultProvider(
    BaseProvider
):


    def __init__(
        self,
        **kwargs,
    ):


        self.api_key = kwargs.get(
            "api_key"
        ) or os.getenv(
            "ALCHEMY_API_KEY"
        )


        self._network = kwargs.get(
            "network"
        ) or os.getenv(
            "ALCHEMY_NETWORK",
            "eth-mainnet"
        )


        self._web3 = None


        self.connect()




    @property
    def name(self):

        return "Default"



    @property
    def blockchain(self):

        return "Ethereum"



    @property
    def network(self):

        return self._network




    @property
    def provider_type(self):

        return ProviderType.RPC




    @property
    def http_url(self):


        if not self.api_key:

            return None



        return (
            "https://"
            f"{self.network}"
            ".g.alchemy.com/v2/"
            f"{self.api_key}"
        )




    @property
    def ws_url(self):

        return None




    def connect(self):


        if not self.http_url:

            return False



        try:

            self._web3 = Web3(
                Web3.HTTPProvider(
                    self.http_url
                )
            )


            return self.is_connected()



        except Exception as exc:


            raise ProviderConnectionError(
                str(exc)
            )





    def is_connected(self):


        if self._web3 is None:

            return False



        return self._web3.is_connected()




    def get_web3(self):

        return self._web3




    def health_check(self):

        return self.is_connected()




    def get_config(self):

        return {

            "name":
                self.name,

            "network":
                self.network,

            "blockchain":
                self.blockchain,

        }





    def info(self):

        return {

            **self.get_config(),

            "connected":
                self.is_connected(),

        }






###############################################################################
# Alchemy Provider
###############################################################################


class AlchemyProvider(
    DefaultProvider
):


    def __init__(
        self,
        **kwargs,
    ):


        api_key = kwargs.get(
            "api_key"
        )


        if not api_key:

            raise ProviderConfigurationError(
                "Alchemy API key required"
            )



        super().__init__(
            **kwargs
        )




    @property
    def name(self):

        return "Alchemy"







###############################################################################
# Infura Provider
###############################################################################


class InfuraProvider(
    DefaultProvider
):


    def __init__(
        self,
        **kwargs,
    ):


        self.project_id = kwargs.get(
            "project_id"
        )



        if not self.project_id:

            raise ProviderConfigurationError(
                "Infura project ID required"
            )



        self._network = kwargs.get(
            "network",
            "mainnet"
        )


        self.api_key = self.project_id


        self._web3 = None


        self.connect()




    @property
    def name(self):

        return "Infura"





    @property
    def http_url(self):


        return (
            "https://mainnet.infura.io/v3/"
            f"{self.project_id}"
        )







###############################################################################
# Registration
###############################################################################


ProviderFactory.register_provider(
    "default",
    DefaultProvider
)


ProviderFactory.register_provider(
    "alchemy",
    AlchemyProvider
)


ProviderFactory.register_provider(
    "infura",
    InfuraProvider
)




__all__ = [

    "ProviderFactory",

    "DefaultProvider",

    "AlchemyProvider",

    "InfuraProvider",

]