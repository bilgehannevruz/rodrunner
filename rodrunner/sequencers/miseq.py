"""
MiSeq sequencer workflow.
"""
from typing import Dict, List, Optional, Union, Any
import os

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context

from rodrunner.models.config import AppConfig
from rodrunner.sequencers.base import BaseSequencerWorkflow


class MiSeqWorkflow(BaseSequencerWorkflow):
    """MiSeq sequencer workflow."""
    
    def get_sequencer_type(self) -> str:
        """
        Get the sequencer type.
        
        Returns:
            Sequencer type
        """
        return 'miseq'
    
    def get_irods_destination(self, run_id: str, metadata: Dict[str, Any]) -> str:
        """
        Get the iRODS destination path for a MiSeq run.
        
        Args:
            run_id: Run ID
            metadata: Run metadata
            
        Returns:
            iRODS destination path
        """
        # Extract components from run ID
        # Format: YYMMDD_M00001_0001_000000000-A1B2C
        parts = run_id.split('_')
        date = parts[0] if len(parts) > 0 else ''
        instrument = parts[1] if len(parts) > 1 else ''
        run_number = parts[2] if len(parts) > 2 else ''
        flowcell = parts[3] if len(parts) > 3 else ''
        
        # Get projects
        projects = metadata.get('projects', [])
        project_str = '_'.join(projects) if projects else 'NoProject'
        
        # Construct path
        path = f"/sequencing/miseq/{date}_{instrument}_{run_number}_{flowcell}"
        
        return path
    
    @flow(name="Process MiSeq Run")
    def process_run(self, run_dir: str) -> Dict[str, Any]:
        """
        Process a MiSeq run.
        
        Args:
            run_dir: Path to the MiSeq run directory
            
        Returns:
            Dictionary with the result of the processing
        """
        logger = get_run_logger()
        
        # Ingest the run
        logger.info(f"Ingesting MiSeq run: {run_dir}")
        ingest_result = self.ingest_run(run_dir)
        
        # Additional MiSeq-specific processing could be added here
        
        return ingest_result
