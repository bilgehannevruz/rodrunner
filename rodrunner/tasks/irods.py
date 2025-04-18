"""
Common iRODS tasks for Prefect workflows.
"""
from typing import Dict, List, Optional, Union, Any

from prefect import task

from rodrunner.irods.client import iRODSClient
from rodrunner.irods.metadata import MetadataOperations
from rodrunner.irods.query import QueryOperations
from rodrunner.models.config import iRODSConfig


@task(name="create_irods_client")
def create_irods_client(config: iRODSConfig) -> iRODSClient:
    """
    Create an iRODS client.
    
    Args:
        config: iRODS configuration
        
    Returns:
        iRODS client
    """
    return iRODSClient(config)


@task(name="upload_file_to_irods")
def upload_file_to_irods(
    client: iRODSClient,
    local_path: str,
    irods_path: str,
    metadata: Optional[Dict[str, str]] = None,
    force: bool = False,
    resource: Optional[str] = None
) -> str:
    """
    Upload a file to iRODS.
    
    Args:
        client: iRODS client
        local_path: Path to local file
        irods_path: Destination path in iRODS
        metadata: Optional metadata to attach to the data object
        force: Whether to overwrite existing data object
        resource: Resource to use for upload
        
    Returns:
        Path to the uploaded data object
    """
    obj = client.upload_file(
        local_path=local_path,
        irods_path=irods_path,
        metadata=metadata,
        force=force,
        resource=resource
    )
    
    return obj.path


@task(name="upload_directory_to_irods")
def upload_directory_to_irods(
    client: iRODSClient,
    local_path: str,
    irods_path: str,
    metadata: Optional[Dict[str, str]] = None,
    file_metadata: Optional[Dict[str, str]] = None,
    force: bool = False,
    resource: Optional[str] = None
) -> str:
    """
    Upload a directory to iRODS.
    
    Args:
        client: iRODS client
        local_path: Path to local directory
        irods_path: Destination path in iRODS
        metadata: Optional metadata to attach to the collection
        file_metadata: Optional metadata to attach to each data object
        force: Whether to overwrite existing data objects
        resource: Resource to use for upload
        
    Returns:
        Path to the uploaded collection
    """
    coll = client.upload_directory(
        local_path=local_path,
        irods_path=irods_path,
        metadata=metadata,
        file_metadata=file_metadata,
        force=force,
        resource=resource
    )
    
    return coll.path


@task(name="add_metadata_to_irods_object")
def add_metadata_to_irods_object(
    client: iRODSClient,
    path: str,
    metadata: Dict[str, str],
    object_type: str = 'data'
) -> None:
    """
    Add metadata to an iRODS object.
    
    Args:
        client: iRODS client
        path: Path to iRODS object
        metadata: Dictionary of metadata to add
        object_type: Type of object ('data' or 'collection')
    """
    metadata_ops = MetadataOperations(client)
    metadata_ops.add_metadata(path, metadata, object_type)


@task(name="update_metadata_on_irods_object")
def update_metadata_on_irods_object(
    client: iRODSClient,
    path: str,
    metadata: Dict[str, str],
    object_type: str = 'data'
) -> None:
    """
    Update metadata on an iRODS object.
    
    Args:
        client: iRODS client
        path: Path to iRODS object
        metadata: Dictionary of metadata to update
        object_type: Type of object ('data' or 'collection')
    """
    metadata_ops = MetadataOperations(client)
    metadata_ops.update_metadata(path, metadata, object_type)


@task(name="search_irods_by_metadata")
def search_irods_by_metadata(
    client: iRODSClient,
    metadata: Dict[str, str],
    object_type: str = 'data'
) -> List[str]:
    """
    Search for iRODS objects by metadata.
    
    Args:
        client: iRODS client
        metadata: Dictionary of metadata to search for
        object_type: Type of object ('data' or 'collection')
        
    Returns:
        List of paths to matching objects
    """
    metadata_ops = MetadataOperations(client)
    return metadata_ops.search_by_metadata(metadata, object_type)


@task(name="query_data_objects_by_metadata")
def query_data_objects_by_metadata(
    client: iRODSClient,
    metadata_items: List[tuple],
    operator: str = "AND",
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> List[Any]:
    """
    Query data objects by metadata.
    
    Args:
        client: iRODS client
        metadata_items: List of (name, value, units) tuples
        operator: Logical operator to use between items ("AND" or "OR")
        limit: Maximum number of results to return
        offset: Number of results to skip
        sort_by: Field to sort results by
        sort_order: Sort order ("asc" or "desc")
        
    Returns:
        List of data objects matching the query
    """
    query_ops = QueryOperations(client)
    return query_ops.query_data_objects_by_metadata(
        metadata_items=metadata_items,
        operator=operator,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )


@task(name="query_collections_by_metadata")
def query_collections_by_metadata(
    client: iRODSClient,
    metadata_items: List[tuple],
    operator: str = "AND",
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> List[Any]:
    """
    Query collections by metadata.
    
    Args:
        client: iRODS client
        metadata_items: List of (name, value, units) tuples
        operator: Logical operator to use between items ("AND" or "OR")
        limit: Maximum number of results to return
        offset: Number of results to skip
        sort_by: Field to sort results by
        sort_order: Sort order ("asc" or "desc")
        
    Returns:
        List of collections matching the query
    """
    query_ops = QueryOperations(client)
    return query_ops.query_collections_by_metadata(
        metadata_items=metadata_items,
        operator=operator,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
