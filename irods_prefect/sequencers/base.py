"""
Base class for sequencer workflows.
"""
from typing import Dict, List, Optional, Union, Any
import os
from abc import ABC, abstractmethod

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context

from irods_prefect.irods.client import iRODSClient
from irods_prefect.models.config import AppConfig
from irods_prefect.parsers.factory import ParserFactory
from irods_prefect.tasks.irods import (
    create_irods_client, upload_directory_to_irods, add_metadata_to_irods_object,
    update_metadata_on_irods_object
)
from irods_prefect.tasks.parsing import (
    parse_run_info, parse_run_parameters, parse_sample_sheet,
    get_sequencer_type, get_projects_from_sample_sheet, parse_sequencer_run
)
from irods_prefect.tasks.notifications import (
    send_workflow_success_notification, send_workflow_failure_notification
)


class BaseSequencerWorkflow(ABC):
    """Base class for sequencer workflows."""
    
    def __init__(self, config: AppConfig):
        """
        Initialize the workflow.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.sequencer_type = self.get_sequencer_type()
    
    @abstractmethod
    def get_sequencer_type(self) -> str:
        """
        Get the sequencer type.
        
        Returns:
            Sequencer type
        """
        pass
    
    @abstractmethod
    def get_irods_destination(self, run_id: str, metadata: Dict[str, Any]) -> str:
        """
        Get the iRODS destination path for a sequencer run.
        
        Args:
            run_id: Run ID
            metadata: Run metadata
            
        Returns:
            iRODS destination path
        """
        pass
    
    @flow(name="Ingest Sequencer Run")
    def ingest_run(self, run_dir: str) -> Dict[str, Any]:
        """
        Ingest a sequencer run.
        
        Args:
            run_dir: Path to the sequencer run directory
            
        Returns:
            Dictionary with the result of the ingestion
        """
        logger = get_run_logger()
        run_context = get_run_context()
        
        try:
            # Parse metadata
            logger.info(f"Parsing metadata from {run_dir}")
            metadata = parse_sequencer_run(run_dir)
            
            # Get run ID
            run_id = metadata.get('run_info', {}).get('run_id', '')
            if not run_id:
                raise ValueError(f"Failed to get run ID from metadata: {metadata}")
            
            # Get iRODS destination
            irods_destination = self.get_irods_destination(run_id, metadata)
            
            # Create iRODS client
            client = create_irods_client(self.config.irods)
            
            # Upload to iRODS
            logger.info(f"Uploading {run_dir} to {irods_destination}")
            collection_path = upload_directory_to_irods(
                client=client,
                local_path=run_dir,
                irods_path=irods_destination,
                metadata={
                    'sequencer_type': self.sequencer_type,
                    'run_id': run_id,
                    'status': 'ingested'
                }
            )
            
            # Add additional metadata
            logger.info(f"Adding metadata to {collection_path}")
            add_metadata_to_irods_object(
                client=client,
                path=collection_path,
                metadata={
                    'flowcell': metadata.get('run_info', {}).get('flowcell', ''),
                    'instrument': metadata.get('run_info', {}).get('instrument', ''),
                    'date': metadata.get('run_info', {}).get('date', '')
                },
                object_type='collection'
            )
            
            # Add project metadata
            projects = metadata.get('projects', [])
            if projects:
                add_metadata_to_irods_object(
                    client=client,
                    path=collection_path,
                    metadata={'projects': ','.join(projects)},
                    object_type='collection'
                )
            
            # Send success notification
            send_workflow_success_notification(
                config=self.config.notification,
                workflow_name=f"Ingest {self.sequencer_type.capitalize()} Run",
                run_id=run_context.flow_run.id,
                details={
                    'run_id': run_id,
                    'run_dir': run_dir,
                    'irods_destination': irods_destination
                }
            )
            
            return {
                'success': True,
                'run_id': run_id,
                'collection_path': collection_path,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Error ingesting run: {str(e)}")
            
            # Send failure notification
            send_workflow_failure_notification(
                config=self.config.notification,
                workflow_name=f"Ingest {self.sequencer_type.capitalize()} Run",
                run_id=run_context.flow_run.id,
                error=str(e),
                details={
                    'run_dir': run_dir
                }
            )
            
            raise
    
    @flow(name="Update Sequencer Run Metadata")
    def update_metadata(self, collection_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update metadata for a sequencer run.
        
        Args:
            collection_path: Path to the iRODS collection
            metadata: Metadata to update
            
        Returns:
            Dictionary with the result of the update
        """
        logger = get_run_logger()
        run_context = get_run_context()
        
        try:
            # Create iRODS client
            client = create_irods_client(self.config.irods)
            
            # Update metadata
            logger.info(f"Updating metadata for {collection_path}")
            update_metadata_on_irods_object(
                client=client,
                path=collection_path,
                metadata=metadata,
                object_type='collection'
            )
            
            # Send success notification
            send_workflow_success_notification(
                config=self.config.notification,
                workflow_name=f"Update {self.sequencer_type.capitalize()} Run Metadata",
                run_id=run_context.flow_run.id,
                details={
                    'collection_path': collection_path,
                    'metadata': metadata
                }
            )
            
            return {
                'success': True,
                'collection_path': collection_path,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            
            # Send failure notification
            send_workflow_failure_notification(
                config=self.config.notification,
                workflow_name=f"Update {self.sequencer_type.capitalize()} Run Metadata",
                run_id=run_context.flow_run.id,
                error=str(e),
                details={
                    'collection_path': collection_path
                }
            )
            
            raise
