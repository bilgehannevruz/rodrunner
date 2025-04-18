"""
Tests for the iRODS client module.
"""
import os
import pytest
import tempfile
from typing import Dict, Any

from rodrunner.irods.client import iRODSClient


@pytest.mark.irods
def test_irods_connection(irods_client: iRODSClient) -> None:
    """Test connection to iRODS server."""
    with irods_client.session() as session:
        # Just check that we can get a session
        assert session is not None


@pytest.mark.irods
def test_collection_operations(irods_client: iRODSClient) -> None:
    """Test collection operations."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_collection_{os.getpid()}"
    
    try:
        # Test collection creation
        assert not irods_client.collection_exists(test_coll_name)
        coll = irods_client.create_collection(test_coll_name)
        assert irods_client.collection_exists(test_coll_name)
        
        # Test nested collection creation
        nested_coll_name = f"{test_coll_name}/nested"
        nested_coll = irods_client.create_collection(nested_coll_name)
        assert irods_client.collection_exists(nested_coll_name)
        
        # Test getting a collection
        retrieved_coll = irods_client.get_collection(test_coll_name)
        assert retrieved_coll.name == test_coll_name.split('/')[-1]
    
    finally:
        # Clean up
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)
        
        # Verify cleanup
        assert not irods_client.collection_exists(test_coll_name)


@pytest.mark.irods
def test_data_object_operations(irods_client: iRODSClient) -> None:
    """Test data object operations."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_data_objects_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        # Test uploading a file
        irods_path = f"{test_coll_name}/test_file.txt"
        obj = irods_client.upload_file(temp_file_path, irods_path)
        assert irods_client.data_object_exists(irods_path)
        
        # Test getting a data object
        retrieved_obj = irods_client.get_data_object(irods_path)
        assert retrieved_obj.name == "test_file.txt"
        
        # Test downloading a file
        download_path = f"{temp_file_path}_downloaded"
        irods_client.download_file(irods_path, download_path)
        with open(download_path, 'rb') as f:
            content = f.read()
            assert content == b"Test content"
        
        # Test removing a data object
        irods_client.remove_data_object(irods_path)
        assert not irods_client.data_object_exists(irods_path)
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if os.path.exists(download_path):
            os.unlink(download_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.irods
def test_metadata_operations(irods_client: iRODSClient) -> None:
    """Test metadata operations."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_metadata_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        # Test uploading a file with metadata
        irods_path = f"{test_coll_name}/test_file.txt"
        metadata = {
            "key1": "value1",
            "key2": "value2"
        }
        obj = irods_client.upload_file(temp_file_path, irods_path, metadata=metadata)
        
        # Verify metadata was added
        retrieved_obj = irods_client.get_data_object(irods_path)
        meta_dict = {m.name: m.value for m in retrieved_obj.metadata.items()}
        assert meta_dict["key1"] == "value1"
        assert meta_dict["key2"] == "value2"
        
        # Test uploading a directory with metadata
        os.makedirs(f"{temp_file_path}_dir/subdir", exist_ok=True)
        with open(f"{temp_file_path}_dir/file1.txt", 'w') as f:
            f.write("File 1 content")
        with open(f"{temp_file_path}_dir/subdir/file2.txt", 'w') as f:
            f.write("File 2 content")
        
        dir_irods_path = f"{test_coll_name}/test_dir"
        coll_metadata = {"collection_key": "collection_value"}
        file_metadata = {"file_key": "file_value"}
        
        coll = irods_client.upload_directory(
            f"{temp_file_path}_dir",
            dir_irods_path,
            metadata=coll_metadata,
            file_metadata=file_metadata
        )
        
        # Verify collection metadata
        retrieved_coll = irods_client.get_collection(dir_irods_path)
        coll_meta_dict = {m.name: m.value for m in retrieved_coll.metadata.items()}
        assert coll_meta_dict["collection_key"] == "collection_value"
        
        # Verify file metadata
        file_obj = irods_client.get_data_object(f"{dir_irods_path}/file1.txt")
        file_meta_dict = {m.name: m.value for m in file_obj.metadata.items()}
        assert file_meta_dict["file_key"] == "file_value"
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if os.path.exists(f"{temp_file_path}_dir"):
            import shutil
            shutil.rmtree(f"{temp_file_path}_dir")
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)
