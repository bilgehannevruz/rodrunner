# Filesystem API Reference

This page contains the API reference for the filesystem module.

## `find_files`

```python
def find_files(
    root_dir: str,
    file_type: str = 'f',
    min_depth: int = None,
    max_depth: int = None,
    name_pattern: str = None,
    exclude_dirs: List[str] = None,
    custom_filter: Callable[[str], bool] = None
) -> Generator[str, None, None]:
    """
    Find files or directories recursively from root_dir.
    
    Args:
        root_dir: Root directory to start the search from
        file_type: Type of files to find ('f' for files, 'd' for directories, 'l' for symlinks)
        min_depth: Minimum depth to search (0 = root_dir)
        max_depth: Maximum depth to search
        name_pattern: Glob pattern to match filenames
        exclude_dirs: List of directory names to exclude from search
        custom_filter: Custom filter function that takes a path and returns a boolean
        
    Returns:
        Generator yielding paths to files or directories that match the criteria
    """
```

This function finds files or directories recursively from a root directory, with various filtering options.

### Parameters

- `root_dir`: Root directory to start the search from
- `file_type`: Type of files to find ('f' for files, 'd' for directories, 'l' for symlinks)
- `min_depth`: Minimum depth to search (0 = root_dir)
- `max_depth`: Maximum depth to search
- `name_pattern`: Glob pattern to match filenames
- `exclude_dirs`: List of directory names to exclude from search
- `custom_filter`: Custom filter function that takes a path and returns a boolean

### Returns

Generator yielding paths to files or directories that match the criteria.

### Example

```python
# Find all Python files in the current directory and its subdirectories
for file_path in find_files(".", name_pattern="*.py"):
    print(file_path)

# Find all directories at depth 1
for dir_path in find_files(".", file_type='d', min_depth=1, max_depth=1):
    print(dir_path)

# Find all files larger than 1 MB
def is_large_file(path):
    return os.path.getsize(path) > 1_000_000

for file_path in find_files(".", custom_filter=is_large_file):
    print(file_path)
```

## `find_sequencer_runs`

```python
def find_sequencer_runs(
    root_dir: str,
    sequencer_type: str,
    completion_indicator: str = "RTAComplete.txt"
) -> Generator[str, None, None]:
    """
    Find sequencer runs of a specific type.
    
    Args:
        root_dir: Root directory to search for sequencer runs
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        completion_indicator: File that indicates a completed run
        
    Returns:
        Generator yielding paths to sequencer run directories
    """
```

This function finds sequencer runs of a specific type in a directory.

### Parameters

- `root_dir`: Root directory to search for sequencer runs
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)
- `completion_indicator`: File that indicates a completed run

### Returns

Generator yielding paths to sequencer run directories.

### Example

```python
# Find all completed MiSeq runs
for run_dir in find_sequencer_runs("/path/to/sequencer/data", "miseq"):
    print(run_dir)

# Find all completed NovaSeq runs with a custom completion indicator
for run_dir in find_sequencer_runs("/path/to/sequencer/data", "novaseq", completion_indicator="CopyComplete.txt"):
    print(run_dir)
```

## `_validate_sequencer_run`

```python
def _validate_sequencer_run(
    run_dir: str,
    sequencer_type: str
) -> bool:
    """
    Validate that a directory is a valid sequencer run.
    
    Args:
        run_dir: Path to the run directory
        sequencer_type: Type of sequencer (miseq, nextseq, novaseq, etc.)
        
    Returns:
        True if the directory is a valid sequencer run, False otherwise
    """
```

This function validates that a directory is a valid sequencer run of a specific type.

### Parameters

- `run_dir`: Path to the run directory
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)

### Returns

True if the directory is a valid sequencer run, False otherwise.

### Example

```python
# Check if a directory is a valid MiSeq run
is_valid = _validate_sequencer_run("/path/to/run/directory", "miseq")
```

## Notes

- The `find_files` function uses generators to yield results one at a time, which makes it memory-efficient even when searching large directory trees.
- The `find_sequencer_runs` function uses `_validate_sequencer_run` to validate that a directory is a valid sequencer run.
- The `_validate_sequencer_run` function checks for required files and naming patterns specific to each sequencer type.
