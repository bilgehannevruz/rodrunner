"""
Edge case tests for the API endpoints.
"""
import os
import pytest
import tempfile
import json
import time
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from rodrunner.models.config import AppConfig
from rodrunner.irods.client import iRODSClient


@pytest.mark.api
def test_api_root_with_invalid_method(api_client: TestClient) -> None:
    """Test the API root endpoint with invalid HTTP method."""
    response = api_client.post("/")
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.api
def test_metadata_search_with_missing_parameters(api_client: TestClient) -> None:
    """Test metadata search with missing parameters."""
    # Test with missing key
    response = api_client.get("/metadata/search?value=test")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with missing value
    response = api_client.get("/metadata/search?key=test")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with empty parameters
    response = api_client.get("/metadata/search?key=&value=")
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.api
def test_metadata_search_with_special_characters(api_client: TestClient, irods_client: iRODSClient) -> None:
    """Test metadata search with special characters."""
    # Create a test collection with metadata containing special characters
    test_coll_name = f"/tempZone/home/rods/test_special_chars_{os.getpid()}"
    
    special_chars = [
        "value with spaces",
        "value_with_unicode_Ü_ñ_é",
        "value-with-dashes",
        "value.with.dots",
        "value+with+plus",
        "value'with'quotes",
        "value\"with\"doublequotes",
        "value(with)parentheses",
        "value[with]brackets",
        "value{with}braces",
        "value#with#hash",
        "value@with@at",
        "value$with$dollar",
        "value%with%percent",
        "value^with^caret",
        "value&with&ampersand",
        "value=with=equals",
        "value;with;semicolon",
        "value,with,comma"
    ]
    
    try:
        # Create collection with metadata
        coll = irods_client.create_collection(test_coll_name)
        
        # Add metadata with special characters
        with irods_client.session() as session:
            coll = session.collections.get(test_coll_name)
            for i, value in enumerate(special_chars):
                coll.metadata.add(f"special_key_{i}", value)
        
        # Test searching for each special character value
        for i, value in enumerate(special_chars):
            response = api_client.get(f"/metadata/search?key=special_key_{i}&value={value}")
            assert response.status_code == 200
            data = response.json()
            
            # Find our test collection in the results
            found = False
            for item in data:
                if item["path"] == test_coll_name:
                    found = True
                    assert item["metadata"][f"special_key_{i}"] == value
                    break
            
            assert found, f"Test collection not found in results for value: {value}"
    
    finally:
        # Clean up
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name)


@pytest.mark.api
def test_metadata_object_with_nonexistent_path(api_client: TestClient) -> None:
    """Test getting metadata for a nonexistent object."""
    response = api_client.get("/metadata/object?path=/tempZone/home/rods/nonexistent/path")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.api
def test_metadata_object_with_invalid_path(api_client: TestClient) -> None:
    """Test getting metadata with an invalid path."""
    # Test with an empty path
    response = api_client.get("/metadata/object?path=")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with a malformed path
    response = api_client.get("/metadata/object?path=invalid_path")
    assert response.status_code == 422  # Unprocessable Entity or 404 Not Found


@pytest.mark.api
def test_metadata_update_with_invalid_data(api_client: TestClient, irods_client: iRODSClient, temp_dir: str) -> None:
    """Test updating metadata with invalid data."""
    # Create a test data object
    test_coll_name = f"/tempZone/home/rods/test_update_invalid_{os.getpid()}"
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    test_obj_path = f"{test_coll_name}/test_file.txt"
    
    try:
        # Create a test file
        with open(test_file_path, "w") as f:
            f.write("Test content")
        
        # Upload to iRODS
        irods_client.create_collection(test_coll_name)
        obj = irods_client.upload_file(test_file_path, test_obj_path)
        
        # Test updating with empty metadata
        update_data = {
            "path": test_obj_path,
            "metadata": {}
        }
        
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 400  # Bad Request
        
        # Test updating with invalid metadata values
        update_data = {
            "path": test_obj_path,
            "metadata": {
                "key1": None,
                "key2": 123,  # Non-string value
                "key3": ""
            }
        }
        
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test updating with missing path
        update_data = {
            "metadata": {
                "key1": "value1"
            }
        }
        
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test updating with missing metadata
        update_data = {
            "path": test_obj_path
        }
        
        response = api_client.post("/metadata/update", json=update_data)
        assert response.status_code == 422  # Unprocessable Entity
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.api
def test_workflow_list_with_invalid_method(api_client: TestClient) -> None:
    """Test workflow list with invalid HTTP method."""
    response = api_client.post("/workflows/list")
    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.api
def test_workflow_run_with_invalid_data(api_client: TestClient) -> None:
    """Test running a workflow with invalid data."""
    # Test with missing workflow name
    workflow_data = {
        "parameters": {
            "sequencer_type": "miseq",
            "root_dir": "/path/to/sequencer/miseq"
        }
    }
    
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with missing parameters
    workflow_data = {
        "workflow_name": "Ingest Sequencer Runs"
    }
    
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with invalid workflow name
    workflow_data = {
        "workflow_name": "Non-existent Workflow",
        "parameters": {}
    }
    
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code == 404  # Not Found
    
    # Test with invalid parameters
    workflow_data = {
        "workflow_name": "Ingest Sequencer Runs",
        "parameters": {
            "invalid_param": "value"
        }
    }
    
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code in [400, 422]  # Bad Request or Unprocessable Entity


@pytest.mark.api
def test_workflow_status_with_invalid_id(api_client: TestClient) -> None:
    """Test getting workflow status with invalid ID."""
    # Test with a non-existent flow run ID
    response = api_client.get("/workflows/status/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404  # Not Found
    
    # Test with an invalid flow run ID format
    response = api_client.get("/workflows/status/invalid-id")
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.api
def test_concurrent_api_requests(api_client: TestClient, irods_client: iRODSClient) -> None:
    """Test concurrent API requests."""
    # Create test collections with metadata
    num_collections = 5
    test_coll_names = []
    
    try:
        # Create collections with metadata
        for i in range(num_collections):
            test_coll_name = f"/tempZone/home/rods/test_concurrent_{os.getpid()}_{i}"
            test_coll_names.append(test_coll_name)
            
            coll = irods_client.create_collection(test_coll_name)
            with irods_client.session() as session:
                coll = session.collections.get(test_coll_name)
                coll.metadata.add("concurrent_key", f"value_{i}")
        
        # Function to make a request
        def make_request(i):
            return api_client.get(f"/metadata/search?key=concurrent_key&value=value_{i}")
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=num_collections) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_collections)]
            responses = [future.result() for future in futures]
        
        # Verify all responses
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            
            # Find our test collection in the results
            found = False
            for item in data:
                if item["path"] == test_coll_names[i]:
                    found = True
                    assert item["metadata"]["concurrent_key"] == f"value_{i}"
                    break
            
            assert found, f"Test collection not found in results for value_{i}"
    
    finally:
        # Clean up
        for test_coll_name in test_coll_names:
            if irods_client.collection_exists(test_coll_name):
                irods_client.remove_collection(test_coll_name)


@pytest.mark.api
def test_large_metadata_response(api_client: TestClient, irods_client: iRODSClient) -> None:
    """Test API response with large metadata."""
    # Create a test collection with a large number of metadata attributes
    test_coll_name = f"/tempZone/home/rods/test_large_metadata_{os.getpid()}"
    
    try:
        # Create collection
        coll = irods_client.create_collection(test_coll_name)
        
        # Add a large number of metadata attributes
        with irods_client.session() as session:
            coll = session.collections.get(test_coll_name)
            
            # Add 100 metadata attributes
            for i in range(100):
                coll.metadata.add(f"large_key_{i}", f"large_value_{i}")
            
            # Add a special key for searching
            coll.metadata.add("search_key", "search_value")
        
        # Test searching for the collection
        response = api_client.get("/metadata/search?key=search_key&value=search_value")
        assert response.status_code == 200
        data = response.json()
        
        # Find our test collection in the results
        found = False
        for item in data:
            if item["path"] == test_coll_name:
                found = True
                
                # Verify that all metadata attributes are present
                for i in range(100):
                    assert item["metadata"][f"large_key_{i}"] == f"large_value_{i}"
                
                break
        
        assert found, "Test collection not found in results"
        
        # Test getting metadata for the specific object
        response = api_client.get(f"/metadata/object?path={test_coll_name}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify that all metadata attributes are present
        for i in range(100):
            assert data["metadata"][f"large_key_{i}"] == f"large_value_{i}"
    
    finally:
        # Clean up
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name)


@pytest.mark.api
def test_api_error_handling(api_client: TestClient) -> None:
    """Test API error handling."""
    # Test with an invalid URL
    response = api_client.get("/invalid/url")
    assert response.status_code == 404  # Not Found
    
    # Test with an invalid HTTP method
    response = api_client.put("/")
    assert response.status_code == 405  # Method Not Allowed
    
    # Test with invalid query parameters
    response = api_client.get("/metadata/search?invalid=param")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with invalid JSON body
    response = api_client.post(
        "/metadata/update",
        headers={"Content-Type": "application/json"},
        content="invalid json"
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.api
def test_api_rate_limiting(api_client: TestClient) -> None:
    """Test API rate limiting by making many requests in a short time."""
    # Make many requests in a short time
    num_requests = 50
    start_time = time.time()
    
    responses = []
    for _ in range(num_requests):
        response = api_client.get("/health")
        responses.append(response)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Check if all requests were successful
    all_successful = all(response.status_code == 200 for response in responses)
    
    # If rate limiting is implemented, some requests might fail or be delayed
    # If all requests were successful, check if they took a reasonable amount of time
    if all_successful:
        # Calculate requests per second
        requests_per_second = num_requests / duration
        print(f"Requests per second: {requests_per_second:.2f}")
        
        # This is just informational, not a strict test
        # If rate limiting is implemented, requests_per_second should be limited
    
    # This test is more about checking if the API can handle a burst of requests
    # rather than strictly testing rate limiting
    assert all_successful, "Some requests failed, which might indicate rate limiting or server issues"
