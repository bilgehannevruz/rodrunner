"""
Tests for the filesystem.find module.
"""
import os
import pytest
from typing import List

from rodrunner.filesystem.find import find_files, find_sequencer_runs, _validate_sequencer_run


@pytest.mark.unit
def test_find_files_basic(temp_dir: str) -> None:
    """Test basic functionality of find_files."""
    # Create test files
    os.makedirs(os.path.join(temp_dir, "dir1"))
    os.makedirs(os.path.join(temp_dir, "dir2"))
    
    with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "dir1", "file3.txt"), "w") as f:
        f.write("test")
    
    # Test finding all files
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == 3
    
    # Test finding only files in the root directory
    files = list(find_files(temp_dir, file_type='f', max_depth=0))
    assert len(files) == 2
    
    # Test finding only directories
    dirs = list(find_files(temp_dir, file_type='d'))
    assert len(dirs) == 2
    
    # Test finding files with a pattern
    files = list(find_files(temp_dir, file_type='f', name_pattern="*.txt"))
    assert len(files) == 3
    
    # Test finding files with a pattern that doesn't match
    files = list(find_files(temp_dir, file_type='f', name_pattern="*.csv"))
    assert len(files) == 0


@pytest.mark.unit
def test_find_files_depth_filtering(temp_dir: str) -> None:
    """Test depth filtering in find_files."""
    # Create a nested directory structure
    os.makedirs(os.path.join(temp_dir, "level1", "level2", "level3"))
    
    with open(os.path.join(temp_dir, "root.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "level1", "level1.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "level1", "level2", "level2.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "level1", "level2", "level3", "level3.txt"), "w") as f:
        f.write("test")
    
    # Test min_depth
    files = list(find_files(temp_dir, file_type='f', min_depth=2))
    assert len(files) == 2
    assert all("level1.txt" not in f for f in files)
    assert all("root.txt" not in f for f in files)
    
    # Test max_depth
    files = list(find_files(temp_dir, file_type='f', max_depth=1))
    assert len(files) == 2
    assert any("root.txt" in f for f in files)
    assert any("level1.txt" in f for f in files)
    
    # Test both min_depth and max_depth
    files = list(find_files(temp_dir, file_type='f', min_depth=1, max_depth=2))
    assert len(files) == 2
    assert any("level1.txt" in f for f in files)
    assert any("level2.txt" in f for f in files)
    assert all("level3.txt" not in f for f in files)


@pytest.mark.unit
def test_find_files_exclude_dirs(temp_dir: str) -> None:
    """Test excluding directories in find_files."""
    # Create test directories and files
    os.makedirs(os.path.join(temp_dir, "include"))
    os.makedirs(os.path.join(temp_dir, "exclude"))
    
    with open(os.path.join(temp_dir, "include", "file1.txt"), "w") as f:
        f.write("test")
    
    with open(os.path.join(temp_dir, "exclude", "file2.txt"), "w") as f:
        f.write("test")
    
    # Test excluding a directory
    files = list(find_files(temp_dir, file_type='f', exclude_dirs=["exclude"]))
    assert len(files) == 1
    assert all("exclude" not in f for f in files)


@pytest.mark.unit
def test_find_files_custom_filter(temp_dir: str) -> None:
    """Test custom filter in find_files."""
    # Create test files
    with open(os.path.join(temp_dir, "small.txt"), "w") as f:
        f.write("small")
    
    with open(os.path.join(temp_dir, "large.txt"), "w") as f:
        f.write("large content" * 100)
    
    # Custom filter to find files larger than 100 bytes
    def is_large_file(path: str) -> bool:
        return os.path.getsize(path) > 100
    
    # Test custom filter
    files = list(find_files(temp_dir, file_type='f', custom_filter=is_large_file))
    assert len(files) == 1
    assert any("large.txt" in f for f in files)


@pytest.mark.unit
def test_find_sequencer_runs(sample_sequencer_run: str, temp_dir: str) -> None:
    """Test find_sequencer_runs function."""
    # The fixture already creates a valid sequencer run
    run_dirs = list(find_sequencer_runs(temp_dir, "miseq"))
    assert len(run_dirs) == 1
    assert sample_sequencer_run in run_dirs
    
    # Test with a non-existent completion indicator
    run_dirs = list(find_sequencer_runs(temp_dir, "miseq", completion_indicator="NonExistent.txt"))
    assert len(run_dirs) == 0


@pytest.mark.unit
def test_validate_sequencer_run(sample_sequencer_run: str) -> None:
    """Test _validate_sequencer_run function."""
    # Test with a valid MiSeq run
    assert _validate_sequencer_run(sample_sequencer_run, "miseq") is True
    
    # Test with an invalid sequencer type
    assert _validate_sequencer_run(sample_sequencer_run, "invalid_type") is False
    
    # Test with a valid run but wrong sequencer type
    assert _validate_sequencer_run(sample_sequencer_run, "novaseq") is False
    
    # Test with missing required file
    os.remove(os.path.join(sample_sequencer_run, "SampleSheet.csv"))
    assert _validate_sequencer_run(sample_sequencer_run, "miseq") is False
