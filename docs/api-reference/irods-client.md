# iRODS Client API Reference

This page contains the API reference for the iRODS client module.

## `iRODSClient`

```python
class iRODSClient:
    """
    Client for interacting with iRODS.
    
    This class provides a simplified interface for common iRODS operations,
    including collection and data object management, metadata operations, and more.
    """
    
    def __init__(self, config: iRODSConfig):
        """
        Initialize the iRODS client.
        
        Args:
            config: iRODS configuration
        """
```

The `iRODSClient` class provides a simplified interface for common iRODS operations.

### Methods

#### `session`

```python
def session(self, retries: int = 0, retry_delay: float = 1.0) -> ContextManager[iRODSSession]:
    """
    Get an iRODS session as a context manager.
    
    Args:
        retries: Number of retries if connection fails
        retry_delay: Delay between retries in seconds
        
    Returns:
        Context manager for an iRODS session
    """
```

This method returns an iRODS session as a context manager.

##### Parameters

- `retries`: Number of retries if connection fails
- `retry_delay`: Delay between retries in seconds

##### Returns

Context manager for an iRODS session.

##### Example

```python
with irods_client.session() as session:
    # Use the session
    coll = session.collections.get("/tempZone/home/rods")
    print(f"Collection: {coll.path}")
```

#### `collection_exists`

```python
def collection_exists(self, path: str) -> bool:
    """
    Check if a collection exists.
    
    Args:
        path: Path to the collection
        
    Returns:
        True if the collection exists, False otherwise
    """
```

This method checks if a collection exists.

##### Parameters

- `path`: Path to the collection

##### Returns

True if the collection exists, False otherwise.

##### Example

```python
if irods_client.collection_exists("/tempZone/home/rods/test"):
    print("Collection exists")
```

#### `create_collection`

```python
def create_collection(self, path: str, create_parents: bool = True) -> iRODSCollection:
    """
    Create a collection.
    
    Args:
        path: Path to the collection
        create_parents: Whether to create parent collections if they don't exist
        
    Returns:
        The created collection
    """
```

This method creates a collection.

##### Parameters

- `path`: Path to the collection
- `create_parents`: Whether to create parent collections if they don't exist

##### Returns

The created collection.

##### Example

```python
coll = irods_client.create_collection("/tempZone/home/rods/test")
```

#### `get_collection`

```python
def get_collection(self, path: str) -> iRODSCollection:
    """
    Get a collection.
    
    Args:
        path: Path to the collection
        
    Returns:
        The collection
    """
```

This method gets a collection.

##### Parameters

- `path`: Path to the collection

##### Returns

The collection.

##### Example

```python
coll = irods_client.get_collection("/tempZone/home/rods/test")
```

#### `remove_collection`

```python
def remove_collection(self, path: str, recursive: bool = False, force: bool = False) -> None:
    """
    Remove a collection.
    
    Args:
        path: Path to the collection
        recursive: Whether to remove the collection recursively
        force: Whether to force removal
    """
```

This method removes a collection.

##### Parameters

- `path`: Path to the collection
- `recursive`: Whether to remove the collection recursively
- `force`: Whether to force removal

##### Example

```python
irods_client.remove_collection("/tempZone/home/rods/test", recursive=True)
```

#### `data_object_exists`

```python
def data_object_exists(self, path: str) -> bool:
    """
    Check if a data object exists.
    
    Args:
        path: Path to the data object
        
    Returns:
        True if the data object exists, False otherwise
    """
```

This method checks if a data object exists.

##### Parameters

- `path`: Path to the data object

##### Returns

True if the data object exists, False otherwise.

##### Example

```python
if irods_client.data_object_exists("/tempZone/home/rods/test.txt"):
    print("Data object exists")
```

#### `upload_file`

```python
def upload_file(
    self,
    local_path: str,
    irods_path: str,
    metadata: Dict[str, str] = None,
    force: bool = False,
    resource: str = None
) -> iRODSDataObject:
    """
    Upload a file to iRODS.
    
    Args:
        local_path: Path to the local file
        irods_path: Path to the iRODS data object
        metadata: Metadata to add to the data object
        force: Whether to overwrite existing data object
        resource: Resource to use for upload
        
    Returns:
        The uploaded data object
    """
```

This method uploads a file to iRODS.

##### Parameters

- `local_path`: Path to the local file
- `irods_path`: Path to the iRODS data object
- `metadata`: Metadata to add to the data object
- `force`: Whether to overwrite existing data object
- `resource`: Resource to use for upload

##### Returns

The uploaded data object.

##### Example

```python
obj = irods_client.upload_file(
    "/path/to/local/file.txt",
    "/tempZone/home/rods/file.txt",
    metadata={"key1": "value1", "key2": "value2"}
)
```

#### `get_data_object`

```python
def get_data_object(self, path: str) -> iRODSDataObject:
    """
    Get a data object.
    
    Args:
        path: Path to the data object
        
    Returns:
        The data object
    """
```

This method gets a data object.

##### Parameters

- `path`: Path to the data object

##### Returns

The data object.

##### Example

```python
obj = irods_client.get_data_object("/tempZone/home/rods/file.txt")
```

#### `download_file`

```python
def download_file(
    self,
    irods_path: str,
    local_path: str,
    force: bool = False
) -> str:
    """
    Download a file from iRODS.
    
    Args:
        irods_path: Path to the iRODS data object
        local_path: Path to the local file
        force: Whether to overwrite existing local file
        
    Returns:
        Path to the downloaded file
    """
```

This method downloads a file from iRODS.

##### Parameters

- `irods_path`: Path to the iRODS data object
- `local_path`: Path to the local file
- `force`: Whether to overwrite existing local file

##### Returns

Path to the downloaded file.

##### Example

```python
local_path = irods_client.download_file(
    "/tempZone/home/rods/file.txt",
    "/path/to/local/download.txt"
)
```

#### `remove_data_object`

```python
def remove_data_object(self, path: str, force: bool = False) -> None:
    """
    Remove a data object.
    
    Args:
        path: Path to the data object
        force: Whether to force removal
    """
```

This method removes a data object.

##### Parameters

- `path`: Path to the data object
- `force`: Whether to force removal

##### Example

```python
irods_client.remove_data_object("/tempZone/home/rods/file.txt")
```

#### `upload_directory`

```python
def upload_directory(
    self,
    local_dir: str,
    irods_path: str,
    metadata: Dict[str, str] = None,
    file_metadata: Dict[str, str] = None,
    force: bool = False,
    resource: str = None
) -> iRODSCollection:
    """
    Upload a directory to iRODS.
    
    Args:
        local_dir: Path to the local directory
        irods_path: Path to the iRODS collection
        metadata: Metadata to add to the collection
        file_metadata: Metadata to add to each file
        force: Whether to overwrite existing data objects
        resource: Resource to use for upload
        
    Returns:
        The uploaded collection
    """
```

This method uploads a directory to iRODS.

##### Parameters

- `local_dir`: Path to the local directory
- `irods_path`: Path to the iRODS collection
- `metadata`: Metadata to add to the collection
- `file_metadata`: Metadata to add to each file
- `force`: Whether to overwrite existing data objects
- `resource`: Resource to use for upload

##### Returns

The uploaded collection.

##### Example

```python
coll = irods_client.upload_directory(
    "/path/to/local/dir",
    "/tempZone/home/rods/dir",
    metadata={"collection_key": "collection_value"},
    file_metadata={"file_key": "file_value"}
)
```

## Notes

- The `iRODSClient` class provides a simplified interface for common iRODS operations.
- The `session` method returns an iRODS session as a context manager, which automatically closes the session when the context is exited.
- The `upload_file` and `upload_directory` methods can add metadata to the uploaded data objects and collections.
- The `download_file` method returns the path to the downloaded file, which can be used to access the file locally.
