"""
Tests for the RunInfo parser.
"""
import os
import pytest
from typing import Dict, Any

from rodrunner.parsers.runinfo import RunInfoParser


@pytest.mark.unit
def test_runinfo_parser(temp_dir: str, sample_run_info_xml: str) -> None:
    """Test parsing RunInfo.xml."""
    # Create a test RunInfo.xml file
    run_info_path = os.path.join(temp_dir, "RunInfo.xml")
    with open(run_info_path, "w") as f:
        f.write(sample_run_info_xml)
    
    # Parse the file
    parser = RunInfoParser()
    metadata = parser.parse(run_info_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert metadata["instrument"] == "M00001"
    assert metadata["flowcell"] == "000000000-A1B2C"
    assert metadata["date"] == "1/1/2022"
    assert len(metadata["reads"]) == 4
    assert metadata["reads"][0]["number"] == "1"
    assert metadata["reads"][0]["num_cycles"] == "151"
    assert metadata["reads"][0]["is_indexed_read"] == "N"


@pytest.mark.unit
def test_runinfo_parser_validation(temp_dir: str, sample_run_info_xml: str) -> None:
    """Test validation of RunInfo.xml metadata."""
    # Create a test RunInfo.xml file
    run_info_path = os.path.join(temp_dir, "RunInfo.xml")
    with open(run_info_path, "w") as f:
        f.write(sample_run_info_xml)
    
    # Parse and validate the file
    parser = RunInfoParser()
    metadata = parser.parse(run_info_path)
    assert parser.validate(metadata) is True
    
    # Test validation with missing required fields
    incomplete_metadata = metadata.copy()
    del incomplete_metadata["run_id"]
    assert parser.validate(incomplete_metadata) is False


@pytest.mark.unit
def test_runinfo_parser_invalid_xml(temp_dir: str) -> None:
    """Test parsing invalid XML."""
    # Create an invalid XML file
    invalid_xml_path = os.path.join(temp_dir, "InvalidRunInfo.xml")
    with open(invalid_xml_path, "w") as f:
        f.write("This is not valid XML")
    
    # Parse the file
    parser = RunInfoParser()
    with pytest.raises(Exception):
        parser.parse(invalid_xml_path)


@pytest.mark.unit
def test_runinfo_parser_missing_elements(temp_dir: str) -> None:
    """Test parsing XML with missing elements."""
    # Create XML with missing elements
    missing_elements_xml = """<?xml version="1.0"?>
<RunInfo Version="2">
  <Run Id="220101_M00001_0001_000000000-A1B2C" Number="1">
    <Flowcell>000000000-A1B2C</Flowcell>
    <!-- Missing Instrument element -->
    <Date>1/1/2022</Date>
    <!-- Missing Reads element -->
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="14" />
  </Run>
</RunInfo>
"""
    
    missing_elements_path = os.path.join(temp_dir, "MissingElements.xml")
    with open(missing_elements_path, "w") as f:
        f.write(missing_elements_xml)
    
    # Parse the file
    parser = RunInfoParser()
    metadata = parser.parse(missing_elements_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert "instrument" not in metadata
    assert metadata["flowcell"] == "000000000-A1B2C"
    assert metadata["date"] == "1/1/2022"
    assert "reads" not in metadata
    
    # Validate the metadata (should fail due to missing required fields)
    assert parser.validate(metadata) is False
