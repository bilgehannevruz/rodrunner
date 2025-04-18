"""
Common filesystem tasks for Prefect workflows.
"""
from typing import Dict, List, Optional, Union, Any, Callable
import os

from prefect import task

from irods_prefect.filesystem.find import find_files, find_sequencer_runs
from irods_prefect.filesystem.utils import (
    get_file_size, get_file_checksum, ensure_directory_exists,
    is_file_newer_than, get_files_by_extension, copy_file_with_metadata,
    get_directory_size, is_directory_empty
)


@task(name="find_files_task")
def find_files_task(
    root_dir: str,
    min_depth: int = 0,
    max_depth: Optional[int] = None,
    name_pattern: Optional[str] = None,
    file_type: str = 'f',
    exclude_dirs: Optional[List[str]] = None,
    custom_filter: Optional[Callable[[str], bool]] = None
) -> List[str]:
    """
    Find files/directories recursively with filtering options.
    
    Args:
        root_dir: Starting directory for the search
        min_depth: Minimum directory depth to include results from
        max_depth: Maximum directory depth to search (None for unlimited)
        name_pattern: Glob pattern to match filenames (e.g., "*.fastq.gz")
        file_type: Type of filesystem objects to return ('f' for files, 'd' for directories, 'l' for links)
        exclude_dirs: List of directory names to exclude from search
        custom_filter: Optional custom filter function that takes a path and returns boolean
        
    Returns:
        List of paths to files/directories that match the criteria
    """
    return list(find_files(
        root_dir=root_dir,
        min_depth=min_depth,
        max_depth=max_depth,
        name_pattern=name_pattern,
        file_type=file_type,
        exclude_dirs=exclude_dirs,
        custom_filter=custom_filter
    ))


@task(name="find_sequencer_runs_task")
def find_sequencer_runs_task(
    root_dir: str,
    sequencer_type: str,
    completion_indicator: str = "RTAComplete.txt"
) -> List[str]:
    """
    Find sequencer run directories of a specific type that have completed.
    
    Args:
        root_dir: Root directory to search for sequencer runs
        sequencer_type: Type of sequencer (miseq, nextseq, etc.)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        List of paths to completed sequencer run directories
    """
    return list(find_sequencer_runs(
        root_dir=root_dir,
        sequencer_type=sequencer_type,
        completion_indicator=completion_indicator
    ))


@task(name="get_file_size_task")
def get_file_size_task(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size of the file in bytes
    """
    return get_file_size(file_path)


@task(name="get_file_checksum_task")
def get_file_checksum_task(
    file_path: str,
    algorithm: str = 'md5',
    buffer_size: int = 65536
) -> str:
    """
    Calculate the checksum of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')
        buffer_size: Size of the buffer for reading the file
        
    Returns:
        Hexadecimal digest of the file
    """
    return get_file_checksum(file_path, algorithm, buffer_size)


@task(name="ensure_directory_exists_task")
def ensure_directory_exists_task(directory: str) -> str:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Path to the directory
    """
    ensure_directory_exists(directory)
    return directory


@task(name="get_files_by_extension_task")
def get_files_by_extension_task(directory: str, extension: str) -> List[str]:
    """
    Get all files in a directory with a specific extension.
    
    Args:
        directory: Path to the directory
        extension: File extension to match (e.g., '.fastq.gz')
        
    Returns:
        List of file paths
    """
    return get_files_by_extension(directory, extension)


@task(name="copy_file_with_metadata_task")
def copy_file_with_metadata_task(src: str, dst: str) -> str:
    """
    Copy a file with its metadata (permissions, timestamps, etc.).
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        Destination file path
    """
    copy_file_with_metadata(src, dst)
    return dst


@task(name="get_directory_size_task")
def get_directory_size_task(directory: str) -> int:
    """
    Calculate the total size of a directory in bytes.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Total size in bytes
    """
    return get_directory_size(directory)


@task(name="is_directory_empty_task")
def is_directory_empty_task(directory: str) -> bool:
    """
    Check if a directory is empty.
    
    Args:
        directory: Path to the directory
        
    Returns:
        True if the directory is empty, False otherwise
    """
    return is_directory_empty(directory)
