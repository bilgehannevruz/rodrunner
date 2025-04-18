"""
Tests for the metadata workflows.
"""
import os
import pytest
from typing import Dict, Any, List

from prefect import flow, task

from rodrunner.models.config import AppConfig
from rodrunner.workflows.metadata import update_run_metadata
from rodrunner.irods.client import iRODSClient


@pytest.mark.integration
def test_update_run_metadata(app_config: AppConfig, irods_client: iRODSClient, 
                           sample_sequencer_run: str, temp_dir: str) -> None:
    """Test updating run metadata."""
    # First, ingest a run into iRODS
    # This would typically be done by the ingest workflow, but we'll do it manually for testing
    run_name = os.path.basename(sample_sequencer_run)
    irods_run_path = f"/tempZone/home/rods/test_metadata_{os.getpid()}/{run_name}"
    
    try:
        # Create the collection
        irods_client.create_collection(irods_run_path)
        
        # Upload the run files
        irods_client.upload_directory(
            sample_sequencer_run,
            irods_run_path,
            metadata={"run_type": "miseq", "status": "raw"}
        )
        
        # Verify the files were uploaded
        assert irods_client.collection_exists(irods_run_path)
        assert irods_client.data_object_exists(f"{irods_run_path}/RunInfo.xml")
        assert irods_client.data_object_exists(f"{irods_run_path}/RunParameters.xml")
        assert irods_client.data_object_exists(f"{irods_run_path}/RTAComplete.txt")
        
        # Run the metadata update workflow
        result = update_run_metadata(
            config=app_config,
            irods_path=irods_run_path,
            sequencer_type="miseq"
        )
        
        # Verify the result
        assert result["success"] is True
        assert result["irods_path"] == irods_run_path
        
        # Verify the metadata was updated
        coll = irods_client.get_collection(irods_run_path)
        meta_dict = {m.name: m.value for m in coll.metadata.items()}
        
        # Check for metadata extracted from RunInfo.xml
        assert "run_id" in meta_dict
        assert meta_dict["run_id"] == "220101_M00001_0001_000000000-A1B2C"
        assert "instrument" in meta_dict
        assert meta_dict["instrument"] == "M00001"
        
        # Check for metadata extracted from RunParameters.xml
        assert "rta_version" in meta_dict
        assert "chemistry" in meta_dict
        
        # Check for metadata extracted from SampleSheet.csv
        assert "sample_count" in meta_dict
        assert meta_dict["sample_count"] == "2"  # Two samples in the sample sheet
        
        # Check that status was updated
        assert meta_dict["status"] == "metadata_extracted"
    
    finally:
        # Clean up
        if irods_client.collection_exists(os.path.dirname(irods_run_path)):
            irods_client.remove_collection(os.path.dirname(irods_run_path), recursive=True)
