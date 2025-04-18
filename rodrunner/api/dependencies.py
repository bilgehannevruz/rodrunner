"""
Dependencies for the API.
"""
from typing import Dict, List, Optional, Union, Any
from functools import lru_cache
import asyncio

from fastapi import Depends, HTTPException, status
from prefect.client.orchestration import get_client as get_prefect_client
from prefect.client.schemas.filters import FlowRunFilter, DeploymentFilter

from rodrunner.config import get_config
from rodrunner.models.config import AppConfig, iRODSConfig, PrefectConfig
from rodrunner.irods.client import iRODSClient


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


def get_prefect_config(config: AppConfig = Depends(get_app_config)) -> PrefectConfig:
    """
    Get the Prefect configuration.

    Args:
        config: Application configuration

    Returns:
        Prefect configuration
    """
    return config.prefect


def get_irods_client(config: iRODSConfig = Depends(get_irods_config)) -> iRODSClient:
    """
    Get an iRODS client.

    Args:
        config: iRODS configuration

    Returns:
        iRODS client
    """
    return iRODSClient(config)
