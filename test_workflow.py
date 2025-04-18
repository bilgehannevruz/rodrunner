#!/usr/bin/env python3
"""
Test script for simulating the workflow without iRODS.
"""
import os
import json
from pprint import pprint

from irods_prefect.parsers.factory import ParserFactory
from irods_prefect.filesystem.find import find_sequencer_runs


def simulate_ingest_workflow(run_dir, sequencer_type):
    """
    Simulate the ingest workflow for a sequencer run.
    
    Args:
        run_dir: Path to the sequencer run directory
        sequencer_type: Type of sequencer
    """
    print(f"Simulating ingest workflow for {sequencer_type} run: {run_dir}")
    print("-" * 80)
    
    # Parse metadata
    metadata = ParserFactory.parse_sequencer_run(run_dir)
    
    # Get run ID
    run_id = metadata.get('run_info', {}).get('run_id', '')
    if not run_id:
        print(f"Failed to get run ID from metadata")
        return
    
    # Get iRODS destination (simulated)
    if sequencer_type == 'miseq':
        # Extract components from run ID
        # Format: YYMMDD_M00001_0001_000000000-A1B2C
        parts = run_id.split('_')
        date = parts[0] if len(parts) > 0 else ''
        instrument = parts[1] if len(parts) > 1 else ''
        run_number = parts[2] if len(parts) > 2 else ''
        flowcell = parts[3] if len(parts) > 3 else ''
        
        # Construct path
        irods_destination = f"/sequencing/miseq/{date}_{instrument}_{run_number}_{flowcell}"
    elif sequencer_type == 'novaseq':
        # Extract components from run ID
        # Format: YYMMDD_A00001_0001_AHGV7DRXX
        parts = run_id.split('_')
        date = parts[0] if len(parts) > 0 else ''
        instrument = parts[1] if len(parts) > 1 else ''
        run_number = parts[2] if len(parts) > 2 else ''
        flowcell = parts[3] if len(parts) > 3 else ''
        
        # Construct path
        irods_destination = f"/sequencing/novaseq/{date}_{instrument}_{run_number}_{flowcell}"
    else:
        irods_destination = f"/sequencing/{sequencer_type}/{run_id}"
    
    print(f"Run ID: {run_id}")
    print(f"iRODS destination: {irods_destination}")
    
    # Simulate upload to iRODS
    print(f"Simulating upload of {run_dir} to {irods_destination}")
    
    # Simulate adding metadata
    print("Simulating adding metadata:")
    metadata_to_add = {
        'sequencer_type': sequencer_type,
        'run_id': run_id,
        'flowcell': metadata.get('run_info', {}).get('flowcell', ''),
        'instrument': metadata.get('run_info', {}).get('instrument', ''),
        'date': metadata.get('run_info', {}).get('date', ''),
        'projects': ','.join(metadata.get('projects', [])),
        'status': 'ingested'
    }
    pprint(metadata_to_add)
    
    print(f"Ingest workflow simulation completed for {run_id}")
    print()


def main():
    """Main function."""
    # Find MiSeq runs
    miseq_runs = list(find_sequencer_runs(
        root_dir="data/sequencer",
        sequencer_type="miseq",
        completion_indicator="RTAComplete.txt"
    ))
    
    # Find NovaSeq runs
    novaseq_runs = list(find_sequencer_runs(
        root_dir="data/sequencer",
        sequencer_type="novaseq",
        completion_indicator="RTAComplete.txt"
    ))
    
    # Simulate ingest workflow for each run
    for run_dir in miseq_runs:
        simulate_ingest_workflow(run_dir, "miseq")
    
    for run_dir in novaseq_runs:
        simulate_ingest_workflow(run_dir, "novaseq")


if __name__ == "__main__":
    main()
