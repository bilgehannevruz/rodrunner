# Workflows API Reference

This page contains the API reference for the workflows module.

## `ingest_sequencer_runs`

```python
@flow(name="Ingest Sequencer Runs")
def ingest_sequencer_runs(
    config: AppConfig,
    sequencer_type: str,
    root_dir: str = None,
    completion_indicator: str = "RTAComplete.txt"
) -> List[Dict[str, Any]]:
    """
    Ingest all completed sequencer runs of a specific type.
    
    Args:
        config: Application configuration
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        root_dir: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        List of dictionaries with the results of the ingestion
    """
```

This flow ingests all completed sequencer runs of a specific type.

### Parameters

- `config`: Application configuration
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)
- `root_dir`: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
- `completion_indicator`: Filename that indicates a completed run

### Returns

List of dictionaries with the results of the ingestion.

### Example

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_sequencer_runs(
    config=config,
    sequencer_type="miseq",
    root_dir="/path/to/sequencer/miseq"
)

# Print the results
for result in results:
    print(f"Run: {result['run_dir']}, Success: {result['success']}")
```

## `ingest_all_sequencer_runs`

```python
@flow(name="Ingest All Sequencer Runs")
def ingest_all_sequencer_runs(
    config: AppConfig,
    root_dir: str = None,
    completion_indicator: str = "RTAComplete.txt"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Ingest all completed sequencer runs of all supported types.
    
    Args:
        config: Application configuration
        root_dir: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        Dictionary mapping sequencer types to lists of ingestion results
    """
```

This flow ingests all completed sequencer runs of all supported types.

### Parameters

- `config`: Application configuration
- `root_dir`: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
- `completion_indicator`: Filename that indicates a completed run

### Returns

Dictionary mapping sequencer types to lists of ingestion results.

### Example

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_all_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_all_sequencer_runs(
    config=config,
    root_dir="/path/to/sequencer"
)

# Print the results
for sequencer_type, type_results in results.items():
    print(f"Sequencer type: {sequencer_type}")
    for result in type_results:
        print(f"  Run: {result['run_dir']}, Success: {result['success']}")
```

## `update_run_metadata`

```python
@flow(name="Update Run Metadata")
def update_run_metadata(
    config: AppConfig,
    irods_path: str,
    sequencer_type: str
) -> Dict[str, Any]:
    """
    Update metadata for a sequencer run in iRODS.
    
    Args:
        config: Application configuration
        irods_path: Path to the sequencer run in iRODS
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        
    Returns:
        Dictionary with the result of the metadata update
    """
```

This flow updates metadata for a sequencer run in iRODS.

### Parameters

- `config`: Application configuration
- `irods_path`: Path to the sequencer run in iRODS
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)

### Returns

Dictionary with the result of the metadata update.

### Example

```python
from rodrunner.config import get_config
from rodrunner.workflows.metadata import update_run_metadata

# Load the configuration
config = get_config()

# Run the metadata update workflow
result = update_run_metadata(
    config=config,
    irods_path="/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
    sequencer_type="miseq"
)

# Print the result
print(f"Success: {result['success']}")
if result['success']:
    print(f"Updated metadata for {result['irods_path']}")
else:
    print(f"Error: {result['error']}")
```

## Tasks

### `find_sequencer_runs_task`

```python
@task
def find_sequencer_runs_task(
    root_dir: str,
    sequencer_type: str,
    completion_indicator: str = "RTAComplete.txt"
) -> List[str]:
    """
    Find sequencer runs of a specific type.
    
    Args:
        root_dir: Root directory to search for sequencer runs
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        List of paths to sequencer run directories
    """
```

This task finds sequencer runs of a specific type.

#### Parameters

- `root_dir`: Root directory to search for sequencer runs
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)
- `completion_indicator`: Filename that indicates a completed run

#### Returns

List of paths to sequencer run directories.

### `ingest_sequencer_run_task`

```python
@task
def ingest_sequencer_run_task(
    config: AppConfig,
    run_dir: str,
    sequencer_type: str
) -> Dict[str, Any]:
    """
    Ingest a sequencer run.
    
    Args:
        config: Application configuration
        run_dir: Path to the sequencer run directory
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        
    Returns:
        Dictionary with the result of the ingestion
    """
```

This task ingests a sequencer run.

#### Parameters

- `config`: Application configuration
- `run_dir`: Path to the sequencer run directory
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)

#### Returns

Dictionary with the result of the ingestion.

### `extract_run_metadata_task`

```python
@task
def extract_run_metadata_task(
    config: AppConfig,
    irods_path: str,
    sequencer_type: str
) -> Dict[str, Any]:
    """
    Extract metadata from a sequencer run in iRODS.
    
    Args:
        config: Application configuration
        irods_path: Path to the sequencer run in iRODS
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        
    Returns:
        Dictionary with the extracted metadata
    """
```

This task extracts metadata from a sequencer run in iRODS.

#### Parameters

- `config`: Application configuration
- `irods_path`: Path to the sequencer run in iRODS
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)

#### Returns

Dictionary with the extracted metadata.

### `update_run_metadata_task`

```python
@task
def update_run_metadata_task(
    config: AppConfig,
    irods_path: str,
    metadata: Dict[str, str]
) -> Dict[str, Any]:
    """
    Update metadata for a sequencer run in iRODS.
    
    Args:
        config: Application configuration
        irods_path: Path to the sequencer run in iRODS
        metadata: Metadata to update
        
    Returns:
        Dictionary with the result of the metadata update
    """
```

This task updates metadata for a sequencer run in iRODS.

#### Parameters

- `config`: Application configuration
- `irods_path`: Path to the sequencer run in iRODS
- `metadata`: Metadata to update

#### Returns

Dictionary with the result of the metadata update.

## Notes

- The `ingest_sequencer_runs` flow ingests all completed sequencer runs of a specific type.
- The `ingest_all_sequencer_runs` flow ingests all completed sequencer runs of all supported types.
- The `update_run_metadata` flow updates metadata for a sequencer run in iRODS.
- The tasks are used by the flows to perform specific operations, such as finding sequencer runs, ingesting a sequencer run, extracting metadata, and updating metadata.
