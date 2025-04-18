# Filesystem Operations

The filesystem module provides generator-based file finding utilities similar to the Unix find command. It allows you to search for files with various filters, including depth, name patterns, and custom filters.

## Key Features

- **Memory-efficient generators** for file finding
- **Depth filtering** with min_depth and max_depth parameters
- **Name pattern filtering** using glob patterns
- **File type filtering** for files, directories, and symlinks
- **Custom filters** for advanced filtering
- **Sequencer run detection** for various sequencer types

## Basic Usage

### Finding Files

The `find_files` function is the core function for finding files. It returns a generator that yields paths to files that match the specified criteria.

```python
from rodrunner.filesystem.find import find_files

# Find all files in a directory
for file_path in find_files("/path/to/directory"):
    print(file_path)

# Find files with a specific extension
for file_path in find_files("/path/to/directory", name_pattern="*.fastq.gz"):
    print(file_path)

# Find directories
for dir_path in find_files("/path/to/directory", file_type='d'):
    print(dir_path)

# Find files at a specific depth
for file_path in find_files("/path/to/directory", min_depth=2, max_depth=3):
    print(file_path)

# Exclude specific directories
for file_path in find_files("/path/to/directory", exclude_dirs=["node_modules", ".git"]):
    print(file_path)

# Use a custom filter
def is_large_file(path):
    return os.path.getsize(path) > 1_000_000

for file_path in find_files("/path/to/directory", custom_filter=is_large_file):
    print(file_path)
```

### Finding Sequencer Runs

The `find_sequencer_runs` function is a specialized function for finding sequencer run directories. It returns a generator that yields paths to sequencer run directories that match the specified criteria.

```python
from rodrunner.filesystem.find import find_sequencer_runs

# Find MiSeq runs
for run_dir in find_sequencer_runs("/path/to/sequencer/data", "miseq"):
    print(run_dir)

# Find NovaSeq runs with a custom completion indicator
for run_dir in find_sequencer_runs("/path/to/sequencer/data", "novaseq", completion_indicator="CopyComplete.txt"):
    print(run_dir)
```

## Advanced Usage

### Validating Sequencer Runs

The `_validate_sequencer_run` function is used internally by `find_sequencer_runs` to validate that a directory is a valid sequencer run. You can use it directly if you need more control over the validation process.

```python
from rodrunner.filesystem.find import _validate_sequencer_run

# Check if a directory is a valid MiSeq run
is_valid = _validate_sequencer_run("/path/to/run/directory", "miseq")
```

### Custom Filters

You can create custom filters for the `find_files` function to implement advanced filtering logic.

```python
from rodrunner.filesystem.find import find_files
import os
import time

# Find files modified in the last 24 hours
def is_recent_file(path):
    return time.time() - os.path.getmtime(path) < 86400

for file_path in find_files("/path/to/directory", custom_filter=is_recent_file):
    print(file_path)

# Find empty files
def is_empty_file(path):
    return os.path.isfile(path) and os.path.getsize(path) == 0

for file_path in find_files("/path/to/directory", custom_filter=is_empty_file):
    print(file_path)
```

## Performance Considerations

The `find_files` function uses generators to yield results one at a time, which makes it memory-efficient even when searching large directory trees. However, there are some performance considerations to keep in mind:

- **Use `max_depth` when possible** to limit the depth of the search
- **Use `exclude_dirs` to skip large directories** that you don't need to search
- **Use `name_pattern` and `file_type` filters** to reduce the number of files processed
- **Implement efficient custom filters** that return quickly for most files

## Examples

### Finding Sequencer Runs and Processing Them

```python
from rodrunner.filesystem.find import find_sequencer_runs
from rodrunner.parsers.factory import ParserFactory

# Create a parser factory
parser_factory = ParserFactory()

# Find MiSeq runs
for run_dir in find_sequencer_runs("/path/to/sequencer/data", "miseq"):
    print(f"Processing run: {run_dir}")
    
    # Parse the run metadata
    metadata = parser_factory.parse_directory(run_dir)
    
    # Process the metadata
    run_id = metadata["RunInfo.xml"]["run_id"]
    instrument = metadata["RunInfo.xml"]["instrument"]
    
    print(f"Run ID: {run_id}, Instrument: {instrument}")
```

### Finding Files with Multiple Filters

```python
from rodrunner.filesystem.find import find_files
import os

# Find large FASTQ files in a specific depth range
def is_large_fastq(path):
    return (
        path.endswith(".fastq.gz") and
        os.path.getsize(path) > 1_000_000_000  # 1 GB
    )

for file_path in find_files(
    "/path/to/sequencer/data",
    min_depth=2,
    max_depth=4,
    custom_filter=is_large_fastq
):
    print(f"Large FASTQ file: {file_path}")
```

## API Reference

For detailed API documentation, see the [Filesystem API Reference](../api-reference/filesystem.md).
