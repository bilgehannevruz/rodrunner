"""
Common parsing tasks for Prefect workflows.
"""
from typing import Dict, List, Optional, Union, Any
import os

from prefect import task

from rodrunner.parsers.factory import ParserFactory
from rodrunner.parsers.runinfo import RunInfoParser
from rodrunner.parsers.runparameters import RunParametersParser
from rodrunner.parsers.samplesheet import SampleSheetParser


@task(name="parse_run_info")
def parse_run_info(run_info_path: str) -> Dict[str, Any]:
    """
    Parse a RunInfo.xml file.
    
    Args:
        run_info_path: Path to the RunInfo.xml file
        
    Returns:
        Dictionary of extracted metadata
    """
    parser = RunInfoParser()
    metadata = parser.get_metadata(run_info_path)
    
    if metadata is None:
        raise ValueError(f"Failed to parse RunInfo.xml: {run_info_path}")
    
    return metadata


@task(name="parse_run_parameters")
def parse_run_parameters(run_parameters_path: str) -> Dict[str, Any]:
    """
    Parse a RunParameters.xml file.
    
    Args:
        run_parameters_path: Path to the RunParameters.xml file
        
    Returns:
        Dictionary of extracted metadata
    """
    parser = RunParametersParser()
    metadata = parser.get_metadata(run_parameters_path)
    
    if metadata is None:
        raise ValueError(f"Failed to parse RunParameters.xml: {run_parameters_path}")
    
    return metadata


@task(name="parse_sample_sheet")
def parse_sample_sheet(sample_sheet_path: str) -> Dict[str, Any]:
    """
    Parse a SampleSheet.csv file.
    
    Args:
        sample_sheet_path: Path to the SampleSheet.csv file
        
    Returns:
        Dictionary of extracted metadata
    """
    parser = SampleSheetParser()
    metadata = parser.get_metadata(sample_sheet_path)
    
    if metadata is None:
        raise ValueError(f"Failed to parse SampleSheet.csv: {sample_sheet_path}")
    
    return metadata


@task(name="get_sequencer_type")
def get_sequencer_type(run_info_metadata: Dict[str, Any]) -> str:
    """
    Determine the sequencer type from RunInfo.xml metadata.
    
    Args:
        run_info_metadata: Dictionary of RunInfo.xml metadata
        
    Returns:
        Sequencer type
    """
    parser = RunInfoParser()
    sequencer_type = parser.get_sequencer_type(run_info_metadata)
    
    if sequencer_type is None:
        raise ValueError(f"Failed to determine sequencer type from metadata: {run_info_metadata}")
    
    return sequencer_type


@task(name="get_projects_from_sample_sheet")
def get_projects_from_sample_sheet(sample_sheet_metadata: Dict[str, Any]) -> List[str]:
    """
    Get the list of projects from SampleSheet.csv metadata.
    
    Args:
        sample_sheet_metadata: Dictionary of SampleSheet.csv metadata
        
    Returns:
        List of project names
    """
    parser = SampleSheetParser()
    projects = parser.get_projects(sample_sheet_metadata)
    
    return projects


@task(name="parse_sequencer_run")
def parse_sequencer_run(run_dir: str) -> Dict[str, Any]:
    """
    Parse all metadata files in a sequencer run directory.
    
    Args:
        run_dir: Path to the sequencer run directory
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = ParserFactory.parse_sequencer_run(run_dir)
    
    if not metadata:
        raise ValueError(f"Failed to parse sequencer run: {run_dir}")
    
    return metadata
