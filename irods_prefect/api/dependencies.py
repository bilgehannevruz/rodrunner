"""
Dependencies for the API.
"""
from typing import Dict, List, Optional, Union, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status

from irods_prefect.config import get_config
from irods_prefect.models.config import AppConfig, iRODSConfig
from irods_prefect.irods.client import iRODSClient


@lru_cache()
def get_app_config() -> AppConfig:
    """
    Get the application configuration.
    
    Returns:
        Application configuration
    """
    return get_config()


def get_irods_config(config: AppConfig = Depends(get_app_config)) -> iRODSConfig:
    """
    Get the iRODS configuration.
    
    Args:
        config: Application configuration
        
    Returns:
        iRODS configuration
    """
    return config.irods


def get_irods_client(config: iRODSConfig = Depends(get_irods_config)) -> iRODSClient:
    """
    Get an iRODS client.
    
    Args:
        config: iRODS configuration
        
    Returns:
        iRODS client
    """
    return iRODSClient(config)
