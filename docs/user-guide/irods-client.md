# iRODS Client

The iRODS client module provides a comprehensive wrapper for the python-irodsclient library. It simplifies common iRODS operations, including collection and data object management, metadata operations, and more.

## Key Features

- **Session management** with context managers
- **Collection operations** for creating, checking, and removing collections
- **Data object operations** for uploading, downloading, and removing data objects
- **Metadata operations** for adding, updating, and querying metadata
- **Error handling** for common iRODS errors

## Basic Usage

### Creating an iRODS Client

```python
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient

# Load the configuration
config = get_config()

# Create an iRODS client
irods_client = iRODSClient(config.irods)
```

### Session Management

The iRODS client provides a context manager for managing iRODS sessions:

```python
# Using the session context manager
with irods_client.session() as session:
    # Use the session
    coll = session.collections.get("/tempZone/home/rods")
    print(f"Collection: {coll.path}")
```

### Collection Operations

```python
# Check if a collection exists
if irods_client.collection_exists("/tempZone/home/rods/test"):
    print("Collection exists")

# Create a collection
coll = irods_client.create_collection("/tempZone/home/rods/test")

# Create a collection with parent collections
coll = irods_client.create_collection("/tempZone/home/rods/test/nested/deep", create_parents=True)

# Get a collection
coll = irods_client.get_collection("/tempZone/home/rods/test")

# Remove a collection
irods_client.remove_collection("/tempZone/home/rods/test", recursive=True)
```

### Data Object Operations

```python
# Check if a data object exists
if irods_client.data_object_exists("/tempZone/home/rods/test.txt"):
    print("Data object exists")

# Upload a file
obj = irods_client.upload_file("/path/to/local/file.txt", "/tempZone/home/rods/file.txt")

# Upload a file with metadata
metadata = {
    "key1": "value1",
    "key2": "value2"
}
obj = irods_client.upload_file("/path/to/local/file.txt", "/tempZone/home/rods/file.txt", metadata=metadata)

# Get a data object
obj = irods_client.get_data_object("/tempZone/home/rods/file.txt")

# Download a file
local_path = irods_client.download_file("/tempZone/home/rods/file.txt", "/path/to/local/download.txt")

# Remove a data object
irods_client.remove_data_object("/tempZone/home/rods/file.txt")
```

### Directory Operations

```python
# Upload a directory
coll = irods_client.upload_directory("/path/to/local/dir", "/tempZone/home/rods/dir")

# Upload a directory with metadata
coll_metadata = {
    "collection_key": "collection_value"
}
file_metadata = {
    "file_key": "file_value"
}
coll = irods_client.upload_directory(
    "/path/to/local/dir",
    "/tempZone/home/rods/dir",
    metadata=coll_metadata,
    file_metadata=file_metadata
)
```

## Advanced Usage

### Working with Metadata

```python
# Get metadata from a collection
coll = irods_client.get_collection("/tempZone/home/rods/test")
for meta in coll.metadata.items():
    print(f"{meta.name}: {meta.value}")

# Get metadata from a data object
obj = irods_client.get_data_object("/tempZone/home/rods/file.txt")
for meta in obj.metadata.items():
    print(f"{meta.name}: {meta.value}")

# Add metadata to a collection
with irods_client.session() as session:
    coll = session.collections.get("/tempZone/home/rods/test")
    coll.metadata.add("key", "value")

# Add metadata to a data object
with irods_client.session() as session:
    obj = session.data_objects.get("/tempZone/home/rods/file.txt")
    obj.metadata.add("key", "value")
```

### Error Handling

```python
from rodrunner.irods.exceptions import iRODSException

try:
    obj = irods_client.get_data_object("/tempZone/home/rods/non_existent.txt")
except iRODSException as e:
    print(f"iRODS error: {e}")
```

## Performance Considerations

- **Use bulk operations** when possible (e.g., `upload_directory` instead of multiple `upload_file` calls)
- **Reuse the session** for multiple operations to avoid connection overhead
- **Use `force=True` with caution** when removing collections or data objects
- **Consider using a resource** for uploads to control where data is stored

## Examples

### Ingesting Sequencer Data

```python
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient
from rodrunner.parsers.factory import ParserFactory
import os

# Load the configuration
config = get_config()

# Create an iRODS client
irods_client = iRODSClient(config.irods)

# Create a parser factory
parser_factory = ParserFactory()

# Define the local and iRODS paths
local_run_dir = "/path/to/sequencer/run"
irods_run_path = "/tempZone/home/rods/sequencer/run"

# Parse the run metadata
metadata = parser_factory.parse_directory(local_run_dir)

# Extract key metadata for the collection
collection_metadata = {
    "run_id": metadata["RunInfo.xml"]["run_id"],
    "instrument": metadata["RunInfo.xml"]["instrument"],
    "date": metadata["RunInfo.xml"]["date"],
    "run_type": "miseq",
    "status": "raw"
}

# Upload the run directory with metadata
coll = irods_client.upload_directory(
    local_run_dir,
    irods_run_path,
    metadata=collection_metadata
)

print(f"Uploaded run to {irods_run_path}")
```

### Searching for Data by Metadata

```python
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient
from rodrunner.irods.query import query_by_metadata

# Load the configuration
config = get_config()

# Create an iRODS client
irods_client = iRODSClient(config.irods)

# Search for collections with specific metadata
results = query_by_metadata(
    irods_client,
    key="run_type",
    value="miseq",
    object_type="collection"
)

for result in results:
    print(f"Collection: {result.path}")
    
    # Get the collection and its metadata
    coll = irods_client.get_collection(result.path)
    for meta in coll.metadata.items():
        print(f"  {meta.name}: {meta.value}")
```

## API Reference

For detailed API documentation, see the [iRODS Client API Reference](../api-reference/irods-client.md).
