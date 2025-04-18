"""
Tests for the SampleSheet parser.
"""
import os
import pytest
from typing import Dict, Any

from rodrunner.parsers.samplesheet import SampleSheetParser


@pytest.mark.unit
def test_samplesheet_parser(temp_dir: str, sample_samplesheet_csv: str) -> None:
    """Test parsing SampleSheet.csv."""
    # Create a test SampleSheet.csv file
    samplesheet_path = os.path.join(temp_dir, "SampleSheet.csv")
    with open(samplesheet_path, "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Parse the file
    parser = SampleSheetParser()
    metadata = parser.parse(samplesheet_path)
    
    # Verify parsed metadata
    assert metadata["header"]["IEMFileVersion"] == "5"
    assert metadata["header"]["Workflow"] == "GenerateFASTQ"
    assert metadata["header"]["Chemistry"] == "Amplicon"
    
    assert metadata["reads"] == ["151", "151"]
    
    assert metadata["settings"]["ReverseComplement"] == "0"
    assert metadata["settings"]["Adapter"] == "CTGTCTCTTATACACATCT"
    
    assert len(metadata["data"]) == 2
    assert metadata["data"][0]["Sample_ID"] == "Sample1"
    assert metadata["data"][0]["Sample_Project"] == "Project1"
    assert metadata["data"][1]["Sample_ID"] == "Sample2"
    assert metadata["data"][1]["index"] == "CGTACTAG"


@pytest.mark.unit
def test_samplesheet_parser_validation(temp_dir: str, sample_samplesheet_csv: str) -> None:
    """Test validation of SampleSheet.csv metadata."""
    # Create a test SampleSheet.csv file
    samplesheet_path = os.path.join(temp_dir, "SampleSheet.csv")
    with open(samplesheet_path, "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Parse and validate the file
    parser = SampleSheetParser()
    metadata = parser.parse(samplesheet_path)
    assert parser.validate(metadata) is True
    
    # Test validation with missing required sections
    incomplete_metadata = metadata.copy()
    del incomplete_metadata["data"]
    assert parser.validate(incomplete_metadata) is False


@pytest.mark.unit
def test_samplesheet_parser_invalid_format(temp_dir: str) -> None:
    """Test parsing invalid SampleSheet format."""
    # Create an invalid SampleSheet file
    invalid_sheet_path = os.path.join(temp_dir, "InvalidSampleSheet.csv")
    with open(invalid_sheet_path, "w") as f:
        f.write("This is not a valid SampleSheet format")
    
    # Parse the file
    parser = SampleSheetParser()
    with pytest.raises(Exception):
        parser.parse(invalid_sheet_path)


@pytest.mark.unit
def test_samplesheet_v2_parser(temp_dir: str) -> None:
    """Test parsing SampleSheet v2 format."""
    # Create a SampleSheet v2 format file
    samplesheet_v2 = """[Header]
FileFormatVersion,2
RunName,Test Run
InstrumentPlatform,NextSeq 2000
InstrumentType,NextSeq 2000

[Reads]
Read1Cycles,151
Read2Cycles,151
Index1Cycles,10
Index2Cycles,10

[BCLConvert_Settings]
AdapterRead1,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA
AdapterRead2,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT

[BCLConvert_Data]
Sample_ID,Index,Index2
Sample1,ATCACGTT,AACGTGAT
Sample2,CGATGTTT,AAACATCG

[Cloud_Settings]
Cloud_LOT_Enabled,true

[Cloud_Data]
Sample_ID,Project
Sample1,Project1
Sample2,Project1
"""
    
    samplesheet_v2_path = os.path.join(temp_dir, "SampleSheetV2.csv")
    with open(samplesheet_v2_path, "w") as f:
        f.write(samplesheet_v2)
    
    # Parse the file
    parser = SampleSheetParser()
    metadata = parser.parse(samplesheet_v2_path)
    
    # Verify parsed metadata
    assert metadata["header"]["FileFormatVersion"] == "2"
    assert metadata["header"]["InstrumentPlatform"] == "NextSeq 2000"
    
    assert metadata["reads"]["Read1Cycles"] == "151"
    assert metadata["reads"]["Read2Cycles"] == "151"
    
    assert metadata["bclconvert_settings"]["AdapterRead1"] == "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"
    
    assert len(metadata["bclconvert_data"]) == 2
    assert metadata["bclconvert_data"][0]["Sample_ID"] == "Sample1"
    assert metadata["bclconvert_data"][0]["Index"] == "ATCACGTT"
    
    assert metadata["cloud_data"][1]["Sample_ID"] == "Sample2"
    assert metadata["cloud_data"][1]["Project"] == "Project1"
    
    # Validate the metadata
    assert parser.validate(metadata) is True
