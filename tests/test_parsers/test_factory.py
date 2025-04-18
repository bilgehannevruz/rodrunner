"""
Tests for the parser factory.
"""
import os
import pytest
from typing import Dict, Any

from rodrunner.parsers.factory import ParserFactory
from rodrunner.parsers.runinfo import RunInfoParser
from rodrunner.parsers.runparameters import RunParametersParser
from rodrunner.parsers.samplesheet import SampleSheetParser


@pytest.mark.unit
def test_parser_factory_get_parser() -> None:
    """Test getting parsers from the factory."""
    factory = ParserFactory()
    
    # Test getting RunInfo parser
    run_info_parser = factory.get_parser("RunInfo.xml")
    assert isinstance(run_info_parser, RunInfoParser)
    
    # Test getting RunParameters parser
    run_parameters_parser = factory.get_parser("RunParameters.xml")
    assert isinstance(run_parameters_parser, RunParametersParser)
    
    # Test getting SampleSheet parser
    samplesheet_parser = factory.get_parser("SampleSheet.csv")
    assert isinstance(samplesheet_parser, SampleSheetParser)
    
    # Test getting parser for unknown file
    with pytest.raises(ValueError):
        factory.get_parser("unknown.txt")


@pytest.mark.unit
def test_parser_factory_parse_file(temp_dir: str, sample_run_info_xml: str, 
                                 sample_run_parameters_xml: str, 
                                 sample_samplesheet_csv: str) -> None:
    """Test parsing files using the factory."""
    factory = ParserFactory()
    
    # Create test files
    run_info_path = os.path.join(temp_dir, "RunInfo.xml")
    with open(run_info_path, "w") as f:
        f.write(sample_run_info_xml)
    
    run_parameters_path = os.path.join(temp_dir, "RunParameters.xml")
    with open(run_parameters_path, "w") as f:
        f.write(sample_run_parameters_xml)
    
    samplesheet_path = os.path.join(temp_dir, "SampleSheet.csv")
    with open(samplesheet_path, "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Test parsing RunInfo.xml
    run_info_metadata = factory.parse_file(run_info_path)
    assert run_info_metadata is not None
    assert "run_id" in run_info_metadata
    assert run_info_metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    
    # Test parsing RunParameters.xml
    run_parameters_metadata = factory.parse_file(run_parameters_path)
    assert run_parameters_metadata is not None
    assert "run_id" in run_parameters_metadata
    assert run_parameters_metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    
    # Test parsing SampleSheet.csv
    samplesheet_metadata = factory.parse_file(samplesheet_path)
    assert samplesheet_metadata is not None
    assert "header" in samplesheet_metadata
    assert "data" in samplesheet_metadata
    assert len(samplesheet_metadata["data"]) == 2


@pytest.mark.unit
def test_parser_factory_parse_directory(temp_dir: str, sample_run_info_xml: str, 
                                      sample_run_parameters_xml: str, 
                                      sample_samplesheet_csv: str) -> None:
    """Test parsing a directory of files using the factory."""
    factory = ParserFactory()
    
    # Create test files in a directory
    run_dir = os.path.join(temp_dir, "run_dir")
    os.makedirs(run_dir)
    
    with open(os.path.join(run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    with open(os.path.join(run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    with open(os.path.join(run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Also create a file that shouldn't be parsed
    with open(os.path.join(run_dir, "other.txt"), "w") as f:
        f.write("This file should be ignored")
    
    # Test parsing the directory
    metadata = factory.parse_directory(run_dir)
    assert metadata is not None
    assert "RunInfo.xml" in metadata
    assert "RunParameters.xml" in metadata
    assert "SampleSheet.csv" in metadata
    assert "other.txt" not in metadata
    
    # Verify the parsed metadata
    assert metadata["RunInfo.xml"]["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert metadata["RunParameters.xml"]["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert len(metadata["SampleSheet.csv"]["data"]) == 2
