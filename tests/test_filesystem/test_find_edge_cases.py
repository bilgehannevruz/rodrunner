"""
Edge case tests for the filesystem.find module.
"""
import os
import pytest
import stat
import shutil
import tempfile
from typing import List, Generator
from pathlib import Path

from rodrunner.filesystem.find import find_files, find_sequencer_runs, _validate_sequencer_run


@pytest.mark.unit
def test_find_files_empty_directory(temp_dir: str) -> None:
    """Test find_files with an empty directory."""
    # Test finding files in an empty directory
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == 0
    
    # Test finding directories in an empty directory
    dirs = list(find_files(temp_dir, file_type='d'))
    assert len(dirs) == 0


@pytest.mark.unit
def test_find_files_nonexistent_directory() -> None:
    """Test find_files with a nonexistent directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_dir = os.path.join(temp_dir, "nonexistent")
        
        # Test finding files in a nonexistent directory
        with pytest.raises(FileNotFoundError):
            list(find_files(nonexistent_dir))


@pytest.mark.unit
def test_find_files_with_permission_issues(temp_dir: str) -> None:
    """Test find_files with permission issues."""
    if os.name == 'nt':  # Skip on Windows
        pytest.skip("Skipping permission test on Windows")
    
    # Create a directory with restricted permissions
    restricted_dir = os.path.join(temp_dir, "restricted")
    os.makedirs(restricted_dir)
    
    # Create a file in the restricted directory
    with open(os.path.join(restricted_dir, "file.txt"), "w") as f:
        f.write("test")
    
    # Remove read permissions from the directory
    os.chmod(restricted_dir, stat.S_IWUSR | stat.S_IXUSR)
    
    try:
        # Test finding files in a directory with restricted permissions
        # This should skip the restricted directory without failing
        files = list(find_files(temp_dir, file_type='f'))
        assert len(files) == 0
    finally:
        # Restore permissions to allow cleanup
        os.chmod(restricted_dir, stat.S_IRWXU)


@pytest.mark.unit
def test_find_files_with_symlinks(temp_dir: str) -> None:
    """Test find_files with symlinks."""
    if os.name == 'nt':  # Symlinks might not work on Windows without admin rights
        pytest.skip("Skipping symlink test on Windows")
    
    # Create directories and files
    dir1 = os.path.join(temp_dir, "dir1")
    dir2 = os.path.join(temp_dir, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)
    
    with open(os.path.join(dir1, "file1.txt"), "w") as f:
        f.write("test")
    
    # Create a symlink to dir1 inside dir2
    os.symlink(dir1, os.path.join(dir2, "link_to_dir1"))
    
    # Create a symlink to file1.txt inside dir2
    os.symlink(os.path.join(dir1, "file1.txt"), os.path.join(dir2, "link_to_file1.txt"))
    
    # Test finding files including symlinks
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == 2  # file1.txt and link_to_file1.txt
    
    # Test finding only symlinks
    symlinks = list(find_files(temp_dir, file_type='l'))
    assert len(symlinks) == 2  # link_to_dir1 and link_to_file1.txt
    
    # Test finding files excluding symlinks
    def is_not_symlink(path: str) -> bool:
        return not os.path.islink(path)
    
    real_files = list(find_files(temp_dir, file_type='f', custom_filter=is_not_symlink))
    assert len(real_files) == 1  # Only file1.txt


@pytest.mark.unit
def test_find_files_with_special_characters(temp_dir: str) -> None:
    """Test find_files with special characters in filenames."""
    # Create files with special characters
    special_chars = [
        "file with spaces.txt",
        "file_with_unicode_Ü_ñ_é.txt",
        "file-with-dashes.txt",
        "file_with_underscore.txt",
        "file.with.dots.txt",
        "file+with+plus.txt",
        "file'with'quotes.txt",
        "file\"with\"doublequotes.txt",
        "file(with)parentheses.txt",
        "file[with]brackets.txt",
        "file{with}braces.txt",
        "file#with#hash.txt",
        "file@with@at.txt",
        "file$with$dollar.txt",
        "file%with%percent.txt",
        "file^with^caret.txt",
        "file&with&ampersand.txt",
        "file=with=equals.txt",
        "file;with;semicolon.txt",
        "file,with,comma.txt"
    ]
    
    for filename in special_chars:
        with open(os.path.join(temp_dir, filename), "w") as f:
            f.write("test")
    
    # Test finding all files
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == len(special_chars)
    
    # Test finding files with a pattern that includes special characters
    files = list(find_files(temp_dir, file_type='f', name_pattern="*with*"))
    assert len(files) == len(special_chars) - 1  # All except "file with spaces.txt"
    
    # Test finding a specific file with spaces
    files = list(find_files(temp_dir, file_type='f', name_pattern="*spaces*"))
    assert len(files) == 1
    assert os.path.basename(files[0]) == "file with spaces.txt"


@pytest.mark.unit
def test_find_files_with_very_long_paths(temp_dir: str) -> None:
    """Test find_files with very long paths."""
    # Create a deeply nested directory structure
    current_dir = temp_dir
    depth = 15  # Create a path with 15 levels of nesting
    
    for i in range(depth):
        current_dir = os.path.join(current_dir, f"level_{i}")
        os.makedirs(current_dir, exist_ok=True)
    
    # Create a file at the deepest level
    with open(os.path.join(current_dir, "deep_file.txt"), "w") as f:
        f.write("test")
    
    # Test finding the file with no depth limit
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == 1
    assert os.path.basename(files[0]) == "deep_file.txt"
    
    # Test finding the file with a depth limit that's too low
    files = list(find_files(temp_dir, file_type='f', max_depth=5))
    assert len(files) == 0
    
    # Test finding the file with a depth limit that's just right
    files = list(find_files(temp_dir, file_type='f', max_depth=depth))
    assert len(files) == 1
    assert os.path.basename(files[0]) == "deep_file.txt"


@pytest.mark.unit
def test_find_files_with_large_directory(temp_dir: str) -> None:
    """Test find_files with a large number of files."""
    # Create a large number of files
    num_files = 1000
    for i in range(num_files):
        with open(os.path.join(temp_dir, f"file_{i}.txt"), "w") as f:
            f.write(f"content for file {i}")
    
    # Test finding all files
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == num_files
    
    # Test finding files with a pattern
    files = list(find_files(temp_dir, file_type='f', name_pattern="*_5*.txt"))
    # Should match file_5.txt, file_50.txt, ..., file_59.txt, file_500.txt, ..., file_599.txt
    expected_matches = 1 + 10 + 100  # 5, 50-59, 500-599
    assert len(files) == expected_matches
    
    # Test using a custom filter to find files with specific content
    def has_content_42(path: str) -> bool:
        with open(path, 'r') as f:
            return "content for file 42" in f.read()
    
    files = list(find_files(temp_dir, file_type='f', custom_filter=has_content_42))
    assert len(files) == 1
    assert os.path.basename(files[0]) == "file_42.txt"


@pytest.mark.unit
def test_find_sequencer_runs_with_invalid_runs(temp_dir: str, sample_run_info_xml: str, 
                                             sample_run_parameters_xml: str, 
                                             sample_samplesheet_csv: str) -> None:
    """Test find_sequencer_runs with invalid runs."""
    # Create a valid run
    valid_run_dir = os.path.join(temp_dir, "220101_M00001_0001_000000000-A1B2C")
    os.makedirs(valid_run_dir)
    
    with open(os.path.join(valid_run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    with open(os.path.join(valid_run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    with open(os.path.join(valid_run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    with open(os.path.join(valid_run_dir, "RTAComplete.txt"), "w") as f:
        f.write("RTA Complete")
    
    # Create an incomplete run (missing RTAComplete.txt)
    incomplete_run_dir = os.path.join(temp_dir, "220102_M00001_0002_000000000-A1B2D")
    os.makedirs(incomplete_run_dir)
    
    with open(os.path.join(incomplete_run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml.replace("220101_M00001_0001_000000000-A1B2C", "220102_M00001_0002_000000000-A1B2D"))
    
    with open(os.path.join(incomplete_run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml.replace("220101_M00001_0001_000000000-A1B2C", "220102_M00001_0002_000000000-A1B2D"))
    
    with open(os.path.join(incomplete_run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    # Create a run with invalid XML
    invalid_xml_run_dir = os.path.join(temp_dir, "220103_M00001_0003_000000000-A1B2E")
    os.makedirs(invalid_xml_run_dir)
    
    with open(os.path.join(invalid_xml_run_dir, "RunInfo.xml"), "w") as f:
        f.write("This is not valid XML")
    
    with open(os.path.join(invalid_xml_run_dir, "RunParameters.xml"), "w") as f:
        f.write("This is not valid XML either")
    
    with open(os.path.join(invalid_xml_run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    with open(os.path.join(invalid_xml_run_dir, "RTAComplete.txt"), "w") as f:
        f.write("RTA Complete")
    
    # Create a run with a different naming pattern
    different_name_run_dir = os.path.join(temp_dir, "MiSeq_Run_2022_01_04")
    os.makedirs(different_name_run_dir)
    
    with open(os.path.join(different_name_run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    with open(os.path.join(different_name_run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    with open(os.path.join(different_name_run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    with open(os.path.join(different_name_run_dir, "RTAComplete.txt"), "w") as f:
        f.write("RTA Complete")
    
    # Test finding sequencer runs
    run_dirs = list(find_sequencer_runs(temp_dir, "miseq"))
    assert len(run_dirs) == 1
    assert valid_run_dir in run_dirs
    assert incomplete_run_dir not in run_dirs  # Missing RTAComplete.txt
    assert invalid_xml_run_dir not in run_dirs  # Invalid XML
    assert different_name_run_dir not in run_dirs  # Different naming pattern
    
    # Test finding sequencer runs with a different completion indicator
    with open(os.path.join(incomplete_run_dir, "CopyComplete.txt"), "w") as f:
        f.write("Copy Complete")
    
    run_dirs = list(find_sequencer_runs(temp_dir, "miseq", completion_indicator="CopyComplete.txt"))
    assert len(run_dirs) == 1
    assert incomplete_run_dir in run_dirs
    assert valid_run_dir not in run_dirs  # Has RTAComplete.txt but not CopyComplete.txt
    
    # Test finding sequencer runs with no completion indicator
    run_dirs = list(find_sequencer_runs(temp_dir, "miseq", completion_indicator=None))
    assert len(run_dirs) >= 2  # Should include at least valid_run_dir and incomplete_run_dir
    assert valid_run_dir in run_dirs
    assert incomplete_run_dir in run_dirs


@pytest.mark.unit
def test_validate_sequencer_run_edge_cases(temp_dir: str, sample_run_info_xml: str, 
                                         sample_run_parameters_xml: str, 
                                         sample_samplesheet_csv: str) -> None:
    """Test _validate_sequencer_run with edge cases."""
    # Create a run directory
    run_dir = os.path.join(temp_dir, "220101_M00001_0001_000000000-A1B2C")
    os.makedirs(run_dir)
    
    # Test with an empty directory
    assert _validate_sequencer_run(run_dir, "miseq") is False
    
    # Test with only RunInfo.xml
    with open(os.path.join(run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    assert _validate_sequencer_run(run_dir, "miseq") is False
    
    # Test with RunInfo.xml and RunParameters.xml
    with open(os.path.join(run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    assert _validate_sequencer_run(run_dir, "miseq") is False
    
    # Test with all required files
    with open(os.path.join(run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    assert _validate_sequencer_run(run_dir, "miseq") is True
    
    # Test with corrupted RunInfo.xml
    os.remove(os.path.join(run_dir, "RunInfo.xml"))
    with open(os.path.join(run_dir, "RunInfo.xml"), "w") as f:
        f.write("This is not valid XML")
    
    assert _validate_sequencer_run(run_dir, "miseq") is False
    
    # Test with empty files
    os.remove(os.path.join(run_dir, "RunInfo.xml"))
    os.remove(os.path.join(run_dir, "RunParameters.xml"))
    os.remove(os.path.join(run_dir, "SampleSheet.csv"))
    
    with open(os.path.join(run_dir, "RunInfo.xml"), "w") as f:
        f.write("")
    
    with open(os.path.join(run_dir, "RunParameters.xml"), "w") as f:
        f.write("")
    
    with open(os.path.join(run_dir, "SampleSheet.csv"), "w") as f:
        f.write("")
    
    assert _validate_sequencer_run(run_dir, "miseq") is False
    
    # Test with a directory that has the required files but is not a sequencer run
    not_a_run_dir = os.path.join(temp_dir, "not_a_run")
    os.makedirs(not_a_run_dir)
    
    with open(os.path.join(not_a_run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)
    
    with open(os.path.join(not_a_run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)
    
    with open(os.path.join(not_a_run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)
    
    assert _validate_sequencer_run(not_a_run_dir, "miseq") is False  # Not a valid run name pattern
