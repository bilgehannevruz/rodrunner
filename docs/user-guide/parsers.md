# Parsers

The parsers module provides parsers for extracting metadata from sequencer-specific files, including RunInfo.xml, RunParameters.xml, and SampleSheet.csv. It supports various sequencer types and file formats.

## Key Features

- **Extensible parser architecture** with a common base class
- **Specialized parsers** for different file types
- **Parser factory** for selecting the appropriate parser
- **Support for multiple sequencer types** (MiSeq, NextSeq, NovaSeq, etc.)
- **Support for different file formats** (including SampleSheet v2)

## Available Parsers

The following parsers are available:

- **RunInfoParser**: Parses RunInfo.xml files
- **RunParametersParser**: Parses RunParameters.xml files
- **SampleSheetParser**: Parses SampleSheet.csv files (both v1 and v2 formats)

## Basic Usage

### Using the Parser Factory

The easiest way to use the parsers is through the parser factory, which selects the appropriate parser based on the file name:

```python
from rodrunner.parsers.factory import ParserFactory

# Create a parser factory
factory = ParserFactory()

# Parse a file
metadata = factory.parse_file("/path/to/RunInfo.xml")
print(metadata)

# Parse a directory
metadata_dict = factory.parse_directory("/path/to/sequencer/run")
print(metadata_dict["RunInfo.xml"])
print(metadata_dict["RunParameters.xml"])
print(metadata_dict["SampleSheet.csv"])
```

### Using Individual Parsers

You can also use the individual parsers directly:

```python
from rodrunner.parsers.runinfo import RunInfoParser
from rodrunner.parsers.runparameters import RunParametersParser
from rodrunner.parsers.samplesheet import SampleSheetParser

# Parse RunInfo.xml
run_info_parser = RunInfoParser()
run_info_metadata = run_info_parser.parse("/path/to/RunInfo.xml")
print(run_info_metadata)

# Parse RunParameters.xml
run_parameters_parser = RunParametersParser()
run_parameters_metadata = run_parameters_parser.parse("/path/to/RunParameters.xml")
print(run_parameters_metadata)

# Parse SampleSheet.csv
samplesheet_parser = SampleSheetParser()
samplesheet_metadata = samplesheet_parser.parse("/path/to/SampleSheet.csv")
print(samplesheet_metadata)
```

## Metadata Structure

### RunInfo.xml Metadata

The RunInfo parser extracts the following metadata:

```python
{
    "run_id": "220101_M00001_0001_000000000-A1B2C",
    "instrument": "M00001",
    "flowcell": "000000000-A1B2C",
    "date": "1/1/2022",
    "reads": [
        {
            "number": "1",
            "num_cycles": "151",
            "is_indexed_read": "N"
        },
        {
            "number": "2",
            "num_cycles": "8",
            "is_indexed_read": "Y"
        },
        # ...
    ],
    "flowcell_layout": {
        "lane_count": "1",
        "surface_count": "2",
        "swath_count": "1",
        "tile_count": "14"
    }
}
```

### RunParameters.xml Metadata

The RunParameters parser extracts the following metadata:

```python
{
    "run_id": "220101_M00001_0001_000000000-A1B2C",
    "scanner_id": "M00001",
    "rta_version": "2.4.0.3",
    "chemistry": "Amplicon",
    "application_name": "MiSeq Control Software",
    "application_version": "4.0.0.1769",
    "experiment_name": "Test Run"
}
```

### SampleSheet.csv Metadata (v1)

The SampleSheet parser extracts the following metadata for v1 format:

```python
{
    "header": {
        "IEMFileVersion": "5",
        "Date": "1/1/2022",
        "Workflow": "GenerateFASTQ",
        "Application": "FASTQ Only",
        "Instrument Type": "MiSeq",
        "Assay": "Nextera XT",
        "Index Adapters": "Nextera XT Index Kit (96 Indexes, 384 Samples)",
        "Chemistry": "Amplicon"
    },
    "reads": ["151", "151"],
    "settings": {
        "ReverseComplement": "0",
        "Adapter": "CTGTCTCTTATACACATCT"
    },
    "data": [
        {
            "Sample_ID": "Sample1",
            "Sample_Name": "Sample1",
            "Sample_Plate": "Plate1",
            "Sample_Well": "A01",
            "Index_Plate_Well": "A01",
            "I7_Index_ID": "N701",
            "index": "TAAGGCGA",
            "I5_Index_ID": "S501",
            "index2": "TAGATCGC",
            "Sample_Project": "Project1",
            "Description": "Description1"
        },
        # ...
    ]
}
```

### SampleSheet.csv Metadata (v2)

The SampleSheet parser extracts the following metadata for v2 format:

```python
{
    "header": {
        "FileFormatVersion": "2",
        "RunName": "Test Run",
        "InstrumentPlatform": "NextSeq 2000",
        "InstrumentType": "NextSeq 2000"
    },
    "reads": {
        "Read1Cycles": "151",
        "Read2Cycles": "151",
        "Index1Cycles": "10",
        "Index2Cycles": "10"
    },
    "bclconvert_settings": {
        "AdapterRead1": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA",
        "AdapterRead2": "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT"
    },
    "bclconvert_data": [
        {
            "Sample_ID": "Sample1",
            "Index": "ATCACGTT",
            "Index2": "AACGTGAT"
        },
        # ...
    ],
    "cloud_settings": {
        "Cloud_LOT_Enabled": "true"
    },
    "cloud_data": [
        {
            "Sample_ID": "Sample1",
            "Project": "Project1"
        },
        # ...
    ]
}
```

## Advanced Usage

### Validating Metadata

Each parser has a `validate` method that checks if the extracted metadata is valid:

```python
from rodrunner.parsers.runinfo import RunInfoParser

# Parse RunInfo.xml
run_info_parser = RunInfoParser()
metadata = run_info_parser.parse("/path/to/RunInfo.xml")

# Validate the metadata
if run_info_parser.validate(metadata):
    print("Metadata is valid")
else:
    print("Metadata is invalid")
```

### Creating Custom Parsers

You can create custom parsers by extending the `BaseParser` class:

```python
from rodrunner.parsers.base import BaseParser
from typing import Dict, Any

class CustomParser(BaseParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        # Implement parsing logic
        metadata = {}
        with open(file_path, 'r') as f:
            # Parse the file
            pass
        return metadata
    
    def validate(self, metadata: Dict[str, Any]) -> bool:
        # Implement validation logic
        return True
```

### Extending the Parser Factory

You can extend the parser factory to support custom parsers:

```python
from rodrunner.parsers.factory import ParserFactory
from my_custom_parsers import CustomParser

class ExtendedParserFactory(ParserFactory):
    def get_parser(self, file_path: str):
        # Check for custom file types
        if file_path.endswith(".custom"):
            return CustomParser()
        
        # Fall back to the default parser factory
        return super().get_parser(file_path)
```

## Examples

### Extracting Metadata from a Sequencer Run

```python
from rodrunner.parsers.factory import ParserFactory
import os

# Create a parser factory
factory = ParserFactory()

# Parse a sequencer run directory
run_dir = "/path/to/sequencer/run"
metadata = factory.parse_directory(run_dir)

# Extract key metadata
run_id = metadata["RunInfo.xml"]["run_id"]
instrument = metadata["RunInfo.xml"]["instrument"]
chemistry = metadata["RunParameters.xml"]["chemistry"]
sample_count = len(metadata["SampleSheet.csv"]["data"])

print(f"Run ID: {run_id}")
print(f"Instrument: {instrument}")
print(f"Chemistry: {chemistry}")
print(f"Sample Count: {sample_count}")

# Print sample information
print("\nSamples:")
for sample in metadata["SampleSheet.csv"]["data"]:
    print(f"  {sample['Sample_ID']} ({sample['Sample_Project']})")
```

### Converting Metadata to iRODS Metadata

```python
from rodrunner.parsers.factory import ParserFactory
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient
import os

# Create a parser factory
factory = ParserFactory()

# Parse a sequencer run directory
run_dir = "/path/to/sequencer/run"
metadata = factory.parse_directory(run_dir)

# Extract key metadata for iRODS
irods_metadata = {
    "run_id": metadata["RunInfo.xml"]["run_id"],
    "instrument": metadata["RunInfo.xml"]["instrument"],
    "date": metadata["RunInfo.xml"]["date"],
    "chemistry": metadata["RunParameters.xml"]["chemistry"],
    "sample_count": str(len(metadata["SampleSheet.csv"]["data"])),
    "run_type": "miseq",
    "status": "metadata_extracted"
}

# Create an iRODS client
config = get_config()
irods_client = iRODSClient(config.irods)

# Upload the run directory with metadata
irods_path = f"/tempZone/home/rods/sequencer/{os.path.basename(run_dir)}"
coll = irods_client.upload_directory(run_dir, irods_path, metadata=irods_metadata)

print(f"Uploaded run to {irods_path} with metadata")
```

## API Reference

For detailed API documentation, see the [Parsers API Reference](../api-reference/parsers.md).
