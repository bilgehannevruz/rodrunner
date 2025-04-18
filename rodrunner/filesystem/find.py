"""
Generator-based file finding utilities similar to the Unix find command.
"""
import os
import fnmatch
from typing import Generator, List, Optional, Union, Callable


def find_files(
    root_dir: str,
    min_depth: int = 0,
    max_depth: Optional[int] = None,
    name_pattern: Optional[str] = None,
    file_type: str = 'f',  # 'f' for files, 'd' for directories, 'l' for links
    exclude_dirs: Optional[List[str]] = None,
    custom_filter: Optional[Callable[[str], bool]] = None
) -> Generator[str, None, None]:
    """
    Generator function to find files/directories recursively with filtering options.

    Args:
        root_dir: Starting directory for the search
        min_depth: Minimum directory depth to include results from
        max_depth: Maximum directory depth to search (None for unlimited)
        name_pattern: Glob pattern to match filenames (e.g., "*.fastq.gz")
        file_type: Type of filesystem objects to return ('f' for files, 'd' for directories, 'l' for links)
        exclude_dirs: List of directory names to exclude from search
        custom_filter: Optional custom filter function that takes a path and returns boolean

    Yields:
        Paths to files/directories that match the criteria
    """
    exclude_dirs = exclude_dirs or []

    for current_depth, (dirpath, dirnames, filenames) in enumerate(os.walk(root_dir, topdown=True)):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        # Calculate relative depth
        rel_path = os.path.relpath(dirpath, root_dir)
        rel_depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1

        # Check if we've exceeded max_depth
        if max_depth is not None and rel_depth > max_depth:
            dirnames[:] = []  # Don't go deeper
            continue

        # Skip if we haven't reached min_depth yet
        if rel_depth < min_depth:
            continue

        # Process directories if requested
        if file_type == 'd':
            for dirname in dirnames:
                full_path = os.path.join(dirpath, dirname)
                if name_pattern and not fnmatch.fnmatch(dirname, name_pattern):
                    continue
                if custom_filter and not custom_filter(full_path):
                    continue
                yield full_path

        # Process files if requested
        if file_type == 'f':
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if name_pattern and not fnmatch.fnmatch(filename, name_pattern):
                    continue
                if custom_filter and not custom_filter(full_path):
                    continue
                if os.path.isfile(full_path):  # Ensure it's a file
                    yield full_path

        # Process symlinks if requested
        if file_type == 'l':
            for name in dirnames + filenames:
                full_path = os.path.join(dirpath, name)
                if name_pattern and not fnmatch.fnmatch(name, name_pattern):
                    continue
                if custom_filter and not custom_filter(full_path):
                    continue
                if os.path.islink(full_path):  # Ensure it's a symlink
                    yield full_path


def find_sequencer_runs(
    root_dir: str,
    sequencer_type: str,
    completion_indicator: str = "RTAComplete.txt"
) -> Generator[str, None, None]:
    """
    Find sequencer run directories of a specific type that have completed.

    Args:
        root_dir: Root directory to search for sequencer runs
        sequencer_type: Type of sequencer (miseq, nextseq, etc.)
        completion_indicator: Filename that indicates a completed run

    Yields:
        Paths to completed sequencer run directories
    """
    # Define custom filter to check for completion indicator
    def is_complete_run(path: str) -> bool:
        return os.path.isfile(os.path.join(path, completion_indicator))

    # Find directories that match the sequencer type pattern
    for run_dir in find_files(
        root_dir,
        file_type='d',
        custom_filter=is_complete_run
    ):
        # Additional validation based on sequencer type
        if _validate_sequencer_run(run_dir, sequencer_type):
            yield run_dir


def _validate_sequencer_run(run_dir: str, sequencer_type: str) -> bool:
    """
    Validate if a directory is a valid sequencer run of the specified type.

    Args:
        run_dir: Path to the run directory
        sequencer_type: Type of sequencer

    Returns:
        True if valid, False otherwise
    """
    # Implement validation logic based on sequencer type
    required_files = {
        'miseq': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv'],
        'nextseq': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv'],
        'novaseq': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv'],
        'pacbio': ['metadata.xml', 'subreadset.xml'],
        'nanopore': ['final_summary.txt'],
        'novaseqxplus': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv'],
        'iseq': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv'],
        'nextseq2k': ['RunInfo.xml', 'RunParameters.xml', 'SampleSheet.csv']
    }

    if sequencer_type not in required_files:
        return False

    # Check for required files
    for file in required_files[sequencer_type]:
        if not os.path.isfile(os.path.join(run_dir, file)):
            return False

    # Check instrument ID in RunInfo.xml
    if sequencer_type in ['miseq', 'nextseq', 'novaseq', 'novaseqxplus', 'iseq', 'nextseq2k']:
        import xml.etree.ElementTree as ET
        try:
            run_info_path = os.path.join(run_dir, 'RunInfo.xml')
            tree = ET.parse(run_info_path)
            root = tree.getroot()
            run_node = root.find('Run')
            if run_node is None:
                return False

            instrument = run_node.findtext('Instrument', '')

            # Check instrument ID prefix
            if sequencer_type == 'miseq' and not instrument.startswith('M'):
                return False
            elif sequencer_type == 'nextseq' and not instrument.startswith('NS'):
                return False
            elif sequencer_type == 'nextseq2k' and not instrument.startswith('NDX'):
                return False
            elif sequencer_type == 'novaseq' and not instrument.startswith('A'):
                return False
            elif sequencer_type == 'novaseqxplus' and not instrument.startswith('LH'):
                return False
            elif sequencer_type == 'iseq' and not instrument.startswith('FSQ'):
                return False

        except Exception:
            return False

    return True
