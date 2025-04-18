#!/usr/bin/env python3
"""
Test script for iRODS client wrapper.
"""
import os
import sys
import json
import time
from pprint import pprint

from irods_prefect.models.config import iRODSConfig
from irods_prefect.irods.client import iRODSClient
from irods_prefect.parsers.factory import ParserFactory


def test_irods_client(config_file=None):
    """
    Test the iRODS client wrapper.
    
    Args:
        config_file: Path to the configuration file
    """
    # Load configuration
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        irods_config = iRODSConfig(**config_data.get('irods', {}))
    else:
        # Use environment variables or defaults
        irods_config = iRODSConfig(
            host=os.environ.get("IRODS_HOST", "localhost"),
            port=int(os.environ.get("IRODS_PORT", "1247")),
            user=os.environ.get("IRODS_USER", "rods"),
            password=os.environ.get("IRODS_PASSWORD", "rods"),
            zone=os.environ.get("IRODS_ZONE", "tempZone"),
            default_resource=os.environ.get("IRODS_DEFAULT_RESOURCE", "demoResc")
        )
    
    print("iRODS Configuration:")
    print(f"  Host: {irods_config.host}")
    print(f"  Port: {irods_config.port}")
    print(f"  User: {irods_config.user}")
    print(f"  Zone: {irods_config.zone}")
    print(f"  Default Resource: {irods_config.default_resource}")
    print()
    
    # Create iRODS client
    client = iRODSClient(irods_config)
    
    try:
        # Test connection
        print("Testing connection...")
        with client.session() as session:
            print("Connection successful!")
            print()
        
        # Test collection operations
        test_collection = f"/{irods_config.zone}/home/{irods_config.user}/test_collection_{int(time.time())}"
        
        print(f"Creating collection: {test_collection}")
        client.create_collection(test_collection)
        print("Collection created successfully")
        print()
        
        # Test data object operations
        test_file = "test_file.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for iRODS client wrapper testing.")
        
        test_data_object = f"{test_collection}/{test_file}"
        print(f"Uploading file: {test_file} to {test_data_object}")
        client.upload_file(test_file, test_data_object, metadata={"test_key": "test_value"})
        print("File uploaded successfully")
        print()
        
        # Test metadata operations
        print(f"Adding metadata to {test_collection}")
        with client.session() as session:
            coll = session.collections.get(test_collection)
            coll.metadata.add("test_key", "test_value")
            coll.metadata.add("test_key2", "test_value2")
        print("Metadata added successfully")
        print()
        
        print(f"Getting metadata from {test_collection}")
        with client.session() as session:
            coll = session.collections.get(test_collection)
            metadata = {meta.name: meta.value for meta in coll.metadata.items()}
            print("Metadata:")
            pprint(metadata)
        print()
        
        # Test cleanup
        print(f"Removing data object: {test_data_object}")
        client.remove_data_object(test_data_object)
        print("Data object removed successfully")
        print()
        
        print(f"Removing collection: {test_collection}")
        client.remove_collection(test_collection)
        print("Collection removed successfully")
        print()
        
        # Clean up local test file
        os.remove(test_file)
        
        print("iRODS client wrapper test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Get configuration file from command line argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    # Test iRODS client wrapper
    success = test_irods_client(config_file)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
