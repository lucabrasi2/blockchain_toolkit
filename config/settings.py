"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
config.settings

Purpose
-------
Central configuration management for UBP.

Loads environment variables and exposes
typed application settings.

Architecture
------------
UBP Enterprise Configuration Framework


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

from pathlib import Path

from dotenv import load_dotenv


from core.logger import get_logger



logger = get_logger(__name__)




###############################################################################
# Environment Loading
###############################################################################


BASE_DIR = Path(__file__).resolve().parent.parent



ENV_FILE = BASE_DIR / ".env"



if ENV_FILE.exists():

    load_dotenv(
        ENV_FILE
    )

    logger.info(
        "Environment configuration loaded."
    )

else:

    logger.warning(
        ".env file not found."
    )




###############################################################################
# Application Settings
###############################################################################


class Settings:
    """
    Global UBP configuration.

    All modules should import settings
    from this class instead of reading
    environment variables directly.
    """



    ###########################################################################
    # Application
    ###########################################################################


    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Universal_Blockchain_Platform",
    )


    APP_ENV: str = os.getenv(
        "APP_ENV",
        "development",
    )


    APP_DEBUG: bool = (
        os.getenv(
            "APP_DEBUG",
            "false",
        ).lower()
        == "true"
    )


    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "2.0",
    )
    
    ###########################################################################
    # Logging Configuration
    ###########################################################################

    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )



    ###########################################################################
    # Alchemy Configuration
    ###########################################################################

    ALCHEMY_API_KEY: str = os.getenv(
        "ALCHEMY_API_KEY",
        "",
    )


    ALCHEMY_NETWORK: str = os.getenv(
        "ALCHEMY_NETWORK",
        "eth-mainnet",
    )



    ###########################################################################
    # Infura Configuration
    ###########################################################################

    INFURA_PROJECT_ID: str = os.getenv(
        "INFURA_PROJECT_ID",
        "",
    )


    INFURA_NETWORK: str = os.getenv(
        "INFURA_NETWORK",
        "mainnet",
    )



    ###########################################################################
    # Provider Manager Configuration
    ###########################################################################

    PRIMARY_PROVIDER: str = os.getenv(
        "PRIMARY_PROVIDER",
        "alchemy",
    )


    BACKUP_PROVIDER: str = os.getenv(
        "BACKUP_PROVIDER",
        "infura",
    )



    AUTO_FAILOVER: bool = (
        os.getenv(
            "AUTO_FAILOVER",
            "true",
        ).lower()
        == "true"
    )



    HEALTH_CHECK_INTERVAL: int = int(
        os.getenv(
            "HEALTH_CHECK_INTERVAL",
            "60",
        )
    )



    ###########################################################################
    # Ethereum Configuration
    ###########################################################################

    ETH_CHAIN_ID: int = int(
        os.getenv(
            "ETH_CHAIN_ID",
            "1",
        )
    )


    ETH_CONFIRMATIONS: int = int(
        os.getenv(
            "ETH_CONFIRMATIONS",
            "12",
        )
    )
    
    ###########################################################################
    # Database Configuration
    ###########################################################################

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///ubp.db",
    )



    ###########################################################################
    # Security Configuration
    ###########################################################################

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "",
    )


    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "",
    )


    JWT_EXPIRATION_MINUTES: int = int(
        os.getenv(
            "JWT_EXPIRATION_MINUTES",
            "60",
        )
    )



    ###########################################################################
    # Web Server Configuration
    ###########################################################################

    HOST: str = os.getenv(
        "HOST",
        "0.0.0.0",
    )


    PORT: int = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )



    ###########################################################################
    # WebSocket Configuration
    ###########################################################################

    ENABLE_WEBSOCKETS: bool = (
        os.getenv(
            "ENABLE_WEBSOCKETS",
            "true",
        ).lower()
        == "true"
    )



    ###########################################################################
    # Development Configuration
    ###########################################################################

    ENABLE_TEST_MODE: bool = (
        os.getenv(
            "ENABLE_TEST_MODE",
            "false",
        ).lower()
        == "true"
    )



    ###########################################################################
    # Validation
    ###########################################################################

    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration.

        Returns
        -------
        bool
            True if configuration is usable.
        """


        required = [

            "APP_NAME",

            "APP_ENV",

        ]


        for item in required:

            if not getattr(
                cls,
                item,
                None,
            ):

                logger.error(
                    "Missing configuration: %s",
                    item,
                )

                return False



        logger.info(
            "Configuration validation successful."
        )


        return True



    ###########################################################################
    # Information Export
    ###########################################################################

    @classmethod
    def info(cls) -> dict:
        """
        Return safe configuration information.

        Secrets are excluded.
        """

        return {

            "app_name":
                cls.APP_NAME,

            "environment":
                cls.APP_ENV,

            "version":
                cls.APP_VERSION,

            "primary_provider":
                cls.PRIMARY_PROVIDER,

            "backup_provider":
                cls.BACKUP_PROVIDER,

            "auto_failover":
                cls.AUTO_FAILOVER,

            "websocket_enabled":
                cls.ENABLE_WEBSOCKETS,

        }




###############################################################################
# Global Settings Instance
###############################################################################


settings = Settings()



###############################################################################
# End of File
###############################################################################