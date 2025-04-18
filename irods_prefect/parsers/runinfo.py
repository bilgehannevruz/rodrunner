"""
Parser for RunInfo.xml files.
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

from irods_prefect.parsers.base import BaseParser


class RunInfoParser(BaseParser):
    """Parser for RunInfo.xml files."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a RunInfo.xml file and extract metadata.
        
        Args:
            file_path: Path to the RunInfo.xml file
            
        Returns:
            Dictionary of extracted metadata
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract run information
        run_node = root.find('Run')
        if run_node is None:
            return {}
        
        run_id = run_node.get('Id', '')
        run_number = run_node.get('Number', '')
        
        # Extract flowcell information
        flowcell = run_node.findtext('Flowcell', '')
        instrument = run_node.findtext('Instrument', '')
        date = run_node.findtext('Date', '')
        
        # Extract reads information
        reads_node = run_node.find('Reads')
        reads = []
        
        if reads_node is not None:
            for read_node in reads_node.findall('Read'):
                read = {
                    'number': read_node.get('Number', ''),
                    'num_cycles': read_node.get('NumCycles', ''),
                    'is_indexed_read': read_node.get('IsIndexedRead', '')
                }
                reads.append(read)
        
        # Extract flowcell layout
        flowcell_layout_node = run_node.find('FlowcellLayout')
        flowcell_layout = {}
        
        if flowcell_layout_node is not None:
            flowcell_layout = {
                'lane_count': flowcell_layout_node.get('LaneCount', ''),
                'surface_count': flowcell_layout_node.get('SurfaceCount', ''),
                'swath_count': flowcell_layout_node.get('SwathCount', ''),
                'tile_count': flowcell_layout_node.get('TileCount', '')
            }
        
        # Compile metadata
        metadata = {
            'run_id': run_id,
            'run_number': run_number,
            'flowcell': flowcell,
            'instrument': instrument,
            'date': date,
            'reads': reads,
            'flowcell_layout': flowcell_layout
        }
        
        return metadata
    
    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate the extracted metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        # Check for required fields
        required_fields = ['run_id', 'flowcell', 'instrument']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                return False
        
        # Check for reads
        if 'reads' not in metadata or not isinstance(metadata['reads'], list):
            return False
        
        # Check for flowcell layout
        if 'flowcell_layout' not in metadata or not isinstance(metadata['flowcell_layout'], dict):
            return False
        
        return True
    
    def get_sequencer_type(self, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Determine the sequencer type from the metadata.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            Sequencer type, or None if it cannot be determined
        """
        instrument = metadata.get('instrument', '')
        
        if not instrument:
            return None
        
        # Determine sequencer type based on instrument ID prefix
        if instrument.startswith('M'):
            return 'miseq'
        elif instrument.startswith('NS'):
            return 'nextseq'
        elif instrument.startswith('NDX'):
            return 'nextseq2k'
        elif instrument.startswith('A'):
            return 'novaseq'
        elif instrument.startswith('LH'):
            return 'novaseqxplus'
        elif instrument.startswith('MN'):
            return 'miniseq'
        elif instrument.startswith('D'):
            return 'hiseq'
        elif instrument.startswith('FSQ'):
            return 'iseq'
        
        return None
