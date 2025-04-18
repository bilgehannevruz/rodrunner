"""
iRODS metadata operations.
"""
from typing import Dict, List, Optional, Union, Any, Tuple, Generator

from irods.meta import iRODSMeta
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta
from irods.column import Criterion
from irods.session import iRODSSession

from rodrunner.irods.client import iRODSClient


class MetadataOperations:
    """Class for iRODS metadata operations."""
    
    def __init__(self, client: iRODSClient):
        """
        Initialize the metadata operations.
        
        Args:
            client: iRODS client
        """
        self.client = client
    
    def add_metadata(self, path: str, metadata: Dict[str, str], 
                    object_type: str = 'data') -> None:
        """
        Add metadata to an iRODS object.
        
        Args:
            path: Path to iRODS object
            metadata: Dictionary of metadata to add
            object_type: Type of object ('data' or 'collection')
        """
        with self.client.session() as session:
            if object_type == 'data':
                obj = session.data_objects.get(path)
            else:
                obj = session.collections.get(path)
                
            for key, value in metadata.items():
                obj.metadata.add(key, str(value))
    
    def update_metadata(self, path: str, metadata: Dict[str, str], 
                       object_type: str = 'data') -> None:
        """
        Update metadata on an iRODS object (remove and add).
        
        Args:
            path: Path to iRODS object
            metadata: Dictionary of metadata to update
            object_type: Type of object ('data' or 'collection')
        """
        with self.client.session() as session:
            if object_type == 'data':
                obj = session.data_objects.get(path)
            else:
                obj = session.collections.get(path)
                
            for key, value in metadata.items():
                # Remove existing metadata with this key
                for meta in list(obj.metadata.items()):
                    if meta.name == key:
                        obj.metadata.remove(meta)
                
                # Add new metadata
                obj.metadata.add(key, str(value))
    
    def remove_metadata(self, path: str, keys: List[str], 
                       object_type: str = 'data') -> None:
        """
        Remove metadata from an iRODS object.
        
        Args:
            path: Path to iRODS object
            keys: List of metadata keys to remove
            object_type: Type of object ('data' or 'collection')
        """
        with self.client.session() as session:
            if object_type == 'data':
                obj = session.data_objects.get(path)
            else:
                obj = session.collections.get(path)
                
            for key in keys:
                for meta in list(obj.metadata.items()):
                    if meta.name == key:
                        obj.metadata.remove(meta)
    
    def get_metadata(self, path: str, object_type: str = 'data') -> Dict[str, str]:
        """
        Get metadata from an iRODS object.
        
        Args:
            path: Path to iRODS object
            object_type: Type of object ('data' or 'collection')
            
        Returns:
            Dictionary of metadata
        """
        with self.client.session() as session:
            if object_type == 'data':
                obj = session.data_objects.get(path)
            else:
                obj = session.collections.get(path)
                
            return {meta.name: meta.value for meta in obj.metadata.items()}
    
    def search_by_metadata(self, metadata: Dict[str, str], 
                          object_type: str = 'data') -> List[str]:
        """
        Search for iRODS objects by metadata.
        
        Args:
            metadata: Dictionary of metadata to search for
            object_type: Type of object ('data' or 'collection')
            
        Returns:
            List of paths to matching objects
        """
        with self.client.session() as session:
            if object_type == 'data':
                query = session.query(DataObject.name, Collection.name)
                
                # Add metadata conditions
                for i, (key, value) in enumerate(metadata.items()):
                    alias = f"meta{i}"
                    query = query.filter(
                        Criterion('=', DataObjectMeta.name, key, alias),
                        Criterion('=', DataObjectMeta.value, value, alias)
                    )
                
                # Execute query and format results
                results = []
                for row in query:
                    path = f"{row[Collection.name]}/{row[DataObject.name]}"
                    results.append(path)
                
                return results
            else:
                query = session.query(Collection.name)
                
                # Add metadata conditions
                for i, (key, value) in enumerate(metadata.items()):
                    alias = f"meta{i}"
                    query = query.filter(
                        Criterion('=', CollectionMeta.name, key, alias),
                        Criterion('=', CollectionMeta.value, value, alias)
                    )
                
                # Execute query and format results
                results = []
                for row in query:
                    path = row[Collection.name]
                    results.append(path)
                
                return results
