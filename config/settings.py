"""
Universal Blockchain Platform (UBP)

Module:
    Settings Configuration

Purpose:
    Manage application configuration and
    environment settings for the UBP platform.

Responsibilities:
    • Load environment variables
    • Provide configuration defaults
    • Manage network settings
    • Manage provider settings
    • Validate configuration

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from core.logger import get_logger


logger = get_logger(__name__)


class Settings:
    """
    Application settings manager.
    """

    def __init__(self, env_file: str = ".env"):
        """
        Initialize settings from environment variables.

        Parameters
        ----------
        env_file : str, optional
            Path to the .env file.
        """
        self.env_file = env_file
        self._load_env()
        self._initialize_settings()

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        try:
            if os.path.exists(self.env_file):
                load_dotenv(self.env_file)
                logger.info(f"Loaded environment from {self.env_file}")
            else:
                logger.warning(f"{self.env_file} not found. Using defaults.")
        except Exception as error:
            logger.error(f"Error loading environment: {error}")

    def _initialize_settings(self) -> None:
        """Initialize all settings with defaults or environment values."""
        # Network Settings
        self.network = os.getenv("NETWORK", "mainnet")
        self.chain_id = int(os.getenv("CHAIN_ID", "1"))
        
        # RPC Settings
        self.rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")
        self.rpc_timeout = int(os.getenv("RPC_TIMEOUT", "30"))
        self.rpc_retries = int(os.getenv("RPC_RETRIES", "3"))
        
        # Provider Settings
        self.provider = os.getenv("PROVIDER", "auto")
        self.provider_api_key = os.getenv("PROVIDER_API_KEY", "")
        
        # Database Settings
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///ubp.db")
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", "5"))
        
        # Logging Settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/ubp.log")
        
        # Application Settings
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Security Settings
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
        self.encryption_enabled = os.getenv("ENCRYPTION_ENABLED", "False").lower() == "true"
        
        logger.info("Settings initialized successfully.")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting by key.

        Parameters
        ----------
        key : str
            Setting key.
        default : Any, optional
            Default value if key doesn't exist.

        Returns
        -------
        Any
            Setting value.
        """
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting by key.

        Parameters
        ----------
        key : str
            Setting key.
        value : Any
            Setting value.
        """
        setattr(self, key, value)
        logger.debug(f"Set {key} = {value}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.

        Returns
        -------
        Dict[str, Any]
            All settings as a dictionary.
        """
        return {
            "network": self.network,
            "chain_id": self.chain_id,
            "rpc_url": self.rpc_url,
            "rpc_timeout": self.rpc_timeout,
            "rpc_retries": self.rpc_retries,
            "provider": self.provider,
            "provider_api_key": self.provider_api_key,
            "database_url": self.database_url,
            "database_pool_size": self.database_pool_size,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "debug": self.debug,
            "environment": self.environment,
            "secret_key": self.secret_key,
            "encryption_enabled": self.encryption_enabled,
        }

    def validate(self) -> bool:
        """
        Validate settings.

        Returns
        -------
        bool
            True if all settings are valid.
        """
        valid = True

        # Validate network
        valid_networks = ["mainnet", "goerli", "sepolia", "local", "main", "testnet", "dev"]
        if self.network not in valid_networks:
            logger.warning(f"Unknown network: {self.network}")
            valid = False

        # Validate RPC URL
        if not self.rpc_url or self.rpc_url == "https://mainnet.infura.io/v3/YOUR_INFURA_KEY":
            logger.warning("RPC URL not set or using default placeholder.")
            valid = False

        # Validate timeout
        if self.rpc_timeout < 1 or self.rpc_timeout > 300:
            logger.warning(f"Invalid RPC timeout: {self.rpc_timeout}")
            valid = False

        return valid

    def get_network_config(self) -> Dict[str, Any]:
        """
        Get network-specific configuration.

        Returns
        -------
        Dict[str, Any]
            Network configuration.
        """
        network_configs = {
            "mainnet": {
                "chain_id": 1,
                "name": "Ethereum Mainnet",
                "currency": "ETH",
                "explorer": "https://etherscan.io",
            },
            "goerli": {
                "chain_id": 5,
                "name": "Goerli Testnet",
                "currency": "ETH",
                "explorer": "https://goerli.etherscan.io",
            },
            "sepolia": {
                "chain_id": 11155111,
                "name": "Sepolia Testnet",
                "currency": "ETH",
                "explorer": "https://sepolia.etherscan.io",
            },
            "local": {
                "chain_id": 1337,
                "name": "Local Network",
                "currency": "ETH",
                "explorer": "http://localhost:8545",
            },
        }
        return network_configs.get(self.network, network_configs["mainnet"])

    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get provider-specific configuration.

        Returns
        -------
        Dict[str, Any]
            Provider configuration.
        """
        provider_configs = {
            "alchemy": {
                "url_template": "https://{network}.g.alchemy.com/v2/{api_key}",
                "websocket_template": "wss://{network}.g.alchemy.com/v2/{api_key}",
            },
            "infura": {
                "url_template": "https://{network}.infura.io/v3/{api_key}",
                "websocket_template": "wss://{network}.infura.io/ws/v3/{api_key}",
            },
            "quicknode": {
                "url_template": "https://{network}.quicknode.com/v1/{api_key}",
                "websocket_template": "wss://{network}.quicknode.com/v1/{api_key}",
            },
            "ankr": {
                "url_template": "https://rpc.ankr.com/{network}/{api_key}",
                "websocket_template": "wss://rpc.ankr.com/{network}/{api_key}",
            },
            "local": {
                "url_template": "http://localhost:8545",
                "websocket_template": "ws://localhost:8545",
            },
        }
        return provider_configs.get(self.provider, provider_configs["local"])


# For backward compatibility
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings instance.

    Returns
    -------
    Settings
        Settings instance.
    """
    return settings