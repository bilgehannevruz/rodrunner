"""
Tests for the main module.
"""
import os
import pytest
import tempfile
from typing import Dict, Any

from fastapi.testclient import TestClient
from rodrunner.models.config import AppConfig


@pytest.mark.api
def test_api_root(api_client: TestClient) -> None:
    """Test the API root endpoint."""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the iRODS Prefect API"


@pytest.mark.api
def test_api_health(api_client: TestClient) -> None:
    """Test the API health endpoint."""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
