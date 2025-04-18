"""
NovaSeq sequencer workflow.
"""
from typing import Dict, List, Optional, Union, Any
import os

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context

from irods_prefect.models.config import AppConfig
from irods_prefect.sequencers.base import BaseSequencerWorkflow


class NovaSeqWorkflow(BaseSequencerWorkflow):
    """NovaSeq sequencer workflow."""
    
    def get_sequencer_type(self) -> str:
        """
        Get the sequencer type.
        
        Returns:
            Sequencer type
        """
        return 'novaseq'
    
    def get_irods_destination(self, run_id: str, metadata: Dict[str, Any]) -> str:
        """
        Get the iRODS destination path for a NovaSeq run.
        
        Args:
            run_id: Run ID
            metadata: Run metadata
            
        Returns:
            iRODS destination path
        """
        # Extract components from run ID
        # Format: YYMMDD_A00001_0001_AHGV7DRXX
        parts = run_id.split('_')
        date = parts[0] if len(parts) > 0 else ''
        instrument = parts[1] if len(parts) > 1 else ''
        run_number = parts[2] if len(parts) > 2 else ''
        flowcell = parts[3] if len(parts) > 3 else ''
        
        # Get projects
        projects = metadata.get('projects', [])
        project_str = '_'.join(projects) if projects else 'NoProject'
        
        # Construct path
        path = f"/sequencing/novaseq/{date}_{instrument}_{run_number}_{flowcell}"
        
        return path
    
    @flow(name="Process NovaSeq Run")
    def process_run(self, run_dir: str) -> Dict[str, Any]:
        """
        Process a NovaSeq run.
        
        Args:
            run_dir: Path to the NovaSeq run directory
            
        Returns:
            Dictionary with the result of the processing
        """
        logger = get_run_logger()
        
        # Ingest the run
        logger.info(f"Ingesting NovaSeq run: {run_dir}")
        ingest_result = self.ingest_run(run_dir)
        
        # Additional NovaSeq-specific processing could be added here
        
        return ingest_result
