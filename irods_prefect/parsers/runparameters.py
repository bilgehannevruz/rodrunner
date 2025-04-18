"""
Parser for RunParameters.xml files.
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

from irods_prefect.parsers.base import BaseParser


class RunParametersParser(BaseParser):
    """Parser for RunParameters.xml files."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a RunParameters.xml file and extract metadata.
        
        Args:
            file_path: Path to the RunParameters.xml file
            
        Returns:
            Dictionary of extracted metadata
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract common parameters
        metadata = {}
        
        # Extract instrument type
        instrument_type = root.findtext('InstrumentType', '')
        metadata['instrument_type'] = instrument_type
        
        # Extract run ID
        run_id = root.findtext('RunId', '')
        metadata['run_id'] = run_id
        
        # Extract experiment name
        experiment_name = root.findtext('ExperimentName', '')
        metadata['experiment_name'] = experiment_name
        
        # Extract sequencing kit number
        sequencing_kit_number = root.findtext('SequencingKitNumber', '')
        metadata['sequencing_kit_number'] = sequencing_kit_number
        
        # Extract read cycle information
        read1_cycles = root.findtext('Read1NumberOfCycles', '')
        read2_cycles = root.findtext('Read2NumberOfCycles', '')
        index1_cycles = root.findtext('IndexRead1NumberOfCycles', '')
        index2_cycles = root.findtext('IndexRead2NumberOfCycles', '')
        
        metadata['read1_cycles'] = read1_cycles
        metadata['read2_cycles'] = read2_cycles
        metadata['index1_cycles'] = index1_cycles
        metadata['index2_cycles'] = index2_cycles
        
        # Extract platform-specific parameters
        if instrument_type.lower() == 'novaseqxplus':
            self._parse_novaseqxplus_parameters(root, metadata)
        elif instrument_type.lower() == 'novaseq':
            self._parse_novaseq_parameters(root, metadata)
        elif instrument_type.lower() == 'nextseq':
            self._parse_nextseq_parameters(root, metadata)
        elif instrument_type.lower() == 'miseq':
            self._parse_miseq_parameters(root, metadata)
        elif instrument_type.lower() == 'iseq':
            self._parse_iseq_parameters(root, metadata)
        
        return metadata
    
    def _parse_novaseqxplus_parameters(self, root: ET.Element, metadata: Dict[str, Any]) -> None:
        """
        Parse NovaSeq X Plus specific parameters.
        
        Args:
            root: XML root element
            metadata: Dictionary to update with extracted metadata
        """
        # Extract NovaSeq X Plus specific parameters
        pass
    
    def _parse_novaseq_parameters(self, root: ET.Element, metadata: Dict[str, Any]) -> None:
        """
        Parse NovaSeq specific parameters.
        
        Args:
            root: XML root element
            metadata: Dictionary to update with extracted metadata
        """
        # Extract NovaSeq specific parameters
        workflow_type = root.findtext('WorkflowType', '')
        metadata['workflow_type'] = workflow_type
        
        # Extract chemistry version
        chemistry_version = root.findtext('ChemistryVersion', '')
        metadata['chemistry_version'] = chemistry_version
    
    def _parse_nextseq_parameters(self, root: ET.Element, metadata: Dict[str, Any]) -> None:
        """
        Parse NextSeq specific parameters.
        
        Args:
            root: XML root element
            metadata: Dictionary to update with extracted metadata
        """
        # Extract NextSeq specific parameters
        chemistry_version = root.findtext('ChemistryVersion', '')
        metadata['chemistry_version'] = chemistry_version
    
    def _parse_miseq_parameters(self, root: ET.Element, metadata: Dict[str, Any]) -> None:
        """
        Parse MiSeq specific parameters.
        
        Args:
            root: XML root element
            metadata: Dictionary to update with extracted metadata
        """
        # Extract MiSeq specific parameters
        chemistry = root.findtext('Chemistry', '')
        metadata['chemistry'] = chemistry
    
    def _parse_iseq_parameters(self, root: ET.Element, metadata: Dict[str, Any]) -> None:
        """
        Parse iSeq specific parameters.
        
        Args:
            root: XML root element
            metadata: Dictionary to update with extracted metadata
        """
        # Extract iSeq specific parameters
        pass
    
    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate the extracted metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        # Check for required fields
        required_fields = ['instrument_type', 'run_id']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                return False
        
        # Check for read cycle information
        cycle_fields = ['read1_cycles', 'read2_cycles', 'index1_cycles', 'index2_cycles']
        for field in cycle_fields:
            if field not in metadata:
                return False
        
        return True
