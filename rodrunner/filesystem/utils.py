"""
General filesystem utilities.
"""
import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Generator


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size of the file in bytes
    """
    return os.path.getsize(file_path)


def get_file_checksum(file_path: str, algorithm: str = 'md5', buffer_size: int = 65536) -> str:
    """
    Calculate the checksum of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')
        buffer_size: Size of the buffer for reading the file
        
    Returns:
        Hexadecimal digest of the file
    """
    if algorithm == 'md5':
        hash_obj = hashlib.md5()
    elif algorithm == 'sha1':
        hash_obj = hashlib.sha1()
    elif algorithm == 'sha256':
        hash_obj = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hash_obj.update(data)
    
    return hash_obj.hexdigest()


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
    """
    os.makedirs(directory, exist_ok=True)


def is_file_newer_than(file_path: str, reference_time: float) -> bool:
    """
    Check if a file is newer than a reference time.
    
    Args:
        file_path: Path to the file
        reference_time: Reference time in seconds since the epoch
        
    Returns:
        True if the file is newer than the reference time, False otherwise
    """
    return os.path.getmtime(file_path) > reference_time


def get_files_by_extension(directory: str, extension: str) -> List[str]:
    """
    Get all files in a directory with a specific extension.
    
    Args:
        directory: Path to the directory
        extension: File extension to match (e.g., '.fastq.gz')
        
    Returns:
        List of file paths
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) 
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)]


def copy_file_with_metadata(src: str, dst: str) -> None:
    """
    Copy a file with its metadata (permissions, timestamps, etc.).
    
    Args:
        src: Source file path
        dst: Destination file path
    """
    shutil.copy2(src, dst)


def get_directory_size(directory: str) -> int:
    """
    Calculate the total size of a directory in bytes.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    
    return total_size


def is_directory_empty(directory: str) -> bool:
    """
    Check if a directory is empty.
    
    Args:
        directory: Path to the directory
        
    Returns:
        True if the directory is empty, False otherwise
    """
    return len(os.listdir(directory)) == 0
