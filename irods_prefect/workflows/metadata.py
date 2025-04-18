"""
Metadata enhancement workflows.
"""
from typing import Dict, List, Optional, Union, Any
import os

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context

from irods_prefect.models.config import AppConfig
from irods_prefect.irods.client import iRODSClient
from irods_prefect.irods.query import QueryOperations
from irods_prefect.tasks.irods import (
    create_irods_client, update_metadata_on_irods_object,
    query_collections_by_metadata
)


@flow(name="Update Run Status")
def update_run_status(
    config: AppConfig,
    collection_path: str,
    status: str
) -> Dict[str, Any]:
    """
    Update the status of a sequencer run.
    
    Args:
        config: Application configuration
        collection_path: Path to the iRODS collection
        status: New status
        
    Returns:
        Dictionary with the result of the update
    """
    logger = get_run_logger()
    
    # Create iRODS client
    client = create_irods_client(config.irods)
    
    # Update status
    logger.info(f"Updating status of {collection_path} to {status}")
    update_metadata_on_irods_object(
        client=client,
        path=collection_path,
        metadata={'status': status},
        object_type='collection'
    )
    
    return {
        'success': True,
        'collection_path': collection_path,
        'status': status
    }


@flow(name="Find Runs by Status")
def find_runs_by_status(
    config: AppConfig,
    status: str,
    sequencer_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find sequencer runs with a specific status.
    
    Args:
        config: Application configuration
        status: Status to search for
        sequencer_type: Optional sequencer type to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of collections matching the query
    """
    logger = get_run_logger()
    
    # Create iRODS client
    client = create_irods_client(config.irods)
    
    # Build metadata query
    metadata_items = [("status", status, None)]
    
    if sequencer_type:
        metadata_items.append(("sequencer_type", sequencer_type, None))
    
    # Query collections
    logger.info(f"Finding runs with status {status}")
    collections = query_collections_by_metadata(
        client=client,
        metadata_items=metadata_items,
        limit=limit,
        sort_by="modify_time",
        sort_order="desc"
    )
    
    # Convert to dictionaries
    results = []
    for coll in collections:
        metadata = {meta.name: meta.value for meta in coll.metadata.items()}
        
        results.append({
            'path': coll.path,
            'name': os.path.basename(coll.path),
            'create_time': str(coll.create_time),
            'modify_time': str(coll.modify_time),
            'metadata': metadata
        })
    
    return results


@flow(name="Process New Runs")
def process_new_runs(
    config: AppConfig,
    sequencer_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find and process new sequencer runs.
    
    Args:
        config: Application configuration
        sequencer_type: Optional sequencer type to filter by
        limit: Maximum number of results to return
        
    Returns:
        List of processing results
    """
    logger = get_run_logger()
    
    # Find new runs
    logger.info("Finding new runs")
    new_runs = find_runs_by_status(
        config=config,
        status="new",
        sequencer_type=sequencer_type,
        limit=limit
    )
    
    logger.info(f"Found {len(new_runs)} new runs")
    
    # Process each run
    results = []
    for run in new_runs:
        collection_path = run['path']
        
        try:
            # Update status to processing
            logger.info(f"Processing run: {collection_path}")
            update_run_status(
                config=config,
                collection_path=collection_path,
                status="processing"
            )
            
            # TODO: Add processing logic here
            
            # Update status to processed
            update_run_status(
                config=config,
                collection_path=collection_path,
                status="processed"
            )
            
            results.append({
                'success': True,
                'collection_path': collection_path
            })
        except Exception as e:
            logger.error(f"Error processing run {collection_path}: {str(e)}")
            
            # Update status to error
            try:
                update_run_status(
                    config=config,
                    collection_path=collection_path,
                    status="error"
                )
            except Exception as update_error:
                logger.error(f"Error updating status: {str(update_error)}")
            
            results.append({
                'success': False,
                'collection_path': collection_path,
                'error': str(e)
            })
    
    return results
