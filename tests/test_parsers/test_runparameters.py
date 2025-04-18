"""
Tests for the RunParameters parser.
"""
import os
import pytest
from typing import Dict, Any

from rodrunner.parsers.runparameters import RunParametersParser


@pytest.mark.unit
def test_runparameters_parser(temp_dir: str, sample_run_parameters_xml: str) -> None:
    """Test parsing RunParameters.xml."""
    # Create a test RunParameters.xml file
    run_parameters_path = os.path.join(temp_dir, "RunParameters.xml")
    with open(run_parameters_path, "w") as f:
        f.write(sample_run_parameters_xml)
    
    # Parse the file
    parser = RunParametersParser()
    metadata = parser.parse(run_parameters_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert metadata["scanner_id"] == "M00001"
    assert metadata["rta_version"] == "2.4.0.3"
    assert metadata["chemistry"] == "Amplicon"
    assert metadata["application_name"] == "MiSeq Control Software"
    assert metadata["application_version"] == "4.0.0.1769"
    assert metadata["experiment_name"] == "Test Run"


@pytest.mark.unit
def test_runparameters_parser_validation(temp_dir: str, sample_run_parameters_xml: str) -> None:
    """Test validation of RunParameters.xml metadata."""
    # Create a test RunParameters.xml file
    run_parameters_path = os.path.join(temp_dir, "RunParameters.xml")
    with open(run_parameters_path, "w") as f:
        f.write(sample_run_parameters_xml)
    
    # Parse and validate the file
    parser = RunParametersParser()
    metadata = parser.parse(run_parameters_path)
    assert parser.validate(metadata) is True
    
    # Test validation with missing required fields
    incomplete_metadata = metadata.copy()
    del incomplete_metadata["run_id"]
    assert parser.validate(incomplete_metadata) is False


@pytest.mark.unit
def test_runparameters_parser_invalid_xml(temp_dir: str) -> None:
    """Test parsing invalid XML."""
    # Create an invalid XML file
    invalid_xml_path = os.path.join(temp_dir, "InvalidRunParameters.xml")
    with open(invalid_xml_path, "w") as f:
        f.write("This is not valid XML")
    
    # Parse the file
    parser = RunParametersParser()
    with pytest.raises(Exception):
        parser.parse(invalid_xml_path)


@pytest.mark.unit
def test_runparameters_parser_different_formats(temp_dir: str) -> None:
    """Test parsing different formats of RunParameters.xml."""
    # Create a NextSeq format RunParameters.xml
    nextseq_xml = """<?xml version="1.0"?>
<RunParameters>
  <Setup>
    <ApplicationName>NextSeq Control Software</ApplicationName>
    <ApplicationVersion>4.0.0</ApplicationVersion>
    <ExperimentName>NextSeq Test Run</ExperimentName>
  </Setup>
  <RunID>220102_NS00001_0001_AHGV7DRXX</RunID>
  <InstrumentID>NS00001</InstrumentID>
  <RTAVersion>2.11.3</RTAVersion>
  <Chemistry>NextSeq High</Chemistry>
</RunParameters>
"""
    
    nextseq_path = os.path.join(temp_dir, "NextSeqRunParameters.xml")
    with open(nextseq_path, "w") as f:
        f.write(nextseq_xml)
    
    # Parse the file
    parser = RunParametersParser()
    metadata = parser.parse(nextseq_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220102_NS00001_0001_AHGV7DRXX"
    assert metadata["scanner_id"] == "NS00001"  # Mapped from InstrumentID
    assert metadata["rta_version"] == "2.11.3"
    assert metadata["chemistry"] == "NextSeq High"
    assert metadata["application_name"] == "NextSeq Control Software"
    
    # Validate the metadata
    assert parser.validate(metadata) is True
