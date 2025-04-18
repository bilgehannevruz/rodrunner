"""
Parser for SampleSheet files (both v1 and v2 formats).
"""
import csv
import os
from typing import Dict, Any, List, Optional, Tuple

from rodrunner.parsers.base import BaseParser


class SampleSheetParser(BaseParser):
    """Parser for SampleSheet files."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a SampleSheet file and extract metadata.
        
        Args:
            file_path: Path to the SampleSheet file
            
        Returns:
            Dictionary of extracted metadata
        """
        # Determine the SampleSheet version
        version = self._determine_version(file_path)
        
        if version == 1:
            return self._parse_v1(file_path)
        elif version == 2:
            return self._parse_v2(file_path)
        else:
            return {}
    
    def _determine_version(self, file_path: str) -> int:
        """
        Determine the SampleSheet version.
        
        Args:
            file_path: Path to the SampleSheet file
            
        Returns:
            SampleSheet version (1 or 2)
        """
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            
            # Check for v2 format
            if first_line == '[Header]' and 'FileFormatVersion' in f.readline():
                return 2
            
            # Default to v1 format
            return 1
    
    def _parse_v1(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a v1 SampleSheet file.
        
        Args:
            file_path: Path to the SampleSheet file
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            'version': 1,
            'header': {},
            'reads': [],
            'settings': {},
            'data': []
        }
        
        current_section = None
        
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if not row:
                    continue
                
                # Check for section headers
                if row[0].startswith('[') and row[0].endswith(']'):
                    current_section = row[0][1:-1].lower()
                    continue
                
                # Process sections
                if current_section == 'header':
                    if len(row) >= 2:
                        metadata['header'][row[0]] = row[1]
                
                elif current_section == 'reads':
                    if row[0].isdigit():
                        metadata['reads'].append(int(row[0]))
                
                elif current_section == 'settings':
                    if len(row) >= 2:
                        metadata['settings'][row[0]] = row[1]
                
                elif current_section == 'data':
                    # First row is the header
                    if 'data_header' not in metadata:
                        metadata['data_header'] = row
                        continue
                    
                    # Create a dictionary for the sample
                    if len(row) == len(metadata['data_header']):
                        sample = {}
                        for i, header in enumerate(metadata['data_header']):
                            sample[header] = row[i]
                        metadata['data'].append(sample)
        
        return metadata
    
    def _parse_v2(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a v2 SampleSheet file.
        
        Args:
            file_path: Path to the SampleSheet file
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            'version': 2,
            'header': {},
            'reads': {},
            'bclconvert_settings': {},
            'bclconvert_data': []
        }
        
        current_section = None
        
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            
            for row in reader:
                if not row:
                    continue
                
                # Check for section headers
                if row[0].startswith('[') and row[0].endswith(']'):
                    current_section = row[0][1:-1].lower()
                    continue
                
                # Process sections
                if current_section == 'header':
                    if len(row) >= 2:
                        metadata['header'][row[0]] = row[1]
                
                elif current_section == 'reads':
                    if len(row) >= 2:
                        metadata['reads'][row[0]] = row[1]
                
                elif current_section == 'bclconvert_settings':
                    if len(row) >= 2:
                        metadata['bclconvert_settings'][row[0]] = row[1]
                
                elif current_section == 'bclconvert_data':
                    # First row is the header
                    if 'bclconvert_data_header' not in metadata:
                        metadata['bclconvert_data_header'] = row
                        continue
                    
                    # Create a dictionary for the sample
                    if len(row) == len(metadata['bclconvert_data_header']):
                        sample = {}
                        for i, header in enumerate(metadata['bclconvert_data_header']):
                            sample[header] = row[i]
                        metadata['bclconvert_data'].append(sample)
        
        return metadata
    
    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate the extracted metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        # Check for version
        if 'version' not in metadata:
            return False
        
        # Validate based on version
        if metadata['version'] == 1:
            return self._validate_v1(metadata)
        elif metadata['version'] == 2:
            return self._validate_v2(metadata)
        
        return False
    
    def _validate_v1(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate v1 SampleSheet metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        # Check for required sections
        required_sections = ['header', 'reads', 'settings', 'data']
        for section in required_sections:
            if section not in metadata:
                return False
        
        # Check for data header
        if 'data_header' not in metadata:
            return False
        
        # Check for samples
        if not metadata['data']:
            return False
        
        return True
    
    def _validate_v2(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate v2 SampleSheet metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        # Check for required sections
        required_sections = ['header', 'reads', 'bclconvert_settings', 'bclconvert_data']
        for section in required_sections:
            if section not in metadata:
                return False
        
        # Check for data header
        if 'bclconvert_data_header' not in metadata:
            return False
        
        # Check for samples
        if not metadata['bclconvert_data']:
            return False
        
        return True
    
    def get_samples(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Get the list of samples from the metadata.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            List of sample dictionaries
        """
        if metadata['version'] == 1:
            return metadata['data']
        elif metadata['version'] == 2:
            return metadata['bclconvert_data']
        
        return []
    
    def get_projects(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Get the list of projects from the metadata.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            List of project names
        """
        projects = set()
        
        if metadata['version'] == 1:
            for sample in metadata['data']:
                if 'Sample_Project' in sample and sample['Sample_Project']:
                    projects.add(sample['Sample_Project'])
        elif metadata['version'] == 2:
            for sample in metadata['bclconvert_data']:
                if 'Sample_Project' in sample and sample['Sample_Project']:
                    projects.add(sample['Sample_Project'])
        
        return list(projects)
