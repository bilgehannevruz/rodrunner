"""
Configuration management for the irods_prefect package.
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional, Union, Any

# BaseSettings has been moved to pydantic-settings in Pydantic v2
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for Pydantic v1
    from pydantic import BaseSettings
from dotenv import load_dotenv

from irods_prefect.models.config import AppConfig, iRODSConfig, SequencerConfig


# Load environment variables from .env file if it exists
load_dotenv()


def load_config_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        file_path: Path to the configuration file

    Returns:
        Dictionary containing the configuration
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def get_config(config_file: Optional[str] = None) -> AppConfig:
    """
    Get the application configuration.

    Args:
        config_file: Path to the configuration file (optional)

    Returns:
        AppConfig object
    """
    # Start with environment variables
    config_data = {}

    # Load from file if provided
    if config_file and os.path.exists(config_file):
        file_config = load_config_from_file(config_file)
        config_data.update(file_config)

    # Create the config object
    # If any required fields are missing, this will raise a validation error
    try:
        return AppConfig(**config_data)
    except Exception as e:
        # If we're missing required fields, try to provide helpful error message
        missing_fields = []
        if 'irods' not in config_data:
            missing_fields.append("irods configuration")
        elif not isinstance(config_data['irods'], dict):
            missing_fields.append("valid irods configuration")

        if 'sequencer' not in config_data:
            missing_fields.append("sequencer configuration")
        elif not isinstance(config_data['sequencer'], dict):
            missing_fields.append("valid sequencer configuration")

        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}") from e

        # If it's some other validation error, re-raise
        raise
