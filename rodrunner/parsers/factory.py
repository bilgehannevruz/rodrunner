"""
Factory for creating parsers.
"""
import os
from typing import Dict, Any, Optional

from rodrunner.parsers.base import BaseParser
from rodrunner.parsers.runinfo import RunInfoParser
from rodrunner.parsers.runparameters import RunParametersParser
from rodrunner.parsers.samplesheet import SampleSheetParser


class ParserFactory:
    """Factory for creating parsers."""
    
    @staticmethod
    def create_parser(file_path: str) -> Optional[BaseParser]:
        """
        Create a parser for the given file.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Parser instance, or None if no parser is available
        """
        if not os.path.exists(file_path):
            return None
        
        file_name = os.path.basename(file_path).lower()
        
        if file_name == 'runinfo.xml':
            return RunInfoParser()
        elif file_name == 'runparameters.xml':
            return RunParametersParser()
        elif file_name == 'samplesheet.csv':
            return SampleSheetParser()
        
        return None
    
    @staticmethod
    def parse_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a file using the appropriate parser.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary of extracted metadata, or None if parsing fails
        """
        parser = ParserFactory.create_parser(file_path)
        
        if parser:
            return parser.get_metadata(file_path)
        
        return None
    
    @staticmethod
    def parse_sequencer_run(run_dir: str) -> Dict[str, Any]:
        """
        Parse all metadata files in a sequencer run directory.
        
        Args:
            run_dir: Path to the sequencer run directory
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        
        # Parse RunInfo.xml
        run_info_path = os.path.join(run_dir, 'RunInfo.xml')
        if os.path.exists(run_info_path):
            run_info_parser = RunInfoParser()
            run_info_metadata = run_info_parser.get_metadata(run_info_path)
            if run_info_metadata:
                metadata['run_info'] = run_info_metadata
                
                # Determine sequencer type
                sequencer_type = run_info_parser.get_sequencer_type(run_info_metadata)
                if sequencer_type:
                    metadata['sequencer_type'] = sequencer_type
        
        # Parse RunParameters.xml
        run_parameters_path = os.path.join(run_dir, 'RunParameters.xml')
        if os.path.exists(run_parameters_path):
            run_parameters_parser = RunParametersParser()
            run_parameters_metadata = run_parameters_parser.get_metadata(run_parameters_path)
            if run_parameters_metadata:
                metadata['run_parameters'] = run_parameters_metadata
        
        # Parse SampleSheet.csv
        sample_sheet_path = os.path.join(run_dir, 'SampleSheet.csv')
        if os.path.exists(sample_sheet_path):
            sample_sheet_parser = SampleSheetParser()
            sample_sheet_metadata = sample_sheet_parser.get_metadata(sample_sheet_path)
            if sample_sheet_metadata:
                metadata['sample_sheet'] = sample_sheet_metadata
                
                # Extract projects
                projects = sample_sheet_parser.get_projects(sample_sheet_metadata)
                if projects:
                    metadata['projects'] = projects
        
        return metadata
