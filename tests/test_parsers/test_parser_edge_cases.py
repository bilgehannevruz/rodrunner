"""
Edge case tests for the parsers module.
"""
import os
import pytest
import tempfile
from typing import Dict, Any

from rodrunner.parsers.runinfo import RunInfoParser
from rodrunner.parsers.runparameters import RunParametersParser
from rodrunner.parsers.samplesheet import SampleSheetParser
from rodrunner.parsers.factory import ParserFactory


@pytest.mark.unit
def test_runinfo_parser_malformed_xml(temp_dir: str) -> None:
    """Test parsing malformed RunInfo.xml."""
    # Create a malformed XML file
    malformed_xml_path = os.path.join(temp_dir, "MalformedRunInfo.xml")
    with open(malformed_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
<RunInfo Version="2">
  <Run Id="220101_M00001_0001_000000000-A1B2C" Number="1">
    <Flowcell>000000000-A1B2C</Flowcell>
    <Instrument>M00001</Instrument>
    <Date>1/1/2022</Date>
    <Reads>
      <Read Number="1" NumCycles="151" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="151" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="14" />
  <!-- Missing closing Run tag -->
</RunInfo>
""")
    
    # Parse the file
    parser = RunInfoParser()
    with pytest.raises(Exception):
        parser.parse(malformed_xml_path)


@pytest.mark.unit
def test_runinfo_parser_incomplete_xml(temp_dir: str) -> None:
    """Test parsing incomplete RunInfo.xml."""
    # Create an incomplete XML file
    incomplete_xml_path = os.path.join(temp_dir, "IncompleteRunInfo.xml")
    with open(incomplete_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
<RunInfo Version="2">
  <Run Id="220101_M00001_0001_000000000-A1B2C" Number="1">
    <!-- Missing required elements -->
  </Run>
</RunInfo>
""")
    
    # Parse the file
    parser = RunInfoParser()
    metadata = parser.parse(incomplete_xml_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert "instrument" not in metadata
    assert "flowcell" not in metadata
    assert "date" not in metadata
    assert "reads" not in metadata
    
    # Validate the metadata (should fail due to missing required fields)
    assert parser.validate(metadata) is False


@pytest.mark.unit
def test_runinfo_parser_extra_elements(temp_dir: str) -> None:
    """Test parsing RunInfo.xml with extra elements."""
    # Create an XML file with extra elements
    extra_elements_xml_path = os.path.join(temp_dir, "ExtraElementsRunInfo.xml")
    with open(extra_elements_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
<RunInfo Version="2">
  <Run Id="220101_M00001_0001_000000000-A1B2C" Number="1">
    <Flowcell>000000000-A1B2C</Flowcell>
    <Instrument>M00001</Instrument>
    <Date>1/1/2022</Date>
    <Reads>
      <Read Number="1" NumCycles="151" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="151" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="14" />
    <ExtraElement>Extra Value</ExtraElement>
    <AnotherExtraElement>
      <NestedElement>Nested Value</NestedElement>
    </AnotherExtraElement>
  </Run>
</RunInfo>
""")
    
    # Parse the file
    parser = RunInfoParser()
    metadata = parser.parse(extra_elements_xml_path)
    
    # Verify parsed metadata
    assert metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert metadata["instrument"] == "M00001"
    assert metadata["flowcell"] == "000000000-A1B2C"
    assert metadata["date"] == "1/1/2022"
    assert len(metadata["reads"]) == 4
    
    # Check if extra elements were captured
    assert "extra_element" in metadata
    assert metadata["extra_element"] == "Extra Value"
    assert "another_extra_element" in metadata
    assert "nested_element" in metadata["another_extra_element"]
    assert metadata["another_extra_element"]["nested_element"] == "Nested Value"
    
    # Validate the metadata (should pass as required fields are present)
    assert parser.validate(metadata) is True


@pytest.mark.unit
def test_runparameters_parser_different_formats(temp_dir: str) -> None:
    """Test parsing different formats of RunParameters.xml."""
    # Create a MiSeq format RunParameters.xml
    miseq_xml_path = os.path.join(temp_dir, "MiSeqRunParameters.xml")
    with open(miseq_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
<RunParameters>
  <RunParametersVersion>MiSeq_1_0</RunParametersVersion>
  <Setup>
    <ApplicationName>MiSeq Control Software</ApplicationName>
    <ApplicationVersion>4.0.0.1769</ApplicationVersion>
    <ExperimentName>Test Run</ExperimentName>
  </Setup>
  <RunID>220101_M00001_0001_000000000-A1B2C</RunID>
  <ScannerID>M00001</ScannerID>
  <RTAVersion>2.4.0.3</RTAVersion>
  <Chemistry>Amplicon</Chemistry>
</RunParameters>
""")
    
    # Create a NextSeq format RunParameters.xml
    nextseq_xml_path = os.path.join(temp_dir, "NextSeqRunParameters.xml")
    with open(nextseq_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
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
""")
    
    # Create a NovaSeq format RunParameters.xml
    novaseq_xml_path = os.path.join(temp_dir, "NovaSeqRunParameters.xml")
    with open(novaseq_xml_path, "w") as f:
        f.write("""<?xml version="1.0"?>
<RunParameters>
  <Setup>
    <ApplicationName>NovaSeq Control Software</ApplicationName>
    <ApplicationVersion>1.7.0</ApplicationVersion>
    <ExperimentName>NovaSeq Test Run</ExperimentName>
  </Setup>
  <RunId>220103_A00001_0001_AHGV7DRXX</RunId>
  <InstrumentId>A00001</InstrumentId>
  <RTAVersion>3.4.4</RTAVersion>
  <RunSetupMode>SequencingRun</RunSetupMode>
  <FlowCellMode>SP</FlowCellMode>
</RunParameters>
""")
    
    # Parse the MiSeq format
    parser = RunParametersParser()
    miseq_metadata = parser.parse(miseq_xml_path)
    
    # Verify MiSeq metadata
    assert miseq_metadata["run_id"] == "220101_M00001_0001_000000000-A1B2C"
    assert miseq_metadata["scanner_id"] == "M00001"
    assert miseq_metadata["rta_version"] == "2.4.0.3"
    assert miseq_metadata["chemistry"] == "Amplicon"
    
    # Parse the NextSeq format
    nextseq_metadata = parser.parse(nextseq_xml_path)
    
    # Verify NextSeq metadata
    assert nextseq_metadata["run_id"] == "220102_NS00001_0001_AHGV7DRXX"
    assert nextseq_metadata["scanner_id"] == "NS00001"  # Mapped from InstrumentID
    assert nextseq_metadata["rta_version"] == "2.11.3"
    assert nextseq_metadata["chemistry"] == "NextSeq High"
    
    # Parse the NovaSeq format
    novaseq_metadata = parser.parse(novaseq_xml_path)
    
    # Verify NovaSeq metadata
    assert novaseq_metadata["run_id"] == "220103_A00001_0001_AHGV7DRXX"
    assert novaseq_metadata["scanner_id"] == "A00001"  # Mapped from InstrumentId
    assert novaseq_metadata["rta_version"] == "3.4.4"
    assert "run_setup_mode" in novaseq_metadata
    assert novaseq_metadata["run_setup_mode"] == "SequencingRun"
    assert "flow_cell_mode" in novaseq_metadata
    assert novaseq_metadata["flow_cell_mode"] == "SP"


@pytest.mark.unit
def test_samplesheet_parser_malformed_csv(temp_dir: str) -> None:
    """Test parsing malformed SampleSheet.csv."""
    # Create a malformed CSV file
    malformed_csv_path = os.path.join(temp_dir, "MalformedSampleSheet.csv")
    with open(malformed_csv_path, "w") as f:
        f.write("""[Header]
IEMFileVersion,5
Date,1/1/2022
Workflow,GenerateFASTQ
Application,FASTQ Only

[Reads]
151
151

[Settings]
ReverseComplement,0
Adapter,CTGTCTCTTATACACATCT

[Data]
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,Index_Plate_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
Sample1,Sample1,Plate1,A01,A01,N701,TAAGGCGA,S501,TAGATCGC,Project1,Description1
Sample2,Sample2,Plate1,A02,A02,N702,CGTACTAG,S502,CTCTCTAT,Project1
""")  # Missing a field in the last line
    
    # Parse the file
    parser = SampleSheetParser()
    with pytest.raises(Exception):
        parser.parse(malformed_csv_path)


@pytest.mark.unit
def test_samplesheet_parser_missing_sections(temp_dir: str) -> None:
    """Test parsing SampleSheet.csv with missing sections."""
    # Create a CSV file with missing sections
    missing_sections_csv_path = os.path.join(temp_dir, "MissingSectionsSampleSheet.csv")
    with open(missing_sections_csv_path, "w") as f:
        f.write("""[Header]
IEMFileVersion,5
Date,1/1/2022
Workflow,GenerateFASTQ
Application,FASTQ Only

[Data]
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,Index_Plate_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
Sample1,Sample1,Plate1,A01,A01,N701,TAAGGCGA,S501,TAGATCGC,Project1,Description1
Sample2,Sample2,Plate1,A02,A02,N702,CGTACTAG,S502,CTCTCTAT,Project1,Description2
""")  # Missing Reads and Settings sections
    
    # Parse the file
    parser = SampleSheetParser()
    metadata = parser.parse(missing_sections_csv_path)
    
    # Verify parsed metadata
    assert "header" in metadata
    assert metadata["header"]["IEMFileVersion"] == "5"
    assert "data" in metadata
    assert len(metadata["data"]) == 2
    assert "reads" not in metadata
    assert "settings" not in metadata
    
    # Validate the metadata (should pass if data section is present)
    assert parser.validate(metadata) is True


@pytest.mark.unit
def test_samplesheet_parser_empty_sections(temp_dir: str) -> None:
    """Test parsing SampleSheet.csv with empty sections."""
    # Create a CSV file with empty sections
    empty_sections_csv_path = os.path.join(temp_dir, "EmptySectionsSampleSheet.csv")
    with open(empty_sections_csv_path, "w") as f:
        f.write("""[Header]
IEMFileVersion,5
Date,1/1/2022

[Reads]

[Settings]

[Data]
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,Index_Plate_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
""")  # Empty Reads, Settings, and Data sections
    
    # Parse the file
    parser = SampleSheetParser()
    metadata = parser.parse(empty_sections_csv_path)
    
    # Verify parsed metadata
    assert "header" in metadata
    assert metadata["header"]["IEMFileVersion"] == "5"
    assert "reads" in metadata
    assert metadata["reads"] == []
    assert "settings" in metadata
    assert metadata["settings"] == {}
    assert "data" in metadata
    assert metadata["data"] == []
    
    # Validate the metadata (should fail if data section is empty)
    assert parser.validate(metadata) is False


@pytest.mark.unit
def test_samplesheet_v2_parser_edge_cases(temp_dir: str) -> None:
    """Test parsing edge cases for SampleSheet v2 format."""
    # Create a SampleSheet v2 with missing sections
    missing_sections_v2_path = os.path.join(temp_dir, "MissingSectionsV2.csv")
    with open(missing_sections_v2_path, "w") as f:
        f.write("""[Header]
FileFormatVersion,2
RunName,Test Run
InstrumentPlatform,NextSeq 2000
InstrumentType,NextSeq 2000

[BCLConvert_Data]
Sample_ID,Index,Index2
Sample1,ATCACGTT,AACGTGAT
Sample2,CGATGTTT,AAACATCG
""")  # Missing Reads, BCLConvert_Settings, Cloud_Settings, and Cloud_Data sections
    
    # Parse the file
    parser = SampleSheetParser()
    metadata = parser.parse(missing_sections_v2_path)
    
    # Verify parsed metadata
    assert "header" in metadata
    assert metadata["header"]["FileFormatVersion"] == "2"
    assert "bclconvert_data" in metadata
    assert len(metadata["bclconvert_data"]) == 2
    assert "reads" not in metadata
    assert "bclconvert_settings" not in metadata
    assert "cloud_settings" not in metadata
    assert "cloud_data" not in metadata
    
    # Validate the metadata (should pass if BCLConvert_Data section is present)
    assert parser.validate(metadata) is True
    
    # Create a SampleSheet v2 with extra sections
    extra_sections_v2_path = os.path.join(temp_dir, "ExtraSectionsV2.csv")
    with open(extra_sections_v2_path, "w") as f:
        f.write("""[Header]
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

[Custom_Section]
Key1,Value1
Key2,Value2

[Another_Custom_Section]
CustomKey1,CustomValue1
CustomKey2,CustomValue2
""")  # Added Custom_Section and Another_Custom_Section
    
    # Parse the file
    metadata = parser.parse(extra_sections_v2_path)
    
    # Verify parsed metadata
    assert "header" in metadata
    assert "reads" in metadata
    assert "bclconvert_settings" in metadata
    assert "bclconvert_data" in metadata
    assert "cloud_settings" in metadata
    assert "cloud_data" in metadata
    assert "custom_section" in metadata
    assert metadata["custom_section"]["Key1"] == "Value1"
    assert "another_custom_section" in metadata
    assert metadata["another_custom_section"]["CustomKey1"] == "CustomValue1"
    
    # Validate the metadata (should pass)
    assert parser.validate(metadata) is True


@pytest.mark.unit
def test_parser_factory_with_nonexistent_file() -> None:
    """Test parser factory with nonexistent file."""
    factory = ParserFactory()
    
    # Test parsing a nonexistent file
    with pytest.raises(FileNotFoundError):
        factory.parse_file("/nonexistent/path/to/file.xml")


@pytest.mark.unit
def test_parser_factory_with_empty_directory(temp_dir: str) -> None:
    """Test parser factory with an empty directory."""
    factory = ParserFactory()
    
    # Test parsing an empty directory
    empty_dir = os.path.join(temp_dir, "empty_dir")
    os.makedirs(empty_dir)
    
    metadata = factory.parse_directory(empty_dir)
    assert metadata == {}


@pytest.mark.unit
def test_parser_factory_with_unsupported_files(temp_dir: str) -> None:
    """Test parser factory with unsupported files."""
    factory = ParserFactory()
    
    # Create a directory with unsupported files
    unsupported_dir = os.path.join(temp_dir, "unsupported_dir")
    os.makedirs(unsupported_dir)
    
    # Create some unsupported files
    with open(os.path.join(unsupported_dir, "file1.txt"), "w") as f:
        f.write("This is a text file")
    
    with open(os.path.join(unsupported_dir, "file2.json"), "w") as f:
        f.write('{"key": "value"}')
    
    # Test parsing the directory
    metadata = factory.parse_directory(unsupported_dir)
    assert metadata == {}
    
    # Test getting a parser for an unsupported file
    with pytest.raises(ValueError):
        factory.get_parser("file.txt")


@pytest.mark.unit
def test_parser_factory_with_mixed_files(temp_dir: str, sample_run_info_xml: str, 
                                       sample_run_parameters_xml: str, 
                                       sample_samplesheet_csv: str) -> None:
    """Test parser factory with a mix of supported and unsupported files."""
    factory = ParserFactory()
    
    # Create a directory with mixed files
    mixed_dir = os.path.join(temp_dir, "mixed_dir")
    os.makedirs(mixed_dir)
    
    # Create supported files
    with open(os.path.join(mixed_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    with open(os.path.join(mixed_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    with open(os.path.join(mixed_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Create unsupported files
    with open(os.path.join(mixed_dir, "file1.txt"), "w") as f:
        f.write("This is a text file")
    
    with open(os.path.join(mixed_dir, "file2.json"), "w") as f:
        f.write('{"key": "value"}')
    
    # Test parsing the directory
    metadata = factory.parse_directory(mixed_dir)
    assert "RunInfo.xml" in metadata
    assert "RunParameters.xml" in metadata
    assert "SampleSheet.csv" in metadata
    assert "file1.txt" not in metadata
    assert "file2.json" not in metadata
