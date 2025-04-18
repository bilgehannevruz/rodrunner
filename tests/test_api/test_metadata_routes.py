"""
Tests for the metadata API routes.
"""
import os
import pytest
from typing import Dict, Any
import json

from fastapi.testclient import TestClient
from rodrunner.models.config import AppConfig
from rodrunner.irods.client import iRODSClient


@pytest.mark.api
def test_get_metadata_by_key(api_client: TestClient, irods_client: iRODSClient) -> None:
    """Test getting metadata by key."""
    # Create a test collection with metadata
    test_coll_name = f"/tempZone/home/rods/test_api_metadata_{os.getpid()}"
    
    try:
        # Create collection with metadata
        coll = irods_client.create_collection(test_coll_name)
        with irods_client.session() as session:
            coll = session.collections.get(test_coll_name)
            coll.metadata.add("test_key", "test_value")
            coll.metadata.add("run_id", "220101_M00001_0001_000000000-A1B2C")
            coll.metadata.add("instrument", "M00001")
        
        # Test the API endpoint
        response = api_client.get("/metadata/search?key=test_key&value=test_value")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Find our test collection in the results
        found = False
        for item in data:
            if item["path"] == test_coll_name:
                found = True
                assert item["metadata"]["test_key"] == "test_value"
                break
        
        assert found, "Test collection not found in results"
        
        # Test searching by a different key
        response = api_client.get("/metadata/search?key=run_id&value=220101_M00001_0001_000000000-A1B2C")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Test searching with a non-existent key
        response = api_client.get("/metadata/search?key=non_existent&value=value")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    finally:
        # Clean up
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name)


@pytest.mark.api
def test_get_object_metadata(api_client: TestClient, irods_client: iRODSClient, temp_dir: str) -> None:
    """Test getting metadata for a specific object."""
    # Create a test data object with metadata
    test_coll_name = f"/tempZone/home/rods/test_api_object_{os.getpid()}"
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    test_obj_path = f"{test_coll_name}/test_file.txt"
    
    try:
        # Create a test file
        with open(test_file_path, "w") as f:
            f.write("Test content")
        
        # Upload to iRODS with metadata
        metadata = {
            "test_key": "test_value",
            "file_type": "text",
            "size": "12"
        }
        irods_client.create_collection(test_coll_name)
        obj = irods_client.upload_file(test_file_path, test_obj_path, metadata=metadata)
        
        # Test the API endpoint
        response = api_client.get(f"/metadata/object?path={test_obj_path}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["path"] == test_obj_path
        assert data["metadata"]["test_key"] == "test_value"
        assert data["metadata"]["file_type"] == "text"
        assert data["metadata"]["size"] == "12"
        
        # Test with a non-existent path
        response = api_client.get("/metadata/object?path=/non/existent/path")
        assert response.status_code == 404
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.api
def test_update_metadata(api_client: TestClient, irods_client: iRODSClient, temp_dir: str) -> None:
    """Test updating metadata for an object."""
    # Create a test data object with metadata
    test_coll_name = f"/tempZone/home/rods/test_api_update_{os.getpid()}"
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    test_obj_path = f"{test_coll_name}/test_file.txt"
    
    try:
        # Create a test file
        with open(test_file_path, "w") as f:
            f.write("Test content")
        
        # Upload to iRODS with metadata
        metadata = {
            "test_key": "test_value",
            "file_type": "text"
        }
        irods_client.create_collection(test_coll_name)
        obj = irods_client.upload_file(test_file_path, test_obj_path, metadata=metadata)
        
        # Test updating metadata
        update_data = {
            "path": test_obj_path,
            "metadata": {
                "test_key": "updated_value",
                "new_key": "new_value"
            }
        }
        
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify the metadata was updated
        obj = irods_client.get_data_object(test_obj_path)
        meta_dict = {m.name: m.value for m in obj.metadata.items()}
        assert meta_dict["test_key"] == "updated_value"
        assert meta_dict["new_key"] == "new_value"
        assert meta_dict["file_type"] == "text"  # Original metadata should still be there
        
        # Test with a non-existent path
        update_data["path"] = "/non/existent/path"
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 404
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)
