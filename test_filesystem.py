#!/usr/bin/env python3
"""
Test script for filesystem module.
"""
import os
from pprint import pprint

from irods_prefect.filesystem.find import find_files, find_sequencer_runs


def test_find_files():
    """Test find_files function."""
    print("Testing find_files function")
    print("-" * 80)
    
    # Find all XML files
    xml_files = list(find_files(
        root_dir="data",
        name_pattern="*.xml",
        file_type='f'
    ))
    
    print(f"Found {len(xml_files)} XML files:")
    for file in xml_files:
        print(f"  {file}")
    print()
    
    # Find all directories with a minimum depth
    dirs = list(find_files(
        root_dir="data",
        min_depth=2,
        file_type='d'
    ))
    
    print(f"Found {len(dirs)} directories with min_depth=2:")
    for dir in dirs:
        print(f"  {dir}")
    print()
    
    # Find all files with a custom filter
    def is_large_file(path):
        return os.path.getsize(path) > 1000
    
    large_files = list(find_files(
        root_dir="data",
        file_type='f',
        custom_filter=is_large_file
    ))
    
    print(f"Found {len(large_files)} large files:")
    for file in large_files:
        print(f"  {file} ({os.path.getsize(file)} bytes)")
    print()
    
    print("find_files test completed!")
    print()


def test_find_sequencer_runs():
    """Test find_sequencer_runs function."""
    print("Testing find_sequencer_runs function")
    print("-" * 80)
    
    # Find MiSeq runs
    miseq_runs = list(find_sequencer_runs(
        root_dir="data/sequencer",
        sequencer_type="miseq",
        completion_indicator="RTAComplete.txt"
    ))
    
    print(f"Found {len(miseq_runs)} MiSeq runs:")
    for run in miseq_runs:
        print(f"  {run}")
    print()
    
    # Find NovaSeq runs
    novaseq_runs = list(find_sequencer_runs(
        root_dir="data/sequencer",
        sequencer_type="novaseq",
        completion_indicator="RTAComplete.txt"
    ))
    
    print(f"Found {len(novaseq_runs)} NovaSeq runs:")
    for run in novaseq_runs:
        print(f"  {run}")
    print()
    
    print("find_sequencer_runs test completed!")
    print()


if __name__ == "__main__":
    test_find_files()
    test_find_sequencer_runs()
