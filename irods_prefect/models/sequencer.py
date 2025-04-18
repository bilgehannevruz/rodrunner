"""
Models for sequencer data.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator


class Read(BaseModel):
    """Model for a sequencing read."""
    number: str = Field(..., description="Read number")
    num_cycles: str = Field(..., description="Number of cycles")
    is_indexed_read: str = Field(..., description="Whether this is an indexed read")


class FlowcellLayout(BaseModel):
    """Model for a flowcell layout."""
    lane_count: str = Field(..., description="Number of lanes")
    surface_count: str = Field(..., description="Number of surfaces")
    swath_count: str = Field(..., description="Number of swaths")
    tile_count: str = Field(..., description="Number of tiles")


class RunInfo(BaseModel):
    """Model for RunInfo.xml data."""
    run_id: str = Field(..., description="Run ID")
    run_number: str = Field(..., description="Run number")
    flowcell: str = Field(..., description="Flowcell ID")
    instrument: str = Field(..., description="Instrument ID")
    date: str = Field(..., description="Run date")
    reads: List[Read] = Field(..., description="List of reads")
    flowcell_layout: FlowcellLayout = Field(..., description="Flowcell layout")


class RunParameters(BaseModel):
    """Model for RunParameters.xml data."""
    instrument_type: str = Field(..., description="Instrument type")
    run_id: str = Field(..., description="Run ID")
    experiment_name: Optional[str] = Field(None, description="Experiment name")
    sequencing_kit_number: Optional[str] = Field(None, description="Sequencing kit number")
    read1_cycles: str = Field(..., description="Number of cycles for read 1")
    read2_cycles: str = Field(..., description="Number of cycles for read 2")
    index1_cycles: str = Field(..., description="Number of cycles for index 1")
    index2_cycles: str = Field(..., description="Number of cycles for index 2")


class Sample(BaseModel):
    """Model for a sample in a SampleSheet."""
    sample_id: str = Field(..., description="Sample ID")
    sample_name: str = Field(..., description="Sample name")
    sample_plate: Optional[str] = Field(None, description="Sample plate")
    sample_well: Optional[str] = Field(None, description="Sample well")
    index: str = Field(..., description="Index sequence")
    index2: Optional[str] = Field(None, description="Index 2 sequence")
    sample_project: str = Field(..., description="Sample project")
    description: Optional[str] = Field(None, description="Sample description")


class SampleSheet(BaseModel):
    """Model for SampleSheet data."""
    version: int = Field(..., description="SampleSheet version")
    header: Dict[str, str] = Field(..., description="Header section")
    samples: List[Sample] = Field(..., description="List of samples")


class SequencerRun(BaseModel):
    """Model for a sequencer run."""
    run_info: RunInfo = Field(..., description="RunInfo.xml data")
    run_parameters: RunParameters = Field(..., description="RunParameters.xml data")
    sample_sheet: SampleSheet = Field(..., description="SampleSheet data")
    sequencer_type: str = Field(..., description="Sequencer type")
    projects: List[str] = Field(..., description="List of projects in the run")
    status: str = Field("new", description="Run status")
    
    class Config:
        schema_extra = {
            "example": {
                "run_info": {
                    "run_id": "220101_M00001_0001_000000000-A1B2C",
                    "run_number": "0001",
                    "flowcell": "000000000-A1B2C",
                    "instrument": "M00001",
                    "date": "220101",
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
                        {
                            "number": "3",
                            "num_cycles": "8",
                            "is_indexed_read": "Y"
                        },
                        {
                            "number": "4",
                            "num_cycles": "151",
                            "is_indexed_read": "N"
                        }
                    ],
                    "flowcell_layout": {
                        "lane_count": "1",
                        "surface_count": "2",
                        "swath_count": "1",
                        "tile_count": "14"
                    }
                },
                "run_parameters": {
                    "instrument_type": "MiSeq",
                    "run_id": "220101_M00001_0001_000000000-A1B2C",
                    "experiment_name": "Experiment1",
                    "sequencing_kit_number": "MS-102-3001",
                    "read1_cycles": "151",
                    "read2_cycles": "151",
                    "index1_cycles": "8",
                    "index2_cycles": "8"
                },
                "sample_sheet": {
                    "version": 1,
                    "header": {
                        "IEMFileVersion": "4",
                        "Investigator Name": "John Doe",
                        "Experiment Name": "Experiment1",
                        "Date": "1/1/2022",
                        "Workflow": "GenerateFASTQ",
                        "Application": "FASTQ Only",
                        "Assay": "Nextera XT",
                        "Description": "Sequencing run",
                        "Chemistry": "Amplicon"
                    },
                    "samples": [
                        {
                            "sample_id": "Sample1",
                            "sample_name": "Sample1",
                            "sample_plate": "Plate1",
                            "sample_well": "A1",
                            "index": "ATCACG",
                            "index2": "AGATCT",
                            "sample_project": "Project1",
                            "description": "Sample 1"
                        },
                        {
                            "sample_id": "Sample2",
                            "sample_name": "Sample2",
                            "sample_plate": "Plate1",
                            "sample_well": "A2",
                            "index": "CGATGT",
                            "index2": "TTAGGC",
                            "sample_project": "Project2",
                            "description": "Sample 2"
                        }
                    ]
                },
                "sequencer_type": "miseq",
                "projects": ["Project1", "Project2"],
                "status": "new"
            }
        }
