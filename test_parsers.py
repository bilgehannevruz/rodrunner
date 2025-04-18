#!/usr/bin/env python3
"""
Test script for parsers.
"""
import os
import json
from pprint import pprint

from irods_prefect.parsers.factory import ParserFactory


def test_miseq_run():
    """Test parsing a MiSeq run."""
    run_dir = "data/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"
    
    print(f"Testing MiSeq run: {run_dir}")
    print("-" * 80)
    
    metadata = ParserFactory.parse_sequencer_run(run_dir)
    
    print("Metadata:")
    pprint(metadata)
    print()
    
    # Check sequencer type
    sequencer_type = metadata.get('sequencer_type')
    print(f"Sequencer type: {sequencer_type}")
    assert sequencer_type == 'miseq', f"Expected 'miseq', got '{sequencer_type}'"
    
    # Check projects
    projects = metadata.get('projects', [])
    print(f"Projects: {projects}")
    assert 'Project1' in projects, "Expected 'Project1' in projects"
    assert 'Project2' in projects, "Expected 'Project2' in projects"
    
    print("MiSeq test passed!")
    print()


def test_novaseq_run():
    """Test parsing a NovaSeq run."""
    run_dir = "data/sequencer/novaseq/220102_A00001_0001_AHGV7DRXX"
    
    print(f"Testing NovaSeq run: {run_dir}")
    print("-" * 80)
    
    metadata = ParserFactory.parse_sequencer_run(run_dir)
    
    print("Metadata:")
    pprint(metadata)
    print()
    
    # Check sequencer type
    sequencer_type = metadata.get('sequencer_type')
    print(f"Sequencer type: {sequencer_type}")
    assert sequencer_type == 'novaseq', f"Expected 'novaseq', got '{sequencer_type}'"
    
    # Check projects
    projects = metadata.get('projects', [])
    print(f"Projects: {projects}")
    assert 'Project3' in projects, "Expected 'Project3' in projects"
    assert 'Project4' in projects, "Expected 'Project4' in projects"
    
    print("NovaSeq test passed!")
    print()


if __name__ == "__main__":
    test_miseq_run()
    test_novaseq_run()
