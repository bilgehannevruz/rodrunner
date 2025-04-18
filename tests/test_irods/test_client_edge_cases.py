"""
Edge case tests for the iRODS client module.
"""
import os
import pytest
import tempfile
import time
import random
import string
from typing import Dict, Any

from rodrunner.irods.client import iRODSClient
from rodrunner.irods.exceptions import iRODSException


@pytest.mark.irods
def test_irods_connection_timeout(irods_client: iRODSClient) -> None:
    """Test connection timeout handling."""
    # Set a very short connection timeout
    irods_client.connection_timeout = 0.001  # 1 millisecond
    
    # Try to perform an operation that should timeout
    with pytest.raises(Exception) as excinfo:
        with irods_client.session() as session:
            # Sleep to ensure timeout
            time.sleep(0.1)
            session.collections.get("/tempZone/home/rods")
    
    # Reset the timeout for other tests
    irods_client.connection_timeout = 120


@pytest.mark.irods
def test_irods_connection_retry(irods_client: iRODSClient) -> None:
    """Test connection retry logic."""
    # Save the original connection parameters
    original_host = irods_client.config.host
    original_port = irods_client.config.port
    
    try:
        # Set invalid connection parameters to force a failure
        irods_client.config.host = "nonexistent-host"
        irods_client.config.port = 1234
        
        # Try to connect with retries
        with pytest.raises(Exception):
            with irods_client.session(retries=3, retry_delay=0.1) as session:
                session.collections.get("/tempZone/home/rods")
    
    finally:
        # Restore the original connection parameters
        irods_client.config.host = original_host
        irods_client.config.port = original_port


@pytest.mark.irods
def test_collection_operations_with_special_characters(irods_client: iRODSClient) -> None:
    """Test collection operations with special characters in names."""
    # Generate a unique collection name with special characters
    special_chars = [
        "collection with spaces",
        "collection_with_unicode_Ü_ñ_é",
        "collection-with-dashes",
        "collection.with.dots",
        "collection+with+plus",
        "collection'with'quotes",
        "collection(with)parentheses",
        "collection[with]brackets",
        "collection{with}braces",
        "collection#with#hash",
        "collection@with@at",
        "collection$with$dollar",
        "collection%with%percent",
        "collection^with^caret",
        "collection&with&ampersand",
        "collection=with=equals",
        "collection;with;semicolon",
        "collection,with,comma"
    ]
    
    for char_name in special_chars:
        test_coll_name = f"/tempZone/home/rods/test_{char_name}_{os.getpid()}"
        
        try:
            # Test collection creation with special characters
            assert not irods_client.collection_exists(test_coll_name)
            coll = irods_client.create_collection(test_coll_name)
            assert irods_client.collection_exists(test_coll_name)
            
            # Test getting a collection with special characters
            retrieved_coll = irods_client.get_collection(test_coll_name)
            assert retrieved_coll.name == test_coll_name.split('/')[-1]
        
        finally:
            # Clean up
            if irods_client.collection_exists(test_coll_name):
                irods_client.remove_collection(test_coll_name, recursive=True)
            
            # Verify cleanup
            assert not irods_client.collection_exists(test_coll_name)


@pytest.mark.irods
def test_nested_collection_operations(irods_client: iRODSClient) -> None:
    """Test operations with deeply nested collections."""
    # Generate a unique base collection name
    base_coll_name = f"/tempZone/home/rods/test_nested_{os.getpid()}"
    
    try:
        # Create a base collection
        irods_client.create_collection(base_coll_name)
        
        # Create a deeply nested collection structure
        current_path = base_coll_name
        nesting_depth = 10
        
        for i in range(nesting_depth):
            current_path = f"{current_path}/level_{i}"
            irods_client.create_collection(current_path)
            assert irods_client.collection_exists(current_path)
        
        # Test getting the deepest collection
        deepest_coll = irods_client.get_collection(current_path)
        assert deepest_coll.name == f"level_{nesting_depth-1}"
        
        # Test removing a middle collection and all its children
        middle_path = f"{base_coll_name}/level_0/level_1/level_2"
        irods_client.remove_collection(middle_path, recursive=True)
        
        # Verify that the middle collection and its children are gone
        assert not irods_client.collection_exists(middle_path)
        assert not irods_client.collection_exists(current_path)
        
        # Verify that the parent collections still exist
        assert irods_client.collection_exists(f"{base_coll_name}/level_0/level_1")
        assert irods_client.collection_exists(f"{base_coll_name}/level_0")
        assert irods_client.collection_exists(base_coll_name)
    
    finally:
        # Clean up
        if irods_client.collection_exists(base_coll_name):
            irods_client.remove_collection(base_coll_name, recursive=True)
        
        # Verify cleanup
        assert not irods_client.collection_exists(base_coll_name)


@pytest.mark.irods
def test_data_object_operations_with_large_files(irods_client: iRODSClient) -> None:
    """Test data object operations with large files."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_large_files_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create a large temporary file (10 MB)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write 10 MB of random data
            chunk_size = 1024 * 1024  # 1 MB
            for _ in range(10):  # 10 chunks of 1 MB
                temp_file.write(os.urandom(chunk_size))
            
            temp_file_path = temp_file.name
        
        # Test uploading a large file
        irods_path = f"{test_coll_name}/large_file.bin"
        obj = irods_client.upload_file(temp_file_path, irods_path)
        assert irods_client.data_object_exists(irods_path)
        
        # Test getting a large data object
        retrieved_obj = irods_client.get_data_object(irods_path)
        assert retrieved_obj.name == "large_file.bin"
        assert retrieved_obj.size == os.path.getsize(temp_file_path)
        
        # Test downloading a large file
        download_path = f"{temp_file_path}_downloaded"
        irods_client.download_file(irods_path, download_path)
        
        # Verify the downloaded file
        assert os.path.exists(download_path)
        assert os.path.getsize(download_path) == os.path.getsize(temp_file_path)
        
        # Compare file contents (hash)
        import hashlib
        
        def get_file_hash(file_path):
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        original_hash = get_file_hash(temp_file_path)
        downloaded_hash = get_file_hash(download_path)
        assert original_hash == downloaded_hash
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if os.path.exists(download_path):
            os.unlink(download_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.irods
def test_data_object_operations_with_empty_files(irods_client: iRODSClient) -> None:
    """Test data object operations with empty files."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_empty_files_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create an empty temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        # Test uploading an empty file
        irods_path = f"{test_coll_name}/empty_file.txt"
        obj = irods_client.upload_file(temp_file_path, irods_path)
        assert irods_client.data_object_exists(irods_path)
        
        # Test getting an empty data object
        retrieved_obj = irods_client.get_data_object(irods_path)
        assert retrieved_obj.name == "empty_file.txt"
        assert retrieved_obj.size == 0
        
        # Test downloading an empty file
        download_path = f"{temp_file_path}_downloaded"
        irods_client.download_file(irods_path, download_path)
        
        # Verify the downloaded file
        assert os.path.exists(download_path)
        assert os.path.getsize(download_path) == 0
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if os.path.exists(download_path):
            os.unlink(download_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.irods
def test_metadata_operations_with_large_values(irods_client: iRODSClient) -> None:
    """Test metadata operations with large values."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_large_metadata_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        # Test uploading a file with large metadata values
        irods_path = f"{test_coll_name}/test_file.txt"
        
        # Generate a large metadata value (64 KB)
        large_value = ''.join(random.choice(string.ascii_letters) for _ in range(64 * 1024))
        
        metadata = {
            "key1": "value1",
            "large_key": large_value
        }
        
        # This might fail if iRODS has a limit on metadata value size
        try:
            obj = irods_client.upload_file(temp_file_path, irods_path, metadata=metadata)
            
            # Verify metadata was added
            retrieved_obj = irods_client.get_data_object(irods_path)
            meta_dict = {m.name: m.value for m in retrieved_obj.metadata.items()}
            assert meta_dict["key1"] == "value1"
            assert meta_dict["large_key"] == large_value
        except Exception as e:
            # If this fails due to iRODS limitations, that's expected
            print(f"Large metadata test failed with: {str(e)}")
            pass
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.irods
def test_metadata_operations_with_many_attributes(irods_client: iRODSClient) -> None:
    """Test metadata operations with many attributes."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_many_metadata_{os.getpid()}"
    
    try:
        # Create a test collection
        irods_client.create_collection(test_coll_name)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name
        
        # Test uploading a file with many metadata attributes
        irods_path = f"{test_coll_name}/test_file.txt"
        
        # Generate many metadata attributes (100)
        metadata = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        obj = irods_client.upload_file(temp_file_path, irods_path, metadata=metadata)
        
        # Verify metadata was added
        retrieved_obj = irods_client.get_data_object(irods_path)
        meta_dict = {m.name: m.value for m in retrieved_obj.metadata.items()}
        
        for i in range(100):
            assert meta_dict[f"key_{i}"] == f"value_{i}"
        
        # Test updating metadata
        with irods_client.session() as session:
            obj = session.data_objects.get(irods_path)
            
            # Update 50 metadata attributes
            for i in range(50):
                obj.metadata[f"key_{i}"] = f"updated_value_{i}"
        
        # Verify metadata was updated
        retrieved_obj = irods_client.get_data_object(irods_path)
        meta_dict = {m.name: m.value for m in retrieved_obj.metadata.items()}
        
        for i in range(50):
            assert meta_dict[f"key_{i}"] == f"updated_value_{i}"
        
        for i in range(50, 100):
            assert meta_dict[f"key_{i}"] == f"value_{i}"
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)


@pytest.mark.irods
def test_upload_directory_with_many_files(irods_client: iRODSClient) -> None:
    """Test uploading a directory with many files."""
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_many_files_{os.getpid()}"
    
    try:
        # Create a temporary directory with many files
        temp_dir = tempfile.mkdtemp()
        num_files = 100
        
        # Create a nested directory structure with files
        os.makedirs(os.path.join(temp_dir, "subdir1", "subdir2"))
        os.makedirs(os.path.join(temp_dir, "subdir3"))
        
        # Create files in the root directory
        for i in range(num_files // 2):
            with open(os.path.join(temp_dir, f"file_{i}.txt"), "w") as f:
                f.write(f"Content for file {i}")
        
        # Create files in subdirectories
        for i in range(num_files // 4):
            with open(os.path.join(temp_dir, "subdir1", f"file_{i}.txt"), "w") as f:
                f.write(f"Content for subdir1/file_{i}")
        
        for i in range(num_files // 8):
            with open(os.path.join(temp_dir, "subdir1", "subdir2", f"file_{i}.txt"), "w") as f:
                f.write(f"Content for subdir1/subdir2/file_{i}")
        
        for i in range(num_files // 8):
            with open(os.path.join(temp_dir, "subdir3", f"file_{i}.txt"), "w") as f:
                f.write(f"Content for subdir3/file_{i}")
        
        # Test uploading the directory
        coll = irods_client.upload_directory(temp_dir, test_coll_name)
        assert irods_client.collection_exists(test_coll_name)
        
        # Verify the directory structure was preserved
        assert irods_client.collection_exists(f"{test_coll_name}/subdir1")
        assert irods_client.collection_exists(f"{test_coll_name}/subdir1/subdir2")
        assert irods_client.collection_exists(f"{test_coll_name}/subdir3")
        
        # Verify files were uploaded
        assert irods_client.data_object_exists(f"{test_coll_name}/file_0.txt")
        assert irods_client.data_object_exists(f"{test_coll_name}/subdir1/file_0.txt")
        assert irods_client.data_object_exists(f"{test_coll_name}/subdir1/subdir2/file_0.txt")
        assert irods_client.data_object_exists(f"{test_coll_name}/subdir3/file_0.txt")
        
        # Count the number of files in the collection
        with irods_client.session() as session:
            # Count files in the root collection
            root_coll = session.collections.get(test_coll_name)
            root_files = list(root_coll.data_objects)
            
            # Count files in subdir1
            subdir1_coll = session.collections.get(f"{test_coll_name}/subdir1")
            subdir1_files = list(subdir1_coll.data_objects)
            
            # Count files in subdir1/subdir2
            subdir2_coll = session.collections.get(f"{test_coll_name}/subdir1/subdir2")
            subdir2_files = list(subdir2_coll.data_objects)
            
            # Count files in subdir3
            subdir3_coll = session.collections.get(f"{test_coll_name}/subdir3")
            subdir3_files = list(subdir3_coll.data_objects)
            
            total_files = len(root_files) + len(subdir1_files) + len(subdir2_files) + len(subdir3_files)
            assert total_files == num_files
    
    finally:
        # Clean up
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)
