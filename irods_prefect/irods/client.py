"""
Base iRODS client wrapper providing session management and common operations.
"""
import os
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional, Union, Any, Tuple

from irods.session import iRODSSession
from irods.meta import iRODSMeta
from irods.models import Collection, DataObject
from irods.collection import iRODSCollection
from irods.data_object import iRODSDataObject
from irods.exception import CAT_NO_ROWS_FOUND, CollectionDoesNotExist, DataObjectDoesNotExist

from irods_prefect.models.config import iRODSConfig


class iRODSClient:
    """Base iRODS client wrapper providing session management and common operations."""
    
    def __init__(self, config: iRODSConfig):
        """
        Initialize the iRODS client.
        
        Args:
            config: iRODS configuration
        """
        self.config = config
    
    @contextmanager
    def session(self) -> Generator[iRODSSession, None, None]:
        """
        Create and yield an iRODS session.
        
        Yields:
            iRODS session
        """
        with iRODSSession(host=self.config.host,
                         port=self.config.port,
                         user=self.config.user,
                         password=self.config.password,
                         zone=self.config.zone) as session:
            yield session
    
    def collection_exists(self, path: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            path: Path to the collection
            
        Returns:
            True if the collection exists, False otherwise
        """
        with self.session() as session:
            try:
                session.collections.get(path)
                return True
            except CollectionDoesNotExist:
                return False
    
    def data_object_exists(self, path: str) -> bool:
        """
        Check if a data object exists.
        
        Args:
            path: Path to the data object
            
        Returns:
            True if the data object exists, False otherwise
        """
        with self.session() as session:
            try:
                session.data_objects.get(path)
                return True
            except DataObjectDoesNotExist:
                return False
    
    def create_collection(self, path: str, create_parents: bool = True) -> iRODSCollection:
        """
        Create a collection and optionally its parent collections.
        
        Args:
            path: Path to the collection
            create_parents: Whether to create parent collections if they don't exist
            
        Returns:
            iRODS collection
        """
        with self.session() as session:
            if create_parents:
                # Split path into components
                components = path.strip('/').split('/')
                current_path = '/'
                
                # Create each component if it doesn't exist
                for component in components:
                    if not component:
                        continue
                    current_path = os.path.join(current_path, component)
                    try:
                        coll = session.collections.get(current_path)
                    except CollectionDoesNotExist:
                        coll = session.collections.create(current_path)
                return coll
            else:
                return session.collections.create(path)
    
    def upload_file(self, local_path: str, irods_path: str, metadata: Dict = None, 
                   force: bool = False, resource: str = None) -> iRODSDataObject:
        """
        Upload a file to iRODS with optional metadata.
        
        Args:
            local_path: Path to local file
            irods_path: Destination path in iRODS
            metadata: Optional metadata to attach to the data object
            force: Whether to overwrite existing data object
            resource: Resource to use for upload
            
        Returns:
            iRODS data object
        """
        with self.session() as session:
            # Check if data object exists
            if not force and self.data_object_exists(irods_path):
                raise FileExistsError(f"Data object already exists: {irods_path}")
            
            # Create parent collection if needed
            parent_coll = os.path.dirname(irods_path)
            if not self.collection_exists(parent_coll):
                self.create_collection(parent_coll)
            
            # Upload file
            options = {}
            if resource:
                options['destRescName'] = resource
            elif self.config.default_resource:
                options['destRescName'] = self.config.default_resource
                
            obj = session.data_objects.put(local_path, irods_path, **options)
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    obj.metadata.add(key, str(value))
            
            return obj
    
    def upload_directory(self, local_path: str, irods_path: str, metadata: Dict = None,
                        file_metadata: Dict = None, force: bool = False, 
                        resource: str = None) -> iRODSCollection:
        """
        Upload a directory to iRODS with optional metadata.
        
        Args:
            local_path: Path to local directory
            irods_path: Destination path in iRODS
            metadata: Optional metadata to attach to the collection
            file_metadata: Optional metadata to attach to each data object
            force: Whether to overwrite existing data objects
            resource: Resource to use for upload
            
        Returns:
            iRODS collection
        """
        with self.session() as session:
            # Create collection if it doesn't exist
            if not self.collection_exists(irods_path):
                coll = self.create_collection(irods_path)
            else:
                coll = session.collections.get(irods_path)
            
            # Add metadata to collection
            if metadata:
                for key, value in metadata.items():
                    coll.metadata.add(key, str(value))
            
            # Walk through local directory and upload files
            for root, dirs, files in os.walk(local_path):
                # Calculate relative path
                rel_path = os.path.relpath(root, local_path)
                if rel_path == '.':
                    rel_path = ''
                
                # Create subcollection if needed
                if rel_path:
                    subcoll_path = os.path.join(irods_path, rel_path)
                    if not self.collection_exists(subcoll_path):
                        subcoll = self.create_collection(subcoll_path)
                    else:
                        subcoll = session.collections.get(subcoll_path)
                else:
                    subcoll_path = irods_path
                
                # Upload files
                for file in files:
                    local_file_path = os.path.join(root, file)
                    irods_file_path = os.path.join(subcoll_path, file)
                    
                    try:
                        self.upload_file(
                            local_file_path, 
                            irods_file_path, 
                            metadata=file_metadata,
                            force=force,
                            resource=resource
                        )
                    except Exception as e:
                        # Log error but continue with other files
                        print(f"Error uploading {local_file_path}: {str(e)}")
            
            return coll
    
    def get_data_object(self, path: str) -> iRODSDataObject:
        """
        Get a data object.
        
        Args:
            path: Path to the data object
            
        Returns:
            iRODS data object
        """
        with self.session() as session:
            return session.data_objects.get(path)
    
    def get_collection(self, path: str) -> iRODSCollection:
        """
        Get a collection.
        
        Args:
            path: Path to the collection
            
        Returns:
            iRODS collection
        """
        with self.session() as session:
            return session.collections.get(path)
    
    def download_file(self, irods_path: str, local_path: str, force: bool = False) -> str:
        """
        Download a file from iRODS.
        
        Args:
            irods_path: Path to the data object in iRODS
            local_path: Destination path on the local filesystem
            force: Whether to overwrite existing local file
            
        Returns:
            Path to the downloaded file
        """
        with self.session() as session:
            # Check if local file exists
            if not force and os.path.exists(local_path):
                raise FileExistsError(f"Local file already exists: {local_path}")
            
            # Create parent directory if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            session.data_objects.get(irods_path, local_path)
            
            return local_path
    
    def remove_data_object(self, path: str, force: bool = False) -> None:
        """
        Remove a data object.
        
        Args:
            path: Path to the data object
            force: Whether to force removal
        """
        with self.session() as session:
            session.data_objects.unlink(path, force=force)
    
    def remove_collection(self, path: str, recursive: bool = True, force: bool = False) -> None:
        """
        Remove a collection.
        
        Args:
            path: Path to the collection
            recursive: Whether to remove recursively
            force: Whether to force removal
        """
        with self.session() as session:
            session.collections.remove(path, recursive=recursive, force=force)
