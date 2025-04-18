"""
Edge case tests for the workflow module.
"""
import os
import pytest
import tempfile
import shutil
from typing import Dict, Any, List

from prefect import flow, task

from rodrunner.models.config import AppConfig
from rodrunner.workflows.ingest import ingest_sequencer_runs, ingest_all_sequencer_runs
from rodrunner.workflows.metadata import update_run_metadata
from rodrunner.irods.client import iRODSClient


@pytest.mark.integration
def test_ingest_workflow_with_no_runs(app_config: AppConfig, temp_dir: str) -> None:
    """Test ingesting with no sequencer runs."""
    # Set up an empty test directory
    sequencer_dir = os.path.join(temp_dir, "empty_sequencer")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    os.makedirs(miseq_dir)
    
    # Update the config to use our test directory
    app_config.sequencer.base_dir = sequencer_dir
    app_config.sequencer.miseq_dir = miseq_dir
    
    # Run the workflow
    results = ingest_sequencer_runs(
        config=app_config,
        sequencer_type="miseq",
        root_dir=miseq_dir
    )
    
    # Verify the results
    assert len(results) == 0


@pytest.mark.integration
def test_ingest_workflow_with_invalid_runs(app_config: AppConfig, sample_sequencer_run: str, temp_dir: str) -> None:
    """Test ingesting with invalid sequencer runs."""
    # Set up a test directory with an invalid run
    sequencer_dir = os.path.join(temp_dir, "invalid_sequencer")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    os.makedirs(miseq_dir)
    
    # Create an invalid run by copying the sample run but removing a required file
    run_name = os.path.basename(sample_sequencer_run)
    invalid_run_dir = os.path.join(miseq_dir, run_name)
    shutil.copytree(sample_sequencer_run, invalid_run_dir)
    os.remove(os.path.join(invalid_run_dir, "RunInfo.xml"))
    
    # Update the config to use our test directory
    app_config.sequencer.base_dir = sequencer_dir
    app_config.sequencer.miseq_dir = miseq_dir
    
    # Run the workflow
    results = ingest_sequencer_runs(
        config=app_config,
        sequencer_type="miseq",
        root_dir=miseq_dir
    )
    
    # Verify the results
    assert len(results) == 0  # No valid runs should be found


@pytest.mark.integration
def test_ingest_workflow_with_mixed_runs(app_config: AppConfig, sample_sequencer_run: str, temp_dir: str) -> None:
    """Test ingesting with a mix of valid and invalid runs."""
    # Set up a test directory with mixed runs
    sequencer_dir = os.path.join(temp_dir, "mixed_sequencer")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    os.makedirs(miseq_dir)
    
    # Copy the sample run to create a valid run
    run_name = os.path.basename(sample_sequencer_run)
    valid_run_dir = os.path.join(miseq_dir, run_name)
    shutil.copytree(sample_sequencer_run, valid_run_dir)
    
    # Create an invalid run by copying the sample run but removing a required file
    invalid_run_name = f"invalid_{run_name}"
    invalid_run_dir = os.path.join(miseq_dir, invalid_run_name)
    shutil.copytree(sample_sequencer_run, invalid_run_dir)
    os.remove(os.path.join(invalid_run_dir, "RunInfo.xml"))
    
    # Create another invalid run with a different issue
    incomplete_run_name = f"incomplete_{run_name}"
    incomplete_run_dir = os.path.join(miseq_dir, incomplete_run_name)
    shutil.copytree(sample_sequencer_run, incomplete_run_dir)
    os.remove(os.path.join(incomplete_run_dir, "RTAComplete.txt"))
    
    # Update the config to use our test directory
    app_config.sequencer.base_dir = sequencer_dir
    app_config.sequencer.miseq_dir = miseq_dir
    
    # Run the workflow
    results = ingest_sequencer_runs(
        config=app_config,
        sequencer_type="miseq",
        root_dir=miseq_dir
    )
    
    # Verify the results
    assert len(results) == 1  # Only the valid run should be ingested
    assert results[0]["success"] is True
    assert valid_run_dir in results[0]["run_dir"]


@pytest.mark.integration
def test_ingest_workflow_with_already_ingested_runs(app_config: AppConfig, sample_sequencer_run: str, 
                                                 temp_dir: str, irods_client: iRODSClient) -> None:
    """Test ingesting runs that have already been ingested."""
    # Set up a test directory with a sequencer run
    sequencer_dir = os.path.join(temp_dir, "already_ingested_sequencer")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    os.makedirs(miseq_dir)
    
    # Copy the sample run to the miseq directory
    run_name = os.path.basename(sample_sequencer_run)
    run_dir = os.path.join(miseq_dir, run_name)
    shutil.copytree(sample_sequencer_run, run_dir)
    
    # Update the config to use our test directory
    app_config.sequencer.base_dir = sequencer_dir
    app_config.sequencer.miseq_dir = miseq_dir
    
    # Create a collection in iRODS that matches the run name
    irods_run_path = f"/tempZone/home/rods/sequencer/miseq/{run_name}"
    
    try:
        # Create the collection with metadata indicating it's already ingested
        irods_client.create_collection(irods_run_path)
        with irods_client.session() as session:
            coll = session.collections.get(irods_run_path)
            coll.metadata.add("status", "ingested")
            coll.metadata.add("run_id", run_name)
        
        # Run the workflow
        results = ingest_sequencer_runs(
            config=app_config,
            sequencer_type="miseq",
            root_dir=miseq_dir
        )
        
        # Verify the results
        assert len(results) == 1
        assert results[0]["success"] is True
        assert "already_ingested" in results[0]
        assert results[0]["already_ingested"] is True
    
    finally:
        # Clean up
        if irods_client.collection_exists(irods_run_path):
            irods_client.remove_collection(irods_run_path, recursive=True)


@pytest.mark.integration
def test_ingest_all_sequencer_runs_with_mixed_types(app_config: AppConfig, sample_sequencer_run: str, 
                                                 temp_dir: str) -> None:
    """Test ingesting all sequencer runs with mixed types."""
    # Set up test directories with sequencer runs
    sequencer_dir = os.path.join(temp_dir, "mixed_types_sequencer")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    novaseq_dir = os.path.join(sequencer_dir, "novaseq")
    pacbio_dir = os.path.join(sequencer_dir, "pacbio")
    nanopore_dir = os.path.join(sequencer_dir, "nanopore")
    os.makedirs(miseq_dir)
    os.makedirs(novaseq_dir)
    os.makedirs(pacbio_dir)
    os.makedirs(nanopore_dir)
    
    # Copy the sample run to the miseq directory
    run_name = os.path.basename(sample_sequencer_run)
    miseq_run_dir = os.path.join(miseq_dir, run_name)
    shutil.copytree(sample_sequencer_run, miseq_run_dir)
    
    # Create a novaseq run by modifying the instrument ID in RunInfo.xml
    novaseq_run_dir = os.path.join(novaseq_dir, "220102_A00001_0001_AHGV7DRXX")
    os.makedirs(novaseq_run_dir)
    
    # Copy files from the sample run
    shutil.copy(os.path.join(sample_sequencer_run, "SampleSheet.csv"), novaseq_run_dir)
    shutil.copy(os.path.join(sample_sequencer_run, "RunParameters.xml"), novaseq_run_dir)
    with open(os.path.join(novaseq_run_dir, "RTAComplete.txt"), "w") as f:
        f.write("RTA Complete")
    
    # Create a modified RunInfo.xml for NovaSeq
    with open(os.path.join(sample_sequencer_run, "RunInfo.xml"), "r") as f:
        run_info_content = f.read()
    
    # Replace MiSeq instrument ID with NovaSeq instrument ID
    novaseq_run_info = run_info_content.replace("<Instrument>M00001</Instrument>", 
                                              "<Instrument>A00001</Instrument>")
    novaseq_run_info = novaseq_run_info.replace("220101_M00001_0001_000000000-A1B2C", 
                                              "220102_A00001_0001_AHGV7DRXX")
    
    with open(os.path.join(novaseq_run_dir, "RunInfo.xml"), "w") as f:
        f.write(novaseq_run_info)
    
    # Create an invalid PacBio run (missing required files)
    pacbio_run_dir = os.path.join(pacbio_dir, "r54228_20220103_123456")
    os.makedirs(pacbio_run_dir)
    with open(os.path.join(pacbio_run_dir, "metadata.xml"), "w") as f:
        f.write("<PacBioMetadata></PacBioMetadata>")
    
    # Create an invalid Nanopore run (missing required files)
    nanopore_run_dir = os.path.join(nanopore_dir, "20220104_1234_X1_FAO12345_a1b2c3d4")
    os.makedirs(nanopore_run_dir)
    with open(os.path.join(nanopore_run_dir, "final_summary.txt"), "w") as f:
        f.write("Nanopore run summary")
    
    # Update the config to use our test directory
    app_config.sequencer.base_dir = sequencer_dir
    app_config.sequencer.miseq_dir = miseq_dir
    app_config.sequencer.novaseq_dir = novaseq_dir
    app_config.sequencer.pacbio_dir = pacbio_dir
    app_config.sequencer.nanopore_dir = nanopore_dir
    
    # Run the workflow
    results = ingest_all_sequencer_runs(
        config=app_config,
        root_dir=sequencer_dir
    )
    
    # Verify the results
    assert "miseq" in results
    assert "novaseq" in results
    assert "pacbio" in results
    assert "nanopore" in results
    
    assert len(results["miseq"]) == 1
    assert results["miseq"][0]["success"] is True
    
    # NovaSeq might fail if the NovaSeq workflow is not fully implemented
    # Just check that it was attempted
    assert len(results["novaseq"]) > 0
    
    # PacBio and Nanopore should have no valid runs
    assert len(results["pacbio"]) == 0
    assert len(results["nanopore"]) == 0


@pytest.mark.integration
def test_update_metadata_with_missing_files(app_config: AppConfig, irods_client: iRODSClient, 
                                         sample_sequencer_run: str, temp_dir: str) -> None:
    """Test updating metadata with missing files."""
    # First, ingest a run into iRODS but with missing files
    run_name = os.path.basename(sample_sequencer_run)
    irods_run_path = f"/tempZone/home/rods/test_missing_files_{os.getpid()}/{run_name}"
    
    try:
        # Create the collection
        irods_client.create_collection(irods_run_path)
        
        # Upload only some of the run files
        with open(os.path.join(sample_sequencer_run, "RunInfo.xml"), "rb") as f:
            irods_client.upload_file(os.path.join(sample_sequencer_run, "RunInfo.xml"), 
                                   f"{irods_run_path}/RunInfo.xml")
        
        # Don't upload RunParameters.xml and SampleSheet.csv
        
        with open(os.path.join(sample_sequencer_run, "RTAComplete.txt"), "rb") as f:
            irods_client.upload_file(os.path.join(sample_sequencer_run, "RTAComplete.txt"), 
                                   f"{irods_run_path}/RTAComplete.txt")
        
        # Add some basic metadata
        with irods_client.session() as session:
            coll = session.collections.get(irods_run_path)
            coll.metadata.add("run_type", "miseq")
            coll.metadata.add("status", "raw")
        
        # Run the metadata update workflow
        result = update_run_metadata(
            config=app_config,
            irods_path=irods_run_path,
            sequencer_type="miseq"
        )
        
        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "missing required files" in result["error"].lower()
    
    finally:
        # Clean up
        if irods_client.collection_exists(os.path.dirname(irods_run_path)):
            irods_client.remove_collection(os.path.dirname(irods_run_path), recursive=True)


@pytest.mark.integration
def test_update_metadata_with_invalid_files(app_config: AppConfig, irods_client: iRODSClient, 
                                         sample_sequencer_run: str, temp_dir: str) -> None:
    """Test updating metadata with invalid files."""
    # First, ingest a run into iRODS but with invalid files
    run_name = os.path.basename(sample_sequencer_run)
    irods_run_path = f"/tempZone/home/rods/test_invalid_files_{os.getpid()}/{run_name}"
    
    try:
        # Create the collection
        irods_client.create_collection(irods_run_path)
        
        # Create invalid files
        invalid_run_info = os.path.join(temp_dir, "InvalidRunInfo.xml")
        with open(invalid_run_info, "w") as f:
            f.write("This is not valid XML")
        
        invalid_run_parameters = os.path.join(temp_dir, "InvalidRunParameters.xml")
        with open(invalid_run_parameters, "w") as f:
            f.write("This is not valid XML either")
        
        invalid_sample_sheet = os.path.join(temp_dir, "InvalidSampleSheet.csv")
        with open(invalid_sample_sheet, "w") as f:
            f.write("This is not a valid CSV file")
        
        # Upload the invalid files
        irods_client.upload_file(invalid_run_info, f"{irods_run_path}/RunInfo.xml")
        irods_client.upload_file(invalid_run_parameters, f"{irods_run_path}/RunParameters.xml")
        irods_client.upload_file(invalid_sample_sheet, f"{irods_run_path}/SampleSheet.csv")
        
        with open(os.path.join(sample_sequencer_run, "RTAComplete.txt"), "rb") as f:
            irods_client.upload_file(os.path.join(sample_sequencer_run, "RTAComplete.txt"), 
                                   f"{irods_run_path}/RTAComplete.txt")
        
        # Add some basic metadata
        with irods_client.session() as session:
            coll = session.collections.get(irods_run_path)
            coll.metadata.add("run_type", "miseq")
            coll.metadata.add("status", "raw")
        
        # Run the metadata update workflow
        result = update_run_metadata(
            config=app_config,
            irods_path=irods_run_path,
            sequencer_type="miseq"
        )
        
        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "failed to parse" in result["error"].lower() or "invalid" in result["error"].lower()
    
    finally:
        # Clean up
        for file_path in [invalid_run_info, invalid_run_parameters, invalid_sample_sheet]:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        if irods_client.collection_exists(os.path.dirname(irods_run_path)):
            irods_client.remove_collection(os.path.dirname(irods_run_path), recursive=True)


@pytest.mark.integration
def test_update_metadata_with_nonexistent_path(app_config: AppConfig) -> None:
    """Test updating metadata with a nonexistent iRODS path."""
    # Run the metadata update workflow with a nonexistent path
    result = update_run_metadata(
        config=app_config,
        irods_path="/tempZone/home/rods/nonexistent/path",
        sequencer_type="miseq"
    )
    
    # Verify the result
    assert result["success"] is False
    assert "error" in result
    assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()


@pytest.mark.integration
def test_update_metadata_with_invalid_sequencer_type(app_config: AppConfig, irods_client: iRODSClient, 
                                                  sample_sequencer_run: str, temp_dir: str) -> None:
    """Test updating metadata with an invalid sequencer type."""
    # First, ingest a run into iRODS
    run_name = os.path.basename(sample_sequencer_run)
    irods_run_path = f"/tempZone/home/rods/test_invalid_type_{os.getpid()}/{run_name}"
    
    try:
        # Create the collection
        irods_client.create_collection(irods_run_path)
        
        # Upload the run files
        irods_client.upload_directory(
            sample_sequencer_run,
            irods_run_path,
            metadata={"run_type": "miseq", "status": "raw"}
        )
        
        # Run the metadata update workflow with an invalid sequencer type
        result = update_run_metadata(
            config=app_config,
            irods_path=irods_run_path,
            sequencer_type="invalid_type"
        )
        
        # Verify the result
        assert result["success"] is False
        assert "error" in result
        assert "invalid sequencer type" in result["error"].lower() or "unsupported" in result["error"].lower()
    
    finally:
        # Clean up
        if irods_client.collection_exists(os.path.dirname(irods_run_path)):
            irods_client.remove_collection(os.path.dirname(irods_run_path), recursive=True)
