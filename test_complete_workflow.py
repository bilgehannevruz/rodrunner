#!/usr/bin/env python3
"""
Test script for the complete workflow with iRODS.
"""
import os
import sys
import json
import time
from pprint import pprint

from irods_prefect.models.config import AppConfig, iRODSConfig, SequencerConfig
from irods_prefect.irods.client import iRODSClient
from irods_prefect.parsers.factory import ParserFactory
from irods_prefect.filesystem.find import find_sequencer_runs


def test_complete_workflow(config_file=None):
    """
    Test the complete workflow with iRODS.
    
    Args:
        config_file: Path to the configuration file
    """
    # Load configuration
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        irods_config = iRODSConfig(**config_data.get('irods', {}))
        sequencer_config = SequencerConfig(**config_data.get('sequencer', {}))
    else:
        # Use environment variables or defaults
        irods_config = iRODSConfig(
            host=os.environ.get("IRODS_HOST", "localhost"),
            port=int(os.environ.get("IRODS_PORT", "1247")),
            user=os.environ.get("IRODS_USER", "rods"),
            password=os.environ.get("IRODS_PASSWORD", "rods"),
            zone=os.environ.get("IRODS_ZONE", "tempZone"),
            default_resource=os.environ.get("IRODS_DEFAULT_RESOURCE", "demoResc")
        )
        sequencer_config = SequencerConfig(
            base_dir=os.environ.get("SEQUENCER_BASE_DIR", "data/sequencer"),
            completion_indicator=os.environ.get("SEQUENCER_COMPLETION_INDICATOR", "RTAComplete.txt")
        )
    
    print("Configuration:")
    print(f"  iRODS Host: {irods_config.host}")
    print(f"  iRODS Port: {irods_config.port}")
    print(f"  iRODS User: {irods_config.user}")
    print(f"  iRODS Zone: {irods_config.zone}")
    print(f"  Sequencer Base Dir: {sequencer_config.base_dir}")
    print(f"  Completion Indicator: {sequencer_config.completion_indicator}")
    print()
    
    # Create iRODS client
    client = iRODSClient(irods_config)
    
    try:
        # Test connection
        print("Testing connection to iRODS server...")
        with client.session() as session:
            print("Connection successful!")
            print()
        
        # Find sequencer runs
        print("Finding sequencer runs...")
        miseq_runs = list(find_sequencer_runs(
            root_dir=sequencer_config.base_dir,
            sequencer_type="miseq",
            completion_indicator=sequencer_config.completion_indicator
        ))
        
        novaseq_runs = list(find_sequencer_runs(
            root_dir=sequencer_config.base_dir,
            sequencer_type="novaseq",
            completion_indicator=sequencer_config.completion_indicator
        ))
        
        print(f"Found {len(miseq_runs)} MiSeq runs and {len(novaseq_runs)} NovaSeq runs")
        print()
        
        # Process each run
        all_runs = [(run, "miseq") for run in miseq_runs] + [(run, "novaseq") for run in novaseq_runs]
        
        for run_dir, sequencer_type in all_runs:
            print(f"Processing {sequencer_type} run: {run_dir}")
            print("-" * 80)
            
            # Parse metadata
            metadata = ParserFactory.parse_sequencer_run(run_dir)
            
            # Get run ID
            run_id = metadata.get('run_info', {}).get('run_id', '')
            if not run_id:
                print(f"Failed to get run ID from metadata")
                continue
            
            # Get iRODS destination
            if sequencer_type == 'miseq':
                # Extract components from run ID
                # Format: YYMMDD_M00001_0001_000000000-A1B2C
                parts = run_id.split('_')
                date = parts[0] if len(parts) > 0 else ''
                instrument = parts[1] if len(parts) > 1 else ''
                run_number = parts[2] if len(parts) > 2 else ''
                flowcell = parts[3] if len(parts) > 3 else ''
                
                # Construct path
                irods_destination = f"/{irods_config.zone}/home/{irods_config.user}/sequencing/miseq/{date}_{instrument}_{run_number}_{flowcell}"
            elif sequencer_type == 'novaseq':
                # Extract components from run ID
                # Format: YYMMDD_A00001_0001_AHGV7DRXX
                parts = run_id.split('_')
                date = parts[0] if len(parts) > 0 else ''
                instrument = parts[1] if len(parts) > 1 else ''
                run_number = parts[2] if len(parts) > 2 else ''
                flowcell = parts[3] if len(parts) > 3 else ''
                
                # Construct path
                irods_destination = f"/{irods_config.zone}/home/{irods_config.user}/sequencing/novaseq/{date}_{instrument}_{run_number}_{flowcell}"
            else:
                irods_destination = f"/{irods_config.zone}/home/{irods_config.user}/sequencing/{sequencer_type}/{run_id}"
            
            print(f"Run ID: {run_id}")
            print(f"iRODS destination: {irods_destination}")
            
            # Create collection
            print(f"Creating collection: {irods_destination}")
            client.create_collection(irods_destination)
            
            # Add metadata
            print("Adding metadata...")
            metadata_to_add = {
                'sequencer_type': sequencer_type,
                'run_id': run_id,
                'flowcell': metadata.get('run_info', {}).get('flowcell', ''),
                'instrument': metadata.get('run_info', {}).get('instrument', ''),
                'date': metadata.get('run_info', {}).get('date', ''),
                'projects': ','.join(metadata.get('projects', [])),
                'status': 'ingested'
            }
            
            with client.session() as session:
                coll = session.collections.get(irods_destination)
                for key, value in metadata_to_add.items():
                    coll.metadata.add(key, str(value))
            
            print("Metadata added successfully:")
            pprint(metadata_to_add)
            
            # Upload a sample file
            sample_file_path = os.path.join(run_dir, "RunInfo.xml")
            sample_file_name = os.path.basename(sample_file_path)
            irods_file_path = f"{irods_destination}/{sample_file_name}"
            
            print(f"Uploading sample file: {sample_file_path} to {irods_file_path}")
            client.upload_file(sample_file_path, irods_file_path)
            
            print(f"Processing completed for {run_id}")
            print()
        
        print("Complete workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Get configuration file from command line argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    # Test complete workflow
    success = test_complete_workflow(config_file)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
