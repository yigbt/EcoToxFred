"""
Configuration Manager for EcoToxFred

This module provides a unified interface for accessing configuration values
across different runtime environments (Streamlit app, CLI, tests, etc.).

Configuration sources are checked in the following priority order:
1. Streamlit secrets (if running in Streamlit context)
2. Environment variables
3. Local .streamlit/secrets.toml file
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("ETF")

expected_keys = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD"
]

# Find the secrets.toml file
current_dir = Path(__file__).parent
secrets_file = current_dir / ".streamlit" / "secrets.toml"


class ConfigManager:
    """
    Manages configuration loading from multiple sources with automatic fallback.

    Provides a dictionary-like interface for accessing configuration values
    regardless of the runtime environment.
    """

    def __init__(self):
        """Initialize the configuration manager and load configuration."""
        logger.debug("ConfigManager: Initialising configuration manager")
        self._config: Dict[str, Any] = {}
        self._streamlit_available = False
        self._load_config()

    @staticmethod
    def _is_streamlit_running() -> bool:
        """
        Check if code is running in a Streamlit context.
        """
        try:
            # Try to import streamlit
            import streamlit as st

            # Check if we can access secrets (this will fail outside Streamlit runtime)
            # We do this by checking if the secrets singleton is properly initialized
            try:
                # This will work in Streamlit context
                # noinspection PyProtectedMember
                _ = st.secrets._secrets
                return True
            except (AttributeError, RuntimeError):
                # Either secrets not initialized or not in Streamlit runtime
                return False
        except ImportError:
            # Streamlit not installed
            return False

    @staticmethod
    def _load_streamlit_secrets() -> Dict[str, Any]:
        import streamlit as st

        # Convert Streamlit secrets to a regular dictionary
        return dict(st.secrets)

    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Returns:
            Dict containing configuration from environment variables
        """
        loaded_config = {}

        for key in expected_keys:
            value = os.environ.get(key)
            if value is not None:
                loaded_config[key] = value

        return loaded_config

    @staticmethod
    def _load_from_toml() -> Dict[str, Any]:
        try:
            import toml
        except ImportError:
            raise ImportError(
                "toml package is required for loading configuration from file. "
                "Install it with: pip install toml"
            )

        if not secrets_file.exists():
            raise FileNotFoundError(
                f"Secrets file not found at {secrets_file}. "
                f"Please create the file or set environment variables."
            )

        with open(secrets_file) as f:
            return toml.load(f)

    def _load_config(self) -> None:
        """
        Load configuration from available sources in priority order.

        Tries sources in order:
        1. Streamlit secrets (if available)
        2. Environment variables
        3. TOML file
        """
        # Try Streamlit first
        if self._is_streamlit_running():
            try:
                self._config = self._load_streamlit_secrets()
                self._streamlit_available = True
                logger.debug("ConfigManager: Loaded configuration from Streamlit secrets")
                return
            except Exception as e:
                logger.debug(f"Failed to load Streamlit secrets: {e}")

        # Try environment variables
        env_config = self._load_from_env()
        if env_config:
            # Check if we have all required keys
            if all(key in env_config for key in expected_keys):
                self._config = env_config
                logger.debug("ConfigManager: Loaded configuration from environment variables")
                return
            else:
                # Partial environment variables - will try to merge with TOML
                logger.debug("ConfigManager: Found partial configuration in environment variables")

        # Try TOML file
        try:
            toml_config = self._load_from_toml()
            # Merge with any partial environment variables (env vars take precedence)
            toml_config.update(env_config)
            self._config = toml_config
            logger.debug("ConfigManager: Loaded configuration from TOML file")
        except FileNotFoundError as e:
            if not env_config:
                raise RuntimeError(
                    "No configuration source available. Please either:\n"
                    "1. Run with Streamlit (streamlit run bot.py)\n"
                    "2. Set environment variables\n"
                    "3. Create .streamlit/secrets.toml file"
                ) from e
            else:
                # Use partial env config
                self._config = env_config
                logger.debug("Using partial configuration from environment variables. Some features may not work.")

    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value by key.
        """
        if key not in self._config:
            raise KeyError(
                f"Configuration key '{key}' not found. "
                f"Available keys: {list(self._config.keys())}"
            )
        return self._config[key]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with optional default.
        """
        return self._config.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self._config

    @property
    def is_streamlit(self) -> bool:
        """Check if the configuration was loaded from Streamlit."""
        return self._streamlit_available

    def keys(self):
        """Return configuration keys."""
        return self._config.keys()

    def items(self):
        """Return configuration items."""
        return self._config.items()

    def values(self):
        """Return configuration values."""
        return self._config.values()


# Create a singleton instance
config = ConfigManager()


# Convenience functions for backward compatibility
def get_config_value(key: str, default: Optional[Any] = None) -> Any:
    if default is None:
        return config[key]
    return config.get(key, default)


def has_config_value(key: str) -> bool:
    return key in config
